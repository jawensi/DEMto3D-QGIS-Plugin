"""Run with the QGIS 3 Python interpreter: python tests/test_qgis3_backport.py."""

import hashlib
import importlib
import importlib.util
import os
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QDialog

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "demto3d_backport_test"
spec = importlib.util.spec_from_file_location(
    PACKAGE, ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
)
package = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = package
spec.loader.exec_module(package)
builder_module = importlib.import_module(PACKAGE + ".model_builder.STL_Builder")
STL = builder_module.STL


def read_binary(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + count * 50
    return np.array([
        struct.unpack_from("<12fH", data, 84 + i * 50)[:12]
        for i in range(count)
    ])


def read_ascii(path):
    lines = path.read_text(encoding="ascii").splitlines()
    assert lines[0] == "solid model" and lines[-1] == "endsolid model"
    assert (len(lines) - 2) % 7 == 0
    faces = []
    for i in range(1, len(lines) - 1, 7):
        assert lines[i + 1].strip() == "outer loop"
        assert lines[i + 5].strip() == "endloop"
        assert lines[i + 6].strip() == "endfacet"
        values = lines[i].split()[2:]
        for vertex in lines[i + 2:i + 5]:
            assert vertex.split()[0] == "vertex"
            values += vertex.split()[1:]
        faces.append([float(v) for v in values])
    return np.array(faces)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.matrix = np.array([
            [[x, y, 3 + x * 0.13 + y * 0.07] for x in (0, 10, 20)]
            for y in (20, 10, 0)
        ], dtype=float)
        self.params = dict(
            divideCols=1, divideRow=1, width=20, height=20,
            spacing_mm=10, has_borders=True, borders=0,
        )

    def test_ascii_matches_binary_for_all_side_options_and_tiles(self):
        for sides, border in ((False, 0), (True, 0), (True, 2)):
            for divisions in (1, 2):
                with self.subTest(sides=sides, border=border, divisions=divisions):
                    params = dict(self.params, has_borders=sides, borders=border,
                                  divideRow=divisions, divideCols=divisions)
                    files = {}
                    for output_format in ("binary", "ascii"):
                        target = self.directory / (output_format + ".v1.stl")
                        builder = STL(dict(params, stl_format=output_format),
                                      str(target), self.matrix)
                        builder.run()
                        files[output_format] = [Path(p) for p in builder.output_files]
                        self.assertEqual(len(builder.output_files), divisions ** 2)
                    for binary, ascii_file in zip(files["binary"], files["ascii"]):
                        actual = read_ascii(ascii_file)
                        np.testing.assert_allclose(actual, read_binary(binary), atol=1e-6)
                        # Terrain elevation must survive ASCII export.
                        self.assertGreater(actual[:, (5, 8, 11)].max(), 3)

    def test_binary_default_remains_byte_identical_to_develop(self):
        # SHA-256 fixtures from develop commit 6a37e885, using this test's
        # mesh and parameters. Protects existing binary triangulation and bytes.
        fixtures = (
            (False, 0, "f178e04484e018727ac9669c7d6f51ee63ba8c4271976a8004e381ee2ad71482"),
            (True, 0, "e3fbd50108fa28282ed9b6e9a0c18637d39ed7030efc8a934b10aa64d85ab374"),
            (True, 2, "9fa5ec820ebd65068609c8e77c3f0d7e5bd391a5e88fe307aa4ad566378b564a"),
        )
        for sides, border, digest in fixtures:
            with self.subTest(sides=sides, border=border):
                params = dict(self.params, has_borders=sides, borders=border)
                target = self.directory / "default.stl"
                STL(params, str(target), self.matrix).run()
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), digest)

    def test_cancellation_stops_before_the_next_tile(self):
        for output_format in ("ascii", "binary"):
            with self.subTest(output_format=output_format):
                params = dict(self.params, stl_format=output_format,
                              divideRow=2, divideCols=2)
                builder = STL(params, str(self.directory / "cancel.stl"), self.matrix)

                def cancel():
                    builder.quit = True

                builder.updateProgress.connect(cancel)
                builder.run()
                self.assertTrue(builder.quit)
                self.assertEqual(len(builder.output_files), 1)

    def test_cancelled_split_export_removes_generated_parts(self):
        module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.Export_dialog")
        from qgis.PyQt.QtWidgets import QMessageBox
        files = [self.directory / "part_00.stl", self.directory / "part_01.stl"]
        for path in files:
            path.write_bytes(b"partial output")
        exporter = types.SimpleNamespace(
            start_time=0,
            prepareUi=Mock(),
            mainDlg=types.SimpleNamespace(ui=Mock(), tr=lambda text: text),
            STLBuilder=types.SimpleNamespace(quit=True, output_files=[str(p) for p in files]),
        )
        with patch.object(QMessageBox, "information"):
            module.Export.finish_model(exporter)
        self.assertTrue(all(not p.exists() for p in files))


class Qgis3UiTests(unittest.TestCase):
    def test_form_resources_and_translations(self):
        from qgis.PyQt.QtCore import QT_VERSION_STR
        self.assertTrue(QT_VERSION_STR.startswith("5."))
        importlib.import_module(PACKAGE + ".resources")
        form = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.DEMto3D_dialog_base")
        for locale, title in (("es", "Formato de salida"), ("fr", "Format de sortie")):
            translator = QTranslator()
            self.assertTrue(translator.load(str(ROOT / "i18n" / ("DEMto3D_" + locale + ".qm"))))
            QCoreApplication.installTranslator(translator)
            try:
                dialog = QDialog()
                ui = form.Ui_DEMto3DDialogBase()
                ui.setupUi(dialog)
                self.assertTrue(ui.radioButton_binary.isChecked())
                ui.radioButton_ascii.setChecked(True)
                self.assertFalse(ui.radioButton_binary.isChecked())
                self.assertEqual(ui.groupBox_2.title(), title)
                self.assertIn("(m)", ui.label_17.text())
                self.assertFalse(QPixmap(":/plugins/DEMto3D/icons/upRight.png").isNull())
                self.assertFalse(dialog.windowIcon().isNull())
                dialog.close()
            finally:
                QCoreApplication.removeTranslator(translator)

    def test_dialog_settings_roundtrip_and_legacy_binary_default(self):
        from osgeo import gdal, osr
        from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
        module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.DEMto3D_dialog")
        with tempfile.TemporaryDirectory() as directory:
            raster_path = str(Path(directory) / "dem.tif")
            gdal.UseExceptions()
            dataset = gdal.GetDriverByName("GTiff").Create(raster_path, 4, 4, 1, gdal.GDT_Float32)
            dataset.SetGeoTransform((0, 10, 0, 40, 0, -10))
            crs = osr.SpatialReference()
            crs.ImportFromEPSG(3857)
            dataset.SetProjection(crs.ExportToWkt())
            dataset.GetRasterBand(1).WriteArray(np.arange(16, dtype=np.float32).reshape(4, 4) + 100)
            dataset = None
            raster = QgsRasterLayer(raster_path, "DEM")
            self.assertTrue(raster.isValid())
            QgsProject.instance().addMapLayer(raster)
            canvas = QgsMapCanvas()
            canvas.setDestinationCrs(raster.crs())
            canvas.setLayers([raster])
            iface = types.SimpleNamespace(mapCanvas=lambda: canvas, mainWindow=lambda: None)
            dialog = module.DEMto3DDialog(iface)
            try:
                dialog.full_extent()
                dialog.ui.SpacingLineEdit.setText("10")
                dialog.ui.WidthLineEdit.setText("40")
                dialog.upload_size_from_width()
                dialog.ui.BaseHeightLineEdit.setText("100")
                dialog.ui.radioButton_ascii.setChecked(True)
                self.assertEqual(dialog.get_parameters()["stl_format"], "ascii")
                params = dialog.get_parameters()
                model_module = importlib.import_module(PACKAGE + ".model_builder.Model_Builder")
                model = model_module.Model(params)
                model.run()
                mesh = model.get_model()
                self.assertEqual(mesh.shape[2], 3)
                self.assertTrue(np.isfinite(mesh).all())
                stl_path = Path(directory) / "terrain.stl"
                STL(params, str(stl_path), mesh).run()
                self.assertGreater(len(read_ascii(stl_path)), 0)
                settings = str(Path(directory) / "settings.txt")
                with patch.object(QFileDialog, "getSaveFileName", return_value=(settings, "")), patch.object(QMessageBox, "information"):
                    dialog.export_params()
                dialog.ui.radioButton_binary.setChecked(True)
                with patch.object(QFileDialog, "getOpenFileName", return_value=(settings, "")):
                    dialog.import_params()
                self.assertTrue(dialog.ui.radioButton_ascii.isChecked())
                import json
                data = json.loads(Path(settings).read_text())
                del data["stl_format"]
                Path(settings).write_text(json.dumps(data))
                with patch.object(QFileDialog, "getOpenFileName", return_value=(settings, "")):
                    dialog.import_params()
                self.assertTrue(dialog.ui.radioButton_binary.isChecked())
            finally:
                for attr in ("extent", "divisions"):
                    item = getattr(dialog, attr, None)
                    if item is not None:
                        canvas.scene().removeItem(item)
                dialog.close()
                QgsProject.instance().clear()


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    unittest.main(verbosity=2)
