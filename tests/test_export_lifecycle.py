"""Run with QGIS Python: python tests/test_export_lifecycle.py."""

import gc
import importlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from osgeo import gdal
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsProject, QgsRasterLayer
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QEvent, QThread, Qt, pyqtSignal
from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox, QWidget

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "demto3d_lifecycle_test"
spec = importlib.util.spec_from_file_location(
    PACKAGE, ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
)
package = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = package
spec.loader.exec_module(package)
dialog_module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.DEMto3D_dialog")
export_module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.Export_dialog")


class ControlledModel(QThread):
    """Real Qt thread whose completion is controlled by the test."""

    updateProgress = pyqtSignal()

    def __init__(self, parameters):
        super().__init__()
        self.quit = False
        self.entered = threading.Event()
        self.release = threading.Event()

    def run(self):
        self.updateProgress.emit()
        self.entered.set()
        self.release.wait(10)

    def get_model(self):
        return [[None, None], [None, None]]


class ControlledSTL(ControlledModel):
    def __init__(self, parameters, file_name, matrix):
        super().__init__(parameters)
        self.path = Path(file_name)
        self.output_files = [file_name]

    def run(self):
        self.path.write_bytes(b"partial STL")
        super().run()
        if not self.quit:
            self.path.write_bytes(b"completed STL")


class ExportLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.app = QgsApplication.instance()
        gdal.UseExceptions()
        self.tmp = tempfile.TemporaryDirectory(prefix="demto3d-lifecycle-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.target = self.directory / "terrain.stl"
        raster_path = self.directory / "dem.tif"
        dataset = gdal.GetDriverByName("GTiff").Create(str(raster_path), 4, 4, 1, gdal.GDT_Float32)
        dataset.SetGeoTransform((0, 1, 0, 4, 0, -1))
        dataset.GetRasterBand(1).Fill(10)
        dataset = None
        self.raster = QgsRasterLayer(str(raster_path), "test terrain")
        self.raster.setCrs(QgsCoordinateReferenceSystem("EPSG:25833"))
        QgsProject.instance().addMapLayer(self.raster)
        self.canvas = QgsMapCanvas()
        self.canvas.setLayers([self.raster])
        self.canvas.setDestinationCrs(self.raster.crs())
        self.main_window = QWidget()
        iface = types.SimpleNamespace(mapCanvas=lambda: self.canvas, mainWindow=lambda: self.main_window)
        self.dialog = dialog_module.DEMto3DDialog(iface)
        self.dialog.get_parameters = Mock(return_value=dict(height=2, width=2, spacing_mm=1))
        self.dialog.height = self.dialog.width = 2
        self.dialog.show()
        self.rejected = Mock()
        self.dialog.rejected.connect(self.rejected)
        for target, attribute, replacement in (
            (export_module, "Model", ControlledModel),
            (export_module, "STL", ControlledSTL),
            (QFileDialog, "getSaveFileName", Mock(return_value=(str(self.target), "*.stl"))),
            (QMessageBox, "information", Mock()),
        ):
            patcher = patch.object(target, attribute, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        exporter = getattr(self.dialog, "export_dlg", None)
        if exporter is not None:
            for worker in (exporter.Model, exporter.STL):
                if worker is not None:
                    worker.quit = True
                    worker.release.set()
                    self.assertTrue(worker.wait(3000))
            self.app.processEvents()
        self.dialog.close()
        self.dialog.deleteLater()
        self.canvas.setLayers([])
        QgsProject.instance().removeMapLayer(self.raster.id())
        self.raster = None
        self.canvas.deleteLater()
        self.main_window.deleteLater()
        self.app.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def wait_until(self, condition):
        deadline = time.monotonic() + 3
        while not condition() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.001)
        self.assertTrue(condition())

    def start_export(self):
        self.dialog.do_export()
        exporter = self.dialog.export_dlg
        self.assertTrue(exporter.Model.entered.wait(3))
        gc.collect()
        return exporter

    def start_stl(self, exporter):
        exporter.Model.release.set()
        self.assertTrue(exporter.Model.wait(3000))
        self.wait_until(lambda: exporter.STL is not None)
        self.assertTrue(exporter.STL.entered.wait(3))

    def assert_close_is_blocked(self):
        QTest.keyClick(self.dialog, Qt.Key.Key_Escape)
        self.assertTrue(self.dialog.isVisible(), "Esc closed the dialog during export")
        self.assertFalse(self.dialog.close(), "Window close succeeded during export")
        self.dialog.reject()
        self.dialog.accept()
        self.dialog.done(QDialog.DialogCode.Rejected)
        self.assertTrue(self.dialog.isVisible())
        self.rejected.assert_not_called()

    def test_closing_is_blocked_in_both_phases_and_while_signals_are_pending(self):
        exporter = self.start_export()
        self.assert_close_is_blocked()
        exporter.Model.release.set()
        self.assertTrue(exporter.Model.wait(3000))
        # The model has ended, but its queued finished slot has not started STL yet.
        self.assertIsNone(exporter.STL)
        self.assert_close_is_blocked()
        self.wait_until(lambda: exporter.STL is not None)
        self.assertTrue(exporter.STL.entered.wait(3))
        self.assert_close_is_blocked()
        exporter.STL.release.set()
        self.assertTrue(exporter.STL.wait(3000))
        # The completion slot must restore the UI before closing is allowed.
        self.assert_close_is_blocked()
        self.wait_until(lambda: self.dialog.ui.STLToolButton.isEnabled())
        self.assertEqual(self.target.read_bytes(), b"completed STL")
        QTest.keyClick(self.dialog, Qt.Key.Key_Escape)
        self.assertFalse(self.dialog.isVisible())
        self.rejected.assert_called_once()

    def test_model_cancellation_finishes_before_window_can_close(self):
        exporter = self.start_export()
        self.dialog.ui.cancelProgressToolButton.click()
        self.assertTrue(exporter.Model.quit)
        self.assert_close_is_blocked()
        exporter.Model.release.set()
        self.assertTrue(exporter.Model.wait(3000))
        self.wait_until(lambda: self.dialog.ui.STLToolButton.isEnabled())
        self.assertIsNone(exporter.STL)
        self.assertFalse(self.target.exists())
        self.assertTrue(self.dialog.close())
        self.assertFalse(self.dialog.isVisible())

    def test_stl_cancellation_cleans_partial_file_before_window_can_close(self):
        exporter = self.start_export()
        self.start_stl(exporter)
        self.assertTrue(self.target.exists())
        self.dialog.ui.cancelProgressToolButton.click()
        self.assertTrue(exporter.STL.quit)
        self.assert_close_is_blocked()
        exporter.STL.release.set()
        self.assertTrue(exporter.STL.wait(3000))
        self.wait_until(lambda: self.dialog.ui.STLToolButton.isEnabled())
        self.assertFalse(self.target.exists())
        self.assertTrue(self.dialog.close())
        self.assertFalse(self.dialog.isVisible())

    def test_dialog_can_close_without_starting_an_export(self):
        QTest.keyClick(self.dialog, Qt.Key.Key_Escape)
        self.assertFalse(self.dialog.isVisible())
        self.dialog.show()
        self.assertTrue(self.dialog.close())
        self.assertFalse(self.dialog.isVisible())


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    unittest.main(verbosity=2)
