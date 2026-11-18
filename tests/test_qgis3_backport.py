"""Run with the QGIS 3 Python interpreter: python tests/test_qgis3_backport.py."""

import hashlib
from collections import Counter
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

    @staticmethod
    def build_mesh(width, height, spacing):
        from osgeo import gdal

        gdal.UseExceptions()
        module = importlib.import_module(PACKAGE + ".model_builder.Model_Builder")
        dataset = gdal.GetDriverByName("MEM").Create("", 8, 8, 1, gdal.GDT_Float32)
        dataset.SetGeoTransform((0, 1000, 0, 5000, 0, -1000))
        dataset.GetRasterBand(1).Fill(3)
        model = module.Model(dict(
            baseModel=2, crs_map=None, crs_layer=None,
            roi_rect_Param=dict(rotation=0, width=width),
        ))
        return model.matrix_dem_builder_interpolation(
            dataset, height, width, 1000, 1, 1, spacing,
            width, 0, 0, 0, 1, True,
        )

    @staticmethod
    def mesh_volume(triangles):
        return np.einsum(
            "ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])
        ).sum() / 6

    def assert_exact_tiles(self, matrix, width, height, columns, rows, output_format):
        params = dict(
            width=width, height=height, spacing_mm=10,
            divideCols=columns, divideRow=rows, has_borders=True, borders=0,
            stl_format=output_format,
        )
        builder = STL(params, str(self.directory / "tiles.stl"), matrix)
        builder.run()
        reader = read_ascii if output_format == "ascii" else read_binary
        triangles = [
            reader(Path(path))[:, 3:12].reshape((-1, 3, 3))
            for path in builder.output_files
        ]
        self.assertEqual(len(triangles), columns * rows)
        points = [faces.reshape((-1, 3)) for faces in triangles]
        lower = [part.min(axis=0) for part in points]
        upper = [part.max(axis=0) for part in points]
        tolerance = max(width, height) * np.finfo(np.float32).eps * 2
        if output_format == "ascii":
            tolerance = 1e-11
        for i in range(rows):
            for j in range(columns):
                index = i * columns + j
                np.testing.assert_allclose(
                    lower[index][:2], [width * j / columns, height * (rows - i - 1) / rows],
                    rtol=0, atol=tolerance,
                )
                np.testing.assert_allclose(
                    upper[index][:2], [width * (j + 1) / columns, height * (rows - i) / rows],
                    rtol=0, atol=tolerance,
                )
                # Every triangle edge of the closed solid must have exactly two faces.
                edges = Counter(
                    tuple(sorted((tuple(face[a]), tuple(face[b]))))
                    for face in triangles[index] for a, b in ((0, 1), (1, 2), (2, 0))
                )
                invalid = [(edge, count) for edge, count in edges.items() if count != 2]
                self.assertFalse(invalid, invalid[:3])
                for neighbor, axis, limit in (
                    (index + 1, 0, upper[index][0]),
                    (index + columns, 1, lower[index][1]),
                ):
                    if (axis == 0 and j + 1 == columns) or (axis == 1 and i + 1 == rows):
                        continue
                    first = points[index][points[index][:, axis] == limit]
                    second = points[neighbor][points[neighbor][:, axis] == limit]
                    np.testing.assert_array_equal(
                        np.unique(first, axis=0), np.unique(second, axis=0)
                    )

        # Cutting must conserve the original triangulated terrain's volume.
        source = self.directory / "whole.stl"
        STL(dict(params, divideCols=1, divideRow=1), str(source), matrix).run()
        expected_volume = self.mesh_volume(reader(source)[:, 3:12].reshape((-1, 3, 3)))
        actual_volume = sum(self.mesh_volume(faces) for faces in triangles)
        self.assertAlmostEqual(
            actual_volume, expected_volume,
            delta=max(abs(expected_volume) * (5e-7 if output_format == "binary" else 1e-12), 1e-9),
        )
        return np.concatenate(points)

    def test_exact_divisions_cross_coarse_cells(self):
        matrix = self.matrix.copy()
        matrix[:, :, 2] = [[3, 8, 5], [11, 4, 13], [7, 16, 6]]
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 20, 20, 3, 4, output_format)

    def test_exact_divisions_preserve_nonplanar_cell_triangles(self):
        matrix = np.array([[[0, 1, 8], [1, 1, 14]], [[0, 0, 2], [1, 0, 4]]], dtype=float)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                points = self.assert_exact_tiles(matrix, 1, 1, 3, 4, output_format)
                for x, y, z in ((1 / 3, 1 / 3, 6), (1 / 3, 1 / 4, 31 / 6)):
                    selected = points[np.isclose(points[:, 0], x) & np.isclose(points[:, 1], y)]
                    selected = selected[selected[:, 2] > 0]
                    self.assertGreater(len(selected), 0)
                    np.testing.assert_allclose(selected[:, 2], z, rtol=0, atol=2e-6)

    def test_exact_divisions_on_2000_mm_model(self):
        matrix = self.build_mesh(2000, 1, 0.5)
        matrix[:, :, 2] += matrix[:, :, 0] * 0.13 + matrix[:, :, 1] * 0.07
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 2000, 1, 30, 1, output_format)

    def test_exact_divisions_with_decimal_height(self):
        matrix = self.build_mesh(2, 100.1, 0.2)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 2, 100.1, 1, 7, output_format)

    def test_exact_dimensions_with_nonuniform_edge_cells(self):
        matrix = self.build_mesh(10.123, 10.345, 0.7)
        self.assertEqual(matrix[-1, -1, 0], 10.123)
        self.assertEqual(matrix[0, 0, 1], 10.345)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 10.123, 10.345, 3, 4, output_format)

    def test_ascii_matches_binary_for_clipped_tiles_with_all_side_options(self):
        for sides, border in ((False, 0), (True, 0), (True, 2)):
            with self.subTest(sides=sides, border=border):
                params = dict(self.params, has_borders=sides, borders=border,
                              divideCols=3, divideRow=4)
                files = {}
                for output_format in ("binary", "ascii"):
                    builder = STL(dict(params, stl_format=output_format),
                                  str(self.directory / (output_format + ".stl")), self.matrix)
                    builder.run()
                    files[output_format] = builder.output_files
                for binary, ascii_path in zip(files["binary"], files["ascii"]):
                    np.testing.assert_allclose(
                        read_binary(Path(binary)), read_ascii(Path(ascii_path)), atol=2e-6,
                    )

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
    def test_modal_dialogs_accept_and_release_plugin_running_state(self):
        from qgis.PyQt.QtCore import QTimer, Qt
        module = importlib.import_module(PACKAGE + ".DEMto3D")
        selection = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.SelectLayer_dialog")
        dialog = selection.Dialog()
        try:
            self.assertTrue(dialog.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
            plugin = module.DEMto3D(types.SimpleNamespace())
            with patch.object(plugin, "_has_visible_raster", return_value=True), patch.object(
                module.DEMto3D_dialog, "DEMto3DDialog", return_value=dialog
            ), patch.object(plugin, "_cleanup_canvas_items"), patch.object(plugin, "_update_action_enabled"):
                QTimer.singleShot(0, dialog.accept)
                plugin.run()
            self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
            self.assertFalse(plugin._running)
        finally:
            dialog.close()

    def test_rectangle_shift_selection_and_release(self):
        from qgis.core import QgsPointXY
        from qgis.PyQt.QtCore import QEvent, Qt
        from qgis.PyQt.QtGui import QKeyEvent
        module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.rectangle_map_tool")
        canvas = QgsMapCanvas()
        tool = module.RectangleMapTool(canvas, Mock())
        try:
            tool.startPoint = QgsPointXY(1, 2)
            tool.isEmittingPoint = True
            event = types.SimpleNamespace(pos=lambda: object())
            with patch.object(tool, "toMapCoordinates", return_value=QgsPointXY(5, 4)), patch.object(
                module.QApplication, "keyboardModifiers", return_value=Qt.KeyboardModifier.ShiftModifier
            ):
                tool.canvasMoveEvent(event)
            self.assertTrue(tool.square_mode)
            square = tool.rectangle()
            self.assertEqual(square["width"], square["height"])
            tool.keyReleaseEvent(QKeyEvent(
                QEvent.Type.KeyRelease, Qt.Key.Key_Shift, Qt.KeyboardModifier.NoModifier
            ))
            self.assertFalse(tool.square_mode)
        finally:
            canvas.scene().removeItem(tool.rubberBand)

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
            iface = types.SimpleNamespace(
                mapCanvas=lambda: canvas, mainWindow=lambda: None, actionPan=lambda: None
            )
            dialog = module.DEMto3DDialog(iface)
            try:
                dialog.full_extent()
                self.assertEqual((dialog.z_min, dialog.z_max), (100, 115))
                from qgis.PyQt.QtCore import QTimer
                selection = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.SelectLayer_dialog")
                selection_dialog = selection.Dialog()
                selection_dialog.ui.mMapLayerComboBox.setLayer(raster)
                try:
                    with patch.object(selection, "Dialog", return_value=selection_dialog):
                        QTimer.singleShot(0, selection_dialog.accept)
                        dialog.layer_extent()
                    self.assertEqual(dialog.rect_Params["center"], [20, 20])
                finally:
                    selection_dialog.close()
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
