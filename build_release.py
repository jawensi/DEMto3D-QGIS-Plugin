"""Build and test the QGIS 3 release using the QGIS Python interpreter."""

import argparse
import ast
import configparser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent
PACKAGE = "DEMto3D"


def check_quality(stage):
    """Check shipped files, including every Bandit severity level."""
    python_files = sorted(str(path) for path in stage.rglob("*.py"))
    subprocess.run(
        [sys.executable, "-m", "flake8", "--isolated", "--jobs=1",
         "--max-line-length=120", *python_files],
        check=True,
    )
    print(f"Flake8: 0 issues in {len(python_files)} packaged Python files", flush=True)
    bandit = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", "-r", str(stage), "-f", "json"],
        capture_output=True, text=True,
    )
    report = json.loads(bandit.stdout)
    findings = report.get("results", [])
    print(f"Bandit (all severities): {len(findings)} issues", flush=True)
    if bandit.returncode or findings or report.get("errors"):
        for finding in findings:
            print(f"{finding['filename']}:{finding['line_number']}: "
                  f"{finding['test_id']} {finding['issue_text']}")
        raise RuntimeError("Bandit security checks failed")
    secrets = subprocess.run(
        [sys.executable, "-m", "detect_secrets", "scan", "--all-files", str(stage)],
        capture_output=True, text=True, check=True,
    )
    secret_findings = json.loads(secrets.stdout)["results"]
    count = sum(len(items) for items in secret_findings.values())
    print(f"Secrets detection: {count} findings", flush=True)
    if count:
        raise RuntimeError("Potential secrets detected in release files")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-quality", action="store_true",
                        help="Require Flake8, full Bandit and detect-secrets checks")
    args = parser.parse_args()
    metadata = configparser.ConfigParser(interpolation=None)
    metadata.read(ROOT / "metadata.txt", encoding="utf-8")
    general = metadata["general"]
    for key in ("name", "version", "qgisMinimumVersion", "qgisMaximumVersion",
                "description", "about", "author", "email", "license",
                "homepage", "repository", "tracker", "icon"):
        if not general.get(key, "").strip():
            raise ValueError(f"Missing metadata field: {key}")
    version = general["version"]
    if not version or any(c not in "0123456789." for c in version):
        raise ValueError("Release version must contain only digits and dots")

    from qgis.core import Qgis
    from qgis.PyQt.QtCore import QT_VERSION_STR

    minimum = [int(part) for part in general["qgisMinimumVersion"].split(".")]
    minimum_number = minimum[0] * 10000 + minimum[1] * 100
    if not minimum_number <= Qgis.QGIS_VERSION_INT < 40000 or not QT_VERSION_STR.startswith("5."):
        raise RuntimeError("Build with a supported QGIS 3 / Qt 5 interpreter")

    with tempfile.TemporaryDirectory(prefix="demto3d-release-") as directory:
        stage = Path(directory) / PACKAGE
        stage.mkdir()
        for name in ("__init__.py", "DEMto3D.py", "metadata.txt", "LICENSE", "README.md"):
            shutil.copy2(ROOT / name, stage / name)
        for name, suffixes in (
            ("DEMto3D_Dialog", {".py", ".ui"}),
            ("model_builder", {".py"}),
            ("icons", {".png", ".svg"}),
            ("i18n", {".ts", ".qm"}),
        ):
            for source in sorted((ROOT / name).iterdir()):
                if source.is_file() and source.suffix in suffixes:
                    target = stage / name / source.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)

        # Regenerate embedded icons instead of using an ignored local resources.py.
        subprocess.run(
            [sys.executable, "-m", "PyQt5.pyrcc_main", "-o",
             str(stage / "resources.py"), "resources.qrc"],
            cwd=ROOT, check=True,
        )
        # pyrcc5 separates module-level definitions with only one blank line.
        # Normalize its output so the shipped file passes the repository lint.
        resource_path = stage / "resources.py"
        resource_code = resource_path.read_text(encoding="utf-8")
        for declaration in ("def qInitResources():", "def qCleanupResources():",
                            "qInitResources()"):
            resource_code = resource_code.replace(
                f"\n\n{declaration}", f"\n\n\n{declaration}"
            )
        resource_path.write_text(resource_code, encoding="utf-8")
        shutil.copy2(ROOT / "resources.qrc", stage / "resources.qrc")
        for source in stage.rglob("*.py"):
            ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        if not (stage / general["icon"]).is_file():
            raise ValueError("Plugin icon is missing")

        if args.check_quality:
            check_quality(stage)

        # Run the existing integration tests against the staged release files.
        test_dir = stage / "tests"
        test_dir.mkdir()
        shutil.copy2(ROOT / "tests" / "test_qgis3_backport.py", test_dir)
        subprocess.run([sys.executable, str(test_dir / "test_qgis3_backport.py")],
                       cwd=stage, check=True)

        output_dir = ROOT / "zip_build"
        output_dir.mkdir(exist_ok=True)
        output = output_dir / f"{PACKAGE}-{version}.zip"
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(stage.rglob("*")):
                relative = source.relative_to(stage)
                if source.is_file() and not {"tests", "__pycache__"}.intersection(relative.parts):
                    archive.write(source, f"{PACKAGE}/{relative.as_posix()}")
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity check failed")
            for required in ("metadata.txt", "__init__.py", "LICENSE", "resources.py",
                             "i18n/DEMto3D_es.qm", "i18n/DEMto3D_fr.qm"):
                archive.getinfo(f"{PACKAGE}/{required}")
        if output.stat().st_size > 25 * 1024 * 1024:
            raise ValueError("Package exceeds the QGIS repository size limit")
        print(f"Validated with QGIS {Qgis.QGIS_VERSION}: {output}", flush=True)
        print(f"Package size: {output.stat().st_size:,} bytes", flush=True)


if __name__ == "__main__":
    main()
