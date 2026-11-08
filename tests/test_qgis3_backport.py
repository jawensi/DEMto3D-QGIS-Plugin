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

    def test_legacy_binary_export_closes_file_and_propagates_mesh_errors(self):
        target = self.directory / "invalid.stl"
        builder = STL(self.params, str(target), self.matrix)
        stream = target.open("wb")
        with patch("builtins.open", return_value=stream), patch.object(
            builder, "face_dem_vector", side_effect=ValueError("invalid mesh")
        ):
            with self.assertRaisesRegex(ValueError, "invalid mesh"):
                builder.write_binary(str(target), self.matrix)
        self.assertTrue(stream.closed)

    def test_legacy_binary_export_propagates_file_open_errors(self):
        builder = STL(self.params, str(self.directory), self.matrix)
        with patch("builtins.open", side_effect=OSError("cannot write STL")):
            with self.assertRaisesRegex(OSError, "cannot write STL"):
                builder.write_binary(str(self.directory), self.matrix)

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
                self.assertFalse(QPixmap(":/plugins/DEMto3D/icons/upRight.svg").isNull())
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


class RuntimeGuardTests(unittest.TestCase):
    def setUp(self):
        self.plugin_module = importlib.import_module(PACKAGE + ".DEMto3D")
        self.dialog_module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.DEMto3D_dialog")
        self.plugin = self.plugin_module.DEMto3D(types.SimpleNamespace())

    def test_optional_locale_signal_uses_application_instance(self):
        for signal in (None, Mock()):
            application = types.SimpleNamespace(localeChanged=signal)
            with patch.object(self.plugin_module, "QgsApplication") as qgis_app:
                qgis_app.instance.return_value = application
                with patch.object(self.plugin_module.DEMto3D, "_install_translator"):
                    plugin = self.plugin_module.DEMto3D(types.SimpleNamespace())
            if signal is not None:
                signal.connect.assert_called_once_with(plugin._on_locale_changed)

    def test_missing_project_or_layer_tree_disables_action_and_rejects_gui(self):
        for project in (None, types.SimpleNamespace(layerTreeRoot=lambda: None)):
            with patch.object(self.plugin_module, "QgsProject") as project_class:
                project_class.instance.return_value = project
                self.assertFalse(self.plugin._has_visible_raster())
                with self.assertRaises(RuntimeError):
                    self.plugin.initGui()

    def test_gui_can_initialize_without_optional_visibility_signal(self):
        root = types.SimpleNamespace(addedChildren=Mock(), removedChildren=Mock())
        project = types.SimpleNamespace(
            layerTreeRoot=lambda: root, mapLayers=lambda: {},
            layersAdded=Mock(), layersRemoved=Mock(),
        )
        self.plugin.iface = Mock()
        self.plugin.iface.mainWindow.return_value = None
        self.plugin.iface.mapCanvas.return_value = None
        with patch.object(self.plugin_module, "QgsProject") as project_class, patch.object(
            self.plugin_module, "QTimer"
        ):
            project_class.instance.return_value = project
            self.plugin.initGui()
            self.assertFalse(self.plugin.action.isEnabled())
            self.plugin.unload()

    def test_deleted_canvas_overlays_are_logged_and_references_cleared(self):
        scene = Mock()
        scene.removeItem.side_effect = RuntimeError("wrapped C++ object has been deleted")
        self.plugin.iface = types.SimpleNamespace(
            mapCanvas=lambda: types.SimpleNamespace(scene=lambda: scene)
        )
        dialog = types.SimpleNamespace(extent=object(), divisions=object())
        with self.assertLogs(self.plugin_module.LOGGER, level="DEBUG") as logs:
            self.plugin._cleanup_canvas_items(dialog)
        self.assertEqual(len(logs.records), 2)
        self.assertIsNone(dialog.extent)
        self.assertIsNone(dialog.divisions)

    def test_unexpected_canvas_cleanup_errors_are_not_swallowed(self):
        scene = Mock()
        scene.removeItem.side_effect = TypeError("invalid overlay")
        self.plugin.iface = types.SimpleNamespace(
            mapCanvas=lambda: types.SimpleNamespace(scene=lambda: scene)
        )
        dialog = types.SimpleNamespace(extent=object(), divisions=None)
        with self.assertRaisesRegex(TypeError, "invalid overlay"):
            self.plugin._cleanup_canvas_items(dialog)
        self.assertIsNone(dialog.extent)

    def test_extent_selection_without_optional_pan_action_or_message_bar(self):
        dialog = types.SimpleNamespace(
            iface=types.SimpleNamespace(actionPan=lambda: None, messageBar=lambda: None),
            rect_map_tool=Mock(), extent=None, divisions=None, canvas=Mock(),
            get_custom_extent_cb=Mock(),
        )
        self.dialog_module.DEMto3DDialog.reject_func(dialog)
        dialog.rect_map_tool.reset.assert_called_once()
        dialog.rect_map_tool.deactivate.assert_called_once()
        with patch.object(self.dialog_module, "RectangleMapTool") as tool_class:
            self.dialog_module.DEMto3DDialog.custom_extent(dialog)
        dialog.canvas.setMapTool.assert_called_once_with(tool_class.return_value)

    def test_unavailable_raster_provider_does_not_produce_export_parameters(self):
        from qgis.core import Qgis
        dialog = types.SimpleNamespace(
            units=Qgis.DistanceUnit.Meters,
            layer=types.SimpleNamespace(dataProvider=lambda: None),
        )
        self.assertIsNone(self.dialog_module.DEMto3DDialog.get_parameters(dialog))

    def test_unavailable_vector_provider_raises_and_restores_cursor(self):
        from qgis.core import QgsCoordinateReferenceSystem
        from qgis.PyQt.QtWidgets import QApplication
        dialog = types.SimpleNamespace(
            rect_Params=dict(center=[0, 0], width=10, height=10, rotation=0),
            map_crs=QgsCoordinateReferenceSystem("EPSG:3857"),
        )
        cursor_before = QApplication.overrideCursor()
        with patch.object(self.dialog_module, "QgsVectorLayer") as layer_class:
            layer_class.return_value.dataProvider.return_value = None
            with self.assertRaisesRegex(RuntimeError, "vector layer provider"):
                self.dialog_module.DEMto3DDialog.get_z_max_z_min(dialog)
        self.assertIs(QApplication.overrideCursor(), cursor_before)

    def test_rectangle_tool_ignores_missing_events_and_accepts_valid_press(self):
        from qgis.core import QgsPointXY
        module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.rectangle_map_tool")
        point = QgsPointXY(1, 2)
        tool = types.SimpleNamespace(
            startPoint=None, endPoint=None, isEmittingPoint=True,
            toMapCoordinates=Mock(return_value=point), showRect=Mock(),
        )
        module.RectangleMapTool.canvasPressEvent(tool, None)
        module.RectangleMapTool.canvasMoveEvent(tool, None)
        tool.toMapCoordinates.assert_not_called()
        self.assertIsNone(tool.startPoint)
        self.assertIsNone(tool.endPoint)
        event = types.SimpleNamespace(pos=lambda: object())
        module.RectangleMapTool.canvasPressEvent(tool, event)
        self.assertEqual(tool.startPoint, point)
        self.assertTrue(tool.isEmittingPoint)
        tool.showRect.assert_called_once_with(point, point)


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    unittest.main(verbosity=2)
