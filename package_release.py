"""Build the QGIS upload ZIP: python package_release.py."""

import ast
import configparser
import hashlib
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parent
PACKAGE = "DEMto3D"  # Preserve the package name registered at plugins.qgis.org.


def main():
    metadata = configparser.ConfigParser(interpolation=None)
    metadata.read(ROOT / "metadata.txt", encoding="utf-8")
    general = metadata["general"]
    for key in (
        "name", "version", "qgisMinimumVersion", "description", "about",
        "author", "email", "homepage", "repository", "tracker", "icon",
    ):
        if not general.get(key, "").strip():
            raise ValueError(f"Missing metadata: {key}")
    version = general["version"]
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,2}", version):
        raise ValueError(f"Invalid release version: {version}")

    files = [ROOT / name for name in (
        "__init__.py", "DEMto3D.py", "metadata.txt", "LICENSE", "README.md",
        "resources.py", "resources.qrc",
    )]
    for folder, extensions in (
        ("DEMto3D_Dialog", {".py", ".ui"}),
        ("model_builder", {".py"}),
        ("i18n", {".qm", ".ts"}),
        ("icons", {".png", ".svg"}),
    ):
        files.extend(p for p in (ROOT / folder).rglob("*")
                     if p.is_file() and p.suffix in extensions
                     and "__pycache__" not in p.parts)
    if ROOT / general["icon"] not in files:
        raise ValueError("The metadata icon is missing from the package")
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))

    output = ROOT / "zip_build" / f"{PACKAGE}-{version}.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            name = f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}"
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
    if output.stat().st_size > 25 * 1024 * 1024:
        raise ValueError("Package exceeds the QGIS repository size limit")
    print(f"Package: {output}")
    print(f"Files: {len(files)}; bytes: {output.stat().st_size}")
    print(f"SHA256: {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
