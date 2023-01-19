# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2022 by Javier
        email                : demto3d@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import absolute_import
import os
import math
import json

from osgeo import gdal
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog, QApplication, QMenu
from qgis.PyQt.QtGui import QColor, QCursor
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsRubberBand, QgsMapTool

from . import Export_dialog
from . import SelectLayer_dialog
from .DEMto3D_dialog_base import Ui_DEMto3DDialogBase
from qgis.core import QgsPointXY, QgsPoint, QgsRectangle, QgsFeature, QgsProject, QgsGeometry, QgsCoordinateTransform, Qgis, QgsMapLayerProxyModel, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsVectorFileWriter
from qgis.analysis import QgsZonalStatistics

from ..model_builder.Model_Builder import Model


class DEMto3DDialog(QDialog, Ui_DEMto3DDialogBase):
    """ Layer to print. """
    layer = None

    ''' Region of interest properties '''
    map_crs = None
    units = None
    roi_x_max = 0
    roi_x_min = 0
    roi_y_max = 0
    roi_y_min = 0
    z_max = 0
    z_min = 0
    rect_Params = None
    extent = None

    ''' Model dimensions '''
    height = 0
    width = 0
    scale_h = 0
    scale_w = 0
    scale = 0
    z_scale = 0

    ''' Raster properties '''
    cell_size = 0
    cols = 0
    rows = 0
    raster_x_max = 0
    raster_x_min = 0
    raster_y_max = 0
    raster_y_min = 0

    divisions = None
    rect_map_tool = None
    lastSavingPath = ''

    changeScale = True

    def __init__(self, iface):
        """Constructor."""
        QDialog.__init__(self)
        self.ui = Ui_DEMto3DDialogBase()
        self.ui.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.canvas.destinationCrsChanged.connect(self.setCanvasCRS)
        self.setCanvasCRS()

        self.units = self.map_crs.mapUnits()
        # --- QgsUnitTypes.DistanceUnit ---
        # DistanceMeters         0 Meters.
        # DistanceKilometers     1 Kilometers.
        # DistanceFeet           2 Imperial feet.
        # DistanceNauticalMiles  3 Nautical miles.
        # DistanceYards          4 Imperial yards.
        # DistanceMiles          5 Terrestrial miles.
        # DistanceDegrees        6 Degrees, for planar geographic CRS distance measurements.
        # DistanceCentimeters    7 Centimeters.
        # DistanceMillimeters    8 Millimeters.
        # DistanceUnknownUnit    9 Unknown distance unit.

        # region LAYER ACTION
        # fill layer combobox with raster visible layers in mapCanvas
        self.viewLayers = self.canvas.layers()
        self.ui.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.ui.mMapLayerComboBox.setExcludedProviders(['wms', 'wfs'])
        self.layer = self.ui.mMapLayerComboBox.currentLayer()
        self.get_raster_properties()
        self.ui.mMapLayerComboBox.layerChanged.connect(self.get_currlayer)
        # endregion

        # region EXTENSION ACTION
        self.extent = None

        self.ui.FullExtToolButton.clicked.connect(self.full_extent)
        self.ui.LayerExtToolButton.clicked.connect(self.layer_extent)
        self.ui.CustomExtToolButton.clicked.connect(self.custom_extent)

        self.ui.XMinLineEdit.returnPressed.connect(self.upload_extent)
        self.ui.XMaxLineEdit.returnPressed.connect(self.upload_extent)
        self.ui.YMaxLineEdit.returnPressed.connect(self.upload_extent)
        self.ui.YMinLineEdit.returnPressed.connect(self.upload_extent)

        self.ui.WidthGeoLineEdit.returnPressed.connect(self.upload_extent_fromWH)
        self.ui.HeightGeoLineEdit.returnPressed.connect(self.upload_extent_fromWH)

        self.ui.LimitsParamGframe.hide()

        # endregion

        # region DIMENSION ACTION
        self.ui.HeightLineEdit.textEdited.connect(self.upload_size_from_height)
        self.ui.WidthLineEdit.textEdited.connect(self.upload_size_from_width)
        self.ui.ScaleLineEdit.scaleChanged.connect(self.upload_size_from_scale)
        # endregion

        self.ui.ZScaleDoubleSpinBox.valueChanged.connect(self.get_height_model)
        self.ui.BaseHeightLineEdit.returnPressed.connect(self.get_height_model)
        self.ui.BaseModellineEdit.returnPressed.connect(self.get_height_model)

        self.ui.RowPartsSpinBox.valueChanged.connect(self.paint_model_division)
        self.ui.ColPartsSpinBox.valueChanged.connect(self.paint_model_division)

        # region BOTTOM BUTTONS ACTION
        menu = QMenu(self.iface.mainWindow())
        menu.addAction(self.tr('Export settings'), self.export_params)
        menu.addAction(self.tr('Import settings'), self.import_params)
        menu.addSeparator()
        menu.addAction(self.tr('Export extension to GeoJSON'), self.exportExtensionToJSON)

        self.ui.ParamPushButton.setMenu(menu)

        self.ui.CancelToolButton.clicked.connect(self.reject)
        self.ui.STLToolButton.clicked.connect(self.do_export)
        self.rejected.connect(self.reject_func)
        # endregion

        self.ui.ProgressLabel.hide()

    def setCanvasCRS(self):
        try:
            self.map_crs = self.canvas.mapSettings().destinationCrs()
        except BaseException:
            self.map_crs = self.canvas.mapRenderer().destinationCrs()

    def reject_func(self):
        if self.rect_map_tool is not None:
            self.rect_map_tool.reset()
            self.rect_map_tool.deactivate()
            self.iface.actionPan().trigger()

    # region Extension functions

    def export_params(self):
        parameters = self.get_parameters()
        file_name = self.layer.name() + '_param.txt'
        if parameters != 0:
            setting_file = QFileDialog.getSaveFileName(self, self.tr(
                'Export settings'), self.lastSavingPath + file_name, "*.txt")
            if setting_file[0] != '':
                self.lastSavingPath = os.path.dirname(setting_file[0]) + '//'
                obj_info = {
                    "layer": parameters['layer'],
                    "roi_x_max": parameters['roi_x_max'],
                    "roi_x_min": parameters['roi_x_min'],
                    "roi_y_max": parameters['roi_y_max'],
                    "roi_y_min": parameters['roi_y_min'],
                    "roi_rect_Param": parameters["roi_rect_Param"],
                    "spacing_mm": parameters['spacing_mm'],
                    "height": parameters['height'],
                    "width": parameters['width'],
                    "z_scale": parameters['z_scale'],
                    "scale": parameters['scale'],
                    "scale_h": parameters['scale_h'],
                    "scale_w": parameters['scale_w'],
                    "z_inv": parameters['z_inv'],
                    "z_base": parameters['z_base'],
                    "divideRow": parameters['divideRow'],
                    "divideCols": parameters['divideCols'],
                    "projected": parameters['projected'],
                    "crs_layer": parameters['crs_layer'].toProj4(),
                    "crs_map": parameters['crs_map'].toProj4(),
                    "trimmed": parameters['trimmed'],
                }
                with open(setting_file[0], 'w') as fp:
                    json.dump(obj_info, fp, indent=4)
                QMessageBox.information(self, self.tr(
                    "Attention"), self.tr("Parameters exported"))
        else:
            QMessageBox.warning(self, self.tr("Attention"),
                                self.tr("Fill the data correctly"))

    def import_params(self):
        setting_file = QFileDialog.getOpenFileName(self, self.tr(
            "Open settings file"), self.lastSavingPath, "*.txt")
        if setting_file[0] != '':
            with open(setting_file[0]) as json_file:
                try:
                    parameters = json.load(json_file)

                    param_crs = QgsCoordinateReferenceSystem()
                    param_crs.createFromProj4(parameters["crs_map"])
                    if (self.map_crs != param_crs):
                        # do traslation
                        transform = QgsCoordinateTransform(param_crs, self.map_crs, QgsProject.instance())
                        pointMin = transform.transform(parameters["roi_x_min"], parameters["roi_y_min"])
                        pointMax = transform.transform(parameters["roi_x_max"], parameters["roi_y_max"])
                        self.roi_x_max = pointMax.x()
                        self.roi_y_min = pointMin.y()
                        self.roi_x_min = pointMin.x()
                        self.roi_y_max = pointMax.y()
                    else:
                        self.roi_x_max = parameters["roi_x_max"]
                        self.roi_y_min = parameters["roi_y_min"]
                        self.roi_x_min = parameters["roi_x_min"]
                        self.roi_y_max = parameters["roi_y_max"]

                    self.ui.XMaxLineEdit.setText(str(round(self.roi_x_max, 3)))
                    self.ui.YMinLineEdit.setText(str(round(self.roi_y_min, 3)))
                    self.ui.XMinLineEdit.setText(str(round(self.roi_x_min, 3)))
                    self.ui.YMaxLineEdit.setText(str(round(self.roi_y_max, 3)))

                    if "roi_rect_Param" in parameters:
                        self.rect_Params = parameters["roi_rect_Param"]
                    else:
                        rec = QgsRectangle(self.roi_x_min, self.roi_y_min, self.roi_x_max, self.roi_y_max)
                        self.rect_Params = {'center': [rec.center().x(), rec.center().y()], 'width': rec.width(), 'height': rec.height(), 'rotation': 0}

                    self.ui.WidthGeoLineEdit.setText(str(round(self.rect_Params["width"], 3)))
                    self.ui.HeightGeoLineEdit.setText(str(round(self.rect_Params["height"], 3)))

                    self.ui.SpacingLineEdit.setText(str(round(parameters["spacing_mm"], 2)))
                    self.scale = parameters['scale']
                    self.scale_h = parameters['scale_h']
                    self.scale_w = parameters['scale_w']
                    self.ui.ScaleLineEdit.setScale(int(parameters["scale"]))
                    self.upload_size_from_scale()
                    self.ui.ZScaleDoubleSpinBox.setValue(parameters["z_scale"])

                    self.get_z_max_z_min()
                    self.ui.BaseHeightLineEdit.setText(str(round(parameters["z_base"], 3)))
                    self.ui.RevereseZCheckBox.setChecked(parameters["z_inv"])
                    self.get_height_model()

                    if "divideRow" in parameters:
                        self.ui.RowPartsSpinBox.setValue(int(parameters["divideRow"]))
                    if "divideCols" in parameters:
                        self.ui.ColPartsSpinBox.setValue(int(parameters["divideCols"]))

                    self.paint_extent(self.rect_Params)

                except:
                    QMessageBox.warning(self, self.tr("Attention"), self.tr("Wrong file"))

    def exportExtensionToJSON(self):
        try:
            file_name = self.layer.name() + '_area.geojson'
            setting_file = QFileDialog.getSaveFileName(self, self.tr('Export extension to GeoJSON'), self.lastSavingPath + file_name, "*.geojson")
            if setting_file[0] != '':
                self.lastSavingPath = os.path.dirname(setting_file[0]) + '//'
                # Specify the geometry type
                layer = QgsVectorLayer('Polygon?crs=' + self.map_crs.authid(), 'polygon', 'memory')
                # Set the provider to accept the data source
                prov = layer.dataProvider()

                points = getPointsFromRectangleParams(self.rect_Params)
                points = [[QgsPointXY(points[0][0], points[0][1]), QgsPointXY(points[1][0], points[1][1]),
                           QgsPointXY(points[2][0], points[2][1]), QgsPointXY(points[3][0], points[3][1])]]
                # Add a new feature and assign the geometry
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPolygonXY(points))
                prov.addFeatures([feat])
                # Update extent of the layer
                layer.updateExtents()
                # # Add the layer to the Layers panel
                # QgsMapLayerRegistry.instance().addMapLayers([layer])
                QgsVectorFileWriter.writeAsVectorFormat(layer, setting_file[0], 'utf-8', self.map_crs, 'GeoJSON', layerOptions=['COORDINATE_PRECISION=3'])
                QMessageBox.information(self, self.tr("Attention"), self.tr("Extension exported"))
        except:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Fill the data correctly"))

    # endregion

    def do_export(self):

        def export():
            stl_file = QFileDialog.getSaveFileName(self, self.tr(
                'Export to STL'), self.lastSavingPath + layer_name, filter="*.stl")
            if stl_file[0] != '':
                self.lastSavingPath = os.path.dirname(stl_file[0]) + '//'
                Export_dialog.Export(self, parameters, stl_file[0])

        parameters = self.get_parameters()
        layer_name = self.layer.name() + '_model.stl'
        if parameters != 0:
            row_stl = int(
                math.ceil(self.height / parameters["spacing_mm"]) + 1)
            col_stl = int(math.ceil(self.width / parameters["spacing_mm"]) + 1)
            tooMuchPoints = row_stl * col_stl > 500000
            if tooMuchPoints:
                reply = QMessageBox.question(self, self.tr('Export to STL'),
                                             self.tr(
                    'The construction of the STL file could takes several minutes. Do you want to continue?'),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    export()
            else:
                export()
        else:
            QMessageBox.warning(self, self.tr("Attention"),
                                self.tr("Fill the data correctly"))

    def get_currlayer(self, layer):
        if layer and self.layer != layer:
            self.ini_dialog()
            # bands = layer.bandCount()
            self.layer = layer
            self.get_raster_properties()

    def ini_dialog(self):
        self.ui.XMaxLineEdit.clear()
        self.ui.XMinLineEdit.clear()
        self.ui.YMaxLineEdit.clear()
        self.ui.YMinLineEdit.clear()
        if self.extent:
            self.canvas.scene().removeItem(self.extent)
            self.extent = None
        if self.divisions:
            self.canvas.scene().removeItem(self.divisions)
            self.divisions = []
        self.ini_dimensions()
        self.ui.ZMaxLabel.setText('0 m')
        self.ui.ZMinLabel.setText('0 m')

    def ini_dimensions(self):
        self.ui.HeightLineEdit.clear()
        self.height = 0
        self.ui.WidthLineEdit.clear()
        self.width = 0
        self.changeScale = False
        self.ui.ScaleLineEdit.setScale(1)
        self.scale_h = 0
        self.scale_w = 0
        self.scale = 0
        self.ui.RecomSpacinglabel.setText('0.2 mm')
        self.ui.BaseHeightLineEdit.clear()
        self.ui.HeightModelLabel.setText('0 mm')

    def get_raster_properties(self):
        self.cell_size = self.layer.rasterUnitsPerPixelX()
        self.rows = self.layer.height()
        self.cols = self.layer.width()
        rec = self.layer.extent()
        self.raster_x_max = rec.xMaximum()
        self.raster_x_min = rec.xMinimum()
        self.raster_y_max = rec.yMaximum()
        self.raster_y_min = rec.yMinimum()

    # region Extension functions

    def full_extent(self):
        rec = self.layer.extent()
        canvasCRS = self.map_crs
        layerCRS = self.layer.crs()
        if canvasCRS != layerCRS:
            transform = QgsCoordinateTransform(layerCRS, canvasCRS, QgsProject.instance())
            rec = transform.transform(rec)

        self.rect_Params = {'center': [rec.center().x(), rec.center().y()], 'width': rec.width(), 'height': rec.height(), 'rotation': 0}
        self.paint_extent(self.rect_Params)
        self.get_z_max_z_min()
        self.ini_dimensions()

    def layer_extent(self):
        select_layer_dialog = SelectLayer_dialog.Dialog()
        if select_layer_dialog.exec_():
            layer = select_layer_dialog.get_layer()
            if layer:
                rec = layer.extent()
                canvasCRS = self.map_crs
                layerCRS = layer.crs()
                if canvasCRS != layerCRS:
                    transform = QgsCoordinateTransform(layerCRS, canvasCRS, QgsProject.instance())
                    rec = transform.transform(rec)

                self.rect_Params = {'center': [rec.center().x(), rec.center().y()], 'width': rec.width(), 'height': rec.height(), 'rotation': 0}
                self.get_custom_extent_cb(self.rect_Params)

    def custom_extent(self):
        self.iface.messageBar().pushMessage("Info", self.tr(
            "Click and drag the mouse to draw print extent"), level=Qgis.Info, duration=3)
        if self.extent:
            self.canvas.scene().removeItem(self.extent)
            self.extent = None
        if self.divisions:
            self.canvas.scene().removeItem(self.divisions)
            self.divisions = []
        self.rect_map_tool = RectangleMapTool(self.canvas, self.get_custom_extent_cb)
        self.canvas.setMapTool(self.rect_map_tool)

    def get_custom_extent_cb(self, rectParams):
        # Geometria del area
        points = getPointsFromRectangleParams(rectParams)
        points = [[QgsPointXY(points[0][0], points[0][1]), QgsPointXY(points[1][0], points[1][1]),
                   QgsPointXY(points[2][0], points[2][1]), QgsPointXY(points[3][0], points[3][1])]]
        rec = QgsGeometry.fromPolygonXY(points)
        # extension de la capa DEM
        layer_extension = self.layer.extent()
        dataCRS = self.layer.crs()
        canvasCRS = self.map_crs
        if dataCRS != canvasCRS:
            transform = QgsCoordinateTransform(dataCRS, canvasCRS, QgsProject.instance())
            layer_extension = transform.transform(layer_extension)

        if rec.intersects(layer_extension):
            # extension = rec.intersect(layer_extension)
            self.rect_Params = rectParams
            self.paint_extent(rectParams)
            self.iface.actionPan().trigger()
            self.get_z_max_z_min()
            self.ini_dimensions()
        else:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Print extent defined outside layer extent"))
            self.paint_extent(self.rect_Params)

    def upload_extent(self):
        try:
            self.roi_x_max = float(self.ui.XMaxLineEdit.text())
            self.roi_x_min = float(self.ui.XMinLineEdit.text())
            self.roi_y_max = float(self.ui.YMaxLineEdit.text())
            self.roi_y_min = float(self.ui.YMinLineEdit.text())
            p3 = QgsPoint(self.roi_x_min, self.roi_y_min)
            p1 = QgsPoint(self.roi_x_max, self.roi_y_max)

            # If we directly start typing coordinates, rect_Params is never
            # initialized.  Assuming rotation of 0.
            # TODO: It's probably better to initialize rect_Params some other way.
            if self.rect_Params is None:
                self.rect_Params = rectangleHWCenterFrom2pCreate(p3, p1, 0)
            else:
                self.rect_Params = rectangleHWCenterFrom2pCreate(
                    p3, p1, self.rect_Params["rotation"])
            
            self.paint_extent(self.rect_Params)
            self.get_z_max_z_min()
            self.ini_dimensions()
        except ValueError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Value entered incorrect"))

    def upload_extent_fromWH(self):
        if self.ui.WidthGeoLineEdit.text() == '' or self.ui.HeightGeoLineEdit.text() == '':
            return
        if self.roi_x_min == 0 and self.roi_y_min == 0 and self.roi_x_max == 0 and self.roi_y_max == 0:
            return
        try:
            widthGeo = float(self.ui.WidthGeoLineEdit.text())
            heightGeo = float(self.ui.HeightGeoLineEdit.text())
            p2x, p2y = getPolarPoint(self.roi_x_min, self.roi_y_min, self.rect_Params["rotation"], widthGeo)
            p1x, p1y = getPolarPoint(p2x, p2y, self.rect_Params["rotation"] + math.pi * 0.5, heightGeo)
            centerX = (self.roi_x_min + p1x) * 0.5
            centerY = (self.roi_y_min + p1y) * 0.5
            self.rect_Params = {'center': [centerX, centerY], 'width': widthGeo, 'height': heightGeo, 'rotation': self.rect_Params["rotation"]}
            self.paint_extent(self.rect_Params)
            self.get_z_max_z_min()
            self.ini_dimensions()
        except ValueError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Value entered incorrect"))

    def paint_extent2(self, rec):
        self.roi_x_max = rec.xMaximum()
        self.ui.XMaxLineEdit.setText(str(round(rec.xMaximum(), 3)))
        self.roi_y_min = rec.yMinimum()
        self.ui.YMinLineEdit.setText(str(round(rec.yMinimum(), 3)))
        self.roi_x_min = rec.xMinimum()
        self.ui.XMinLineEdit.setText(str(round(rec.xMinimum(), 3)))
        self.roi_y_max = rec.yMaximum()
        self.ui.YMaxLineEdit.setText(str(round(rec.yMaximum(), 3)))

        self.ui.WidthGeoLineEdit.setText(
            str(round(rec.xMaximum() - rec.xMinimum(), 3)))
        self.ui.HeightGeoLineEdit.setText(
            str(round(rec.yMaximum() - rec.yMinimum(), 3)))

        if self.extent:
            self.canvas.scene().removeItem(self.extent)
            self.extent = None
        if self.divisions:
            self.canvas.scene().removeItem(self.divisions)
            self.divisions = []

        self.extent = QgsRubberBand(self.canvas, True)

        points = [QgsPoint(self.roi_x_max, self.roi_y_min), QgsPoint(self.roi_x_max, self.roi_y_max),
                  QgsPoint(self.roi_x_min, self.roi_y_max), QgsPoint(self.roi_x_min, self.roi_y_min),
                  QgsPoint(self.roi_x_max, self.roi_y_min)]

        self.extent.setToGeometry(QgsGeometry.fromPolyline(points), None)
        self.extent.setColor(QColor(227, 26, 28, 255))
        self.extent.setWidth(3)
        self.extent.setLineStyle(Qt.PenStyle(Qt.DashLine))

        self.paint_model_division()

        self.canvas.refresh()

    def paint_extent(self, rectParams):
        width = rectParams["width"]
        height = rectParams["height"]
        points = getPointsFromRectangleParams(rectParams)

        #       0       W       1
        #       +---------------+
        #       |               |
        #     H |               + AuxPto
        #       |               |
        #       +---------------+   ----------> rotation
        #       3       W       2

        self.roi_x_max = points[1][0]
        self.ui.XMaxLineEdit.setText(str(round(self.roi_x_max, 3)))
        self.roi_y_min = points[3][1]
        self.ui.YMinLineEdit.setText(str(round(self.roi_y_min, 3)))
        self.roi_x_min = points[3][0]
        self.ui.XMinLineEdit.setText(str(round(self.roi_x_min, 3)))
        self.roi_y_max = points[1][1]
        self.ui.YMaxLineEdit.setText(str(round(self.roi_y_max, 3)))

        self.ui.WidthGeoLineEdit.setText(str(round(width, 3)))
        self.ui.HeightGeoLineEdit.setText(str(round(height, 3)))

        if self.extent:
            self.canvas.scene().removeItem(self.extent)
            self.extent = None
        if self.divisions:
            self.canvas.scene().removeItem(self.divisions)
            self.divisions = []

        self.extent = QgsRubberBand(self.canvas, True)

        points = [QgsPoint(points[0][0], points[0][1]), QgsPoint(points[1][0], points[1][1]),
                  QgsPoint(points[2][0], points[2][1]), QgsPoint(points[3][0], points[3][1]),
                  QgsPoint(points[0][0], points[0][1])]

        self.extent.setToGeometry(QgsGeometry.fromPolyline(points), None)
        self.extent.setColor(QColor(227, 26, 28, 255))
        self.extent.setWidth(3)
        self.extent.setLineStyle(Qt.PenStyle(Qt.DashLine))

        self.paint_model_division()

        self.canvas.refresh()

    def paint_model_division(self):
        if self.rect_Params is None:
            return
        if self.divisions:
            self.canvas.scene().removeItem(self.divisions)
            self.divisions = []
        x_models = int(self.ui.ColPartsSpinBox.value())
        y_models = int(self.ui.RowPartsSpinBox.value())
        points = getPointsFromRectangleParams(self.rect_Params)
        lines = []
        if y_models > 1:
            model_height = self.rect_Params["height"] / y_models
            custRot = self.rect_Params['rotation'] - math.pi * 0.5
            for i in range(1, y_models):
                p1 = getPolarPoint(points[0][0], points[0][1], custRot, model_height * i)
                p2 = getPolarPoint(points[1][0], points[1][1], custRot, model_height * i)
                lines.append([QgsPointXY(p1[0], p1[1]), QgsPointXY(p2[0], p2[1])])
        if x_models > 1:
            model_width = self.rect_Params["width"] / x_models
            for i in range(1, x_models):
                p1 = getPolarPoint(points[3][0], points[3][1], self.rect_Params['rotation'], model_width * i)
                p2 = getPolarPoint(points[0][0], points[0][1], self.rect_Params['rotation'], model_width * i)
                lines.append([QgsPointXY(p1[0], p1[1]), QgsPointXY(p2[0], p2[1])])
        if lines:
            self.divisions = QgsRubberBand(self.canvas, False)
            self.divisions.setColor(QColor(227, 26, 28, 255))
            self.divisions.setWidth(3)
            self.divisions.setLineStyle(Qt.PenStyle(Qt.DashDotLine))
            self.divisions.setToGeometry(QgsGeometry.fromMultiPolylineXY(lines), None)

    def get_z_max_z_min(self):

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        points = getPointsFromRectangleParams(self.rect_Params)
        # Specify the geometry type
        layer = QgsVectorLayer('Polygon?crs=' + self.map_crs.authid(), 'polygon', 'memory')
        # Set the provider to accept the data source
        prov = layer.dataProvider()
        geom = [[QgsPointXY(points[0][0], points[0][1]), QgsPointXY(points[1][0], points[1][1]),
                 QgsPointXY(points[2][0], points[2][1]), QgsPointXY(points[3][0], points[3][1])]]
        # Add a new feature and assign the geometry
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolygonXY(geom))
        prov.addFeatures([feat])
        # Update extent of the layer
        layer.updateExtents()

        zoneStat = QgsZonalStatistics(layer, self.layer, "", 1, QgsZonalStatistics.Max | QgsZonalStatistics.Min)
        zoneStat.calculateStatistics(None)

        minVal = 0
        maxVal = 0
        stats = layer.getFeature(1).attributes()
        if (len(stats) > 0):
            if stats[0] is not None:
                minVal = stats[0]
            if stats[1] is not None:
                maxVal = stats[1]

        self.z_max = round(maxVal, 3)
        self.z_min = round(minVal, 3)
        self.ui.ZMaxLabel.setText(str(self.z_max) + ' m')
        self.ui.ZMinLabel.setText(str(self.z_min) + ' m')

        layer = None
        QApplication.restoreOverrideCursor()

    # endregion

    # region Dimensions function

    def get_min_spacing(self):
        min_spacing = 0
        if self.units == 6:  # Map unit -> Degree
            if self.layer.crs().mapUnits() == 6:  # data unit -> Degree
                width_roi = self.rect_Params["width"]
                min_spacing = round(self.cell_size * self.width / width_roi, 2)
            else:                                # data unit -> others. Meters, ...
                width_roi = self.rect_Params["width"]
                cell_size_deg = self.cell_size / math.pi * 180 / \
                    math.cos(self.roi_y_max * math.pi / 180) / 6371000
                min_spacing = round(cell_size_deg * self.width / width_roi, 2)
        else:                # Map unit -> Others, Meters, ...
            if self.layer.crs().mapUnits() == 6:  # data unit -> Degree
                width_roi = self.rect_Params["width"]
                cell_size_m = self.cell_size * math.pi / 180 * \
                    math.cos(self.raster_y_max * math.pi / 180) * 6371000
                min_spacing = round(cell_size_m * self.width / width_roi, 2)
            else:                                 # data unit -> others. Meters, ...
                width_roi = self.rect_Params["width"]
                min_spacing = round(self.cell_size * self.width / width_roi, 2)
        if min_spacing < 0.2:
            self.ui.RecomSpacinglabel.setText('0.2 mm')
        else:
            self.ui.RecomSpacinglabel.setText(str(min_spacing) + ' mm')

    def upload_size_from_height(self):
        try:
            width_roi = self.rect_Params["width"]
            height_roi = self.rect_Params["height"]
            self.height = float(self.ui.HeightLineEdit.text())
            self.width = round(width_roi * self.height / height_roi, 2)
            self.ui.WidthLineEdit.setText(str(self.width))
            if self.units == 6:  # Degree
                dist = width_roi * math.pi / 180 * \
                    math.cos(self.roi_y_max * math.pi / 180) * 6371000 * 1000
                if abs(dist) < 0.00001:
                    dist = 2 * math.pi * 6371000 * 1000
                self.scale = round(dist / self.width, 6)
                self.scale_h = self.scale
                self.scale_w = self.scale
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(int(self.scale))
            else:                # Meters
                self.scale_h = height_roi / self.height * 1000
                self.scale_w = width_roi / self.width * 1000
                self.scale = round((self.scale_h + self.scale_w) / 2, 6)
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(int(self.scale))
            self.get_min_spacing()
            self.get_height_model()
        except ZeroDivisionError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Define print extent"))
            self.ui.HeightLineEdit.clear()
        except ValueError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Value entered incorrect"))
            self.ui.HeightLineEdit.clear()

    def upload_size_from_width(self):
        try:
            width_roi = self.rect_Params["width"]
            height_roi = self.rect_Params["height"]
            self.width = float(self.ui.WidthLineEdit.text())
            self.height = round(height_roi * self.width / width_roi, 2)
            self.ui.HeightLineEdit.setText(str(self.height))
            if self.units == 6:  # Degree
                dist = width_roi * math.pi / 180 * \
                    math.cos(self.roi_y_max * math.pi / 180) * 6371000 * 1000
                if abs(dist) < 0.00001:
                    dist = 2 * math.pi * 6371000 * 1000
                self.scale = round(dist / self.width, 6)
                self.scale_h = self.scale
                self.scale_w = self.scale
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(int(self.scale))
            else:                # Meters
                self.scale_h = height_roi / self.height * 1000
                self.scale_w = width_roi / self.width * 1000
                self.scale = round((self.scale_h + self.scale_w) / 2, 6)
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(int(self.scale))
            self.get_min_spacing()
            self.get_height_model()
        except ZeroDivisionError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Define size model"))
            self.ui.WidthLineEdit.clear()
        except ValueError:
            QMessageBox.warning(self, self.tr("Attention"), self.tr("Value entered incorrect"))
            self.ui.WidthLineEdit.clear()

    def upload_size_from_scale(self):
        if self.changeScale == False:
            self.changeScale = True
        else:
            try:
                width_roi = self.rect_Params["width"]
                height_roi = self.rect_Params["height"]
                self.scale = float(self.ui.ScaleLineEdit.scale())
                self.scale_h = self.scale
                self.scale_w = self.scale
                if self.units == 6:  # Degree
                    dist = width_roi * math.pi / 180 * \
                        math.cos(self.roi_y_max * math.pi / 180) * \
                        6371000 * 1000
                    if abs(dist) < 0.00001:
                        dist = 2 * math.pi * 6371000 * 1000
                    self.width = round(dist / self.scale, 2)
                    self.ui.WidthLineEdit.setText(str(self.width))
                    self.height = round(height_roi * self.width / width_roi, 2)
                    self.ui.HeightLineEdit.setText(str(self.height))
                else:                # Meters
                    self.height = round(height_roi / self.scale * 1000, 2)
                    self.ui.HeightLineEdit.setText(str(self.height))
                    self.width = round(width_roi / self.scale * 1000, 2)
                    self.ui.WidthLineEdit.setText(str(self.width))
                self.get_min_spacing()
                self.get_height_model()

            except ZeroDivisionError:
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Define print extent"))
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(1)
                self.scale = 0
                self.ui.WidthLineEdit.clear()
            except ValueError:
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Value entered incorrect"))
                self.changeScale = False
                self.ui.ScaleLineEdit.setScale(1)
                self.scale = 0
                self.ui.WidthLineEdit.clear()
                self.ui.HeightLineEdit.clear()

    # endregion

    def get_height_model(self):
        if self.ui.BaseHeightLineEdit.text() == '' or self.ui.BaseHeightLineEdit.text() == '-':
            return
        try:
            z_base = float(self.ui.BaseHeightLineEdit.text())
            self.z_scale = self.ui.ZScaleDoubleSpinBox.value()
            base_model = float(self.ui.BaseModellineEdit.text())
            h_model = round((self.z_max - z_base) / self.scale * 1000 * self.z_scale + base_model, 1)
            if h_model == float("inf"):
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Define size model"))
                self.ui.BaseHeightLineEdit.clear()
                return
            if z_base <= self.z_max:
                self.ui.HeightModelLabel.setText(str(h_model) + ' mm')
            else:
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Height of the base must be lower than DEM highest point"))
                self.ui.BaseHeightLineEdit.clear()
        except ZeroDivisionError:
            if self.scale == 0 and self.roi_x_max != 0:
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Define size model"))
            else:
                QMessageBox.warning(self, self.tr("Attention"), self.tr("Define print extent"))
            self.ui.BaseHeightLineEdit.clear()

    def get_parameters(self):
        projected = True
        if self.units == 6:  # Degree
            projected = False

        provider = self.layer.dataProvider()
        path = provider.dataSourceUri()
        path_layer = path.split('|')
        self.z_scale = self.ui.ZScaleDoubleSpinBox.value()

        self.get_height_model()
        try:
            spacing_mm = float(self.ui.SpacingLineEdit.text())
            z_base = float(self.ui.BaseHeightLineEdit.text())
        except ValueError:
            return 0

        if self.ui.RevereseZCheckBox.isChecked():
            z_inv = True
        else:
            z_inv = False

        rows = int(self.ui.RowPartsSpinBox.value())
        cols = int(self.ui.ColPartsSpinBox.value())

        baseModel = float(self.ui.BaseModellineEdit.text())

        trimmed = False

        return {"layer": path_layer[0],
                "roi_x_max": self.roi_x_max, "roi_x_min": self.roi_x_min, "roi_y_max": self.roi_y_max, "roi_y_min": self.roi_y_min, "roi_rect_Param": self.rect_Params,
                "spacing_mm": spacing_mm, "height": self.height, "width": self.width,
                "z_scale": self.z_scale, "scale": self.scale, "scale_h": self.scale_h, "scale_w": self.scale_w,
                "z_inv": z_inv, "z_base": z_base, "baseModel": baseModel,
                "projected": projected, "crs_layer": self.layer.crs(), "crs_map": self.map_crs, "divideRow": rows, "divideCols": cols, "trimmed": trimmed}


class RectangleMapTool(QgsMapTool):
    startPoint = None
    endPoint = None
    isEmittingPoint = True
    rotation = 0

    def __init__(self, canvas, callback):
        self.canvas = canvas
        QgsMapTool.__init__(self, self.canvas)
        self.callback = callback
        self.rubberBand = QgsRubberBand(self.canvas, 3)
        self.rubberBand.setColor(QColor(227, 26, 28, 255))
        self.rubberBand.setWidth(3)
        self.rubberBand.setLineStyle(Qt.PenStyle(Qt.DashLine))
        self.rotation = self.canvas.rotation() * math.pi / 180
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(True)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.rubberBand.hide()
            self.callback(r)
        return None

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, start_point, end_point):
        self.rubberBand.reset(True)
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        # points = [QgsPointXY(start_point.x(), start_point.y()),
        #           QgsPointXY(start_point.x(), end_point.y()),
        #           QgsPointXY(end_point.x(), end_point.y()),
        #           QgsPointXY(end_point.x(), start_point.y())]
        # points = rectangle2pCreate(start_point, end_point, -self.rotation)

        rectParams = rectangleHWCenterFrom2pCreate(start_point, end_point, self.rotation)
        points = getPointsFromRectangleParams(rectParams)

        self.rubberBand.addPoint(QgsPointXY(points[0][0], points[0][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[1][0], points[1][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[2][0], points[2][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[3][0], points[3][1]), False)
        # true to update canvas
        self.rubberBand.addPoint(QgsPointXY(points[0][0], points[0][1]), True)
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None
        # return QgsRectangle(self.startPoint, self.endPoint)
        rectParams = rectangleHWCenterFrom2pCreate(self.startPoint, self.endPoint, self.rotation)
        return rectParams

    def deactivate(self):
        super(RectangleMapTool, self).deactivate()


def rectangle2pCreate(firstPoint, secondPoint, azimutO):

        #     X1Y2 (1)        H2      secondPoint (2)
        #       +---------------------------+
        #       |                           |
        #       |                           |
        #    V1 |                           | V2
        #       |                           |
        #       |             H1            |
        #       +---------------------------+   ----------> AzimutO
        #     firstPoint (0 - 4)         X2Y1 (3)

    templinePoint = QgsPointXY(secondPoint.x() + 10 * math.sin(azimutO), secondPoint.y() + 10 * math.cos(azimutO))
    p1 = pointToLine2D(firstPoint.x(), firstPoint.y(), secondPoint.x(), secondPoint.y(), templinePoint.x(), templinePoint.y())

    ax = p1.x()-secondPoint.x()
    ay = p1.y()-secondPoint.y()
    width = math.sqrt(ax**2 + ay**2)
    ax = p1.x()-firstPoint.x()
    ay = p1.y()-firstPoint.y()
    height = math.sqrt(ax**2 + ay**2)

    centerX = (firstPoint.x() + secondPoint.x()) * 0.5
    centerY = (firstPoint.y() + secondPoint.y()) * 0.5

    tempLinePoint2 = QgsPointXY(
        firstPoint.x() + 10 * math.sin(azimutO), firstPoint.y() + 10 * math.cos(azimutO))
    p3 = pointToLine2D(secondPoint.x(), secondPoint.y(), firstPoint.x(
    ), firstPoint.y(), tempLinePoint2.x(), tempLinePoint2.y())

    azP1 = normalizeAngle(lineAzimut2p(firstPoint, p1))
    azP3 = normalizeAngle(lineAzimut2p(firstPoint, p3))
    azimut100 = normalizeAngle(azimutO + math.pi * 0.5)

    if abs(azP3 - azimutO) <= 0.000001:
        if abs(azP1 - azimut100) <= 0.000001:
                # Cuadrante 2
            return [p1, firstPoint, p3, secondPoint]
        else:
            # Cuadrante 1
            return [firstPoint, p1, secondPoint, p3]
    else:
        if abs(azP1 - azimut100) <= 0.000001:
            # Cuadrante 3
            return [secondPoint, p3, firstPoint, p1]
        else:
            # Cuadrante 4
            return [p3, secondPoint, p1, firstPoint]


def rectangleHWCenterFrom2pCreate(firstPoint, secondPoint, rotation):

    templinePoint = getPolarPoint(secondPoint.x(), secondPoint.y(), rotation, 10)
    p1 = pointToLine2D(firstPoint.x(), firstPoint.y(), secondPoint.x(), secondPoint.y(), templinePoint[0], templinePoint[1])

    ax = p1.x()-secondPoint.x()
    ay = p1.y()-secondPoint.y()
    width = math.sqrt(ax**2 + ay**2)
    ax = p1.x()-firstPoint.x()
    ay = p1.y()-firstPoint.y()
    height = math.sqrt(ax**2 + ay**2)

    centerX = (firstPoint.x() + secondPoint.x()) * 0.5
    centerY = (firstPoint.y() + secondPoint.y()) * 0.5

    return {'center': [centerX, centerY], 'width': width, 'height': height, 'rotation': rotation}


def getPointsFromRectangleParams(rectParam):
    center = rectParam["center"]
    width = rectParam["width"]
    height = rectParam["height"]
    rotation = rectParam["rotation"]
    #       1       W       2
    #       +---------------+
    #       |               |
    #     H |               + AuxPto
    #       |               |
    #       +---------------+   ----------> rotation
    #       4       W       3
    auxPto = getPolarPoint(center[0], center[1], rotation, width * 0.5)
    p2 = getPolarPoint(auxPto[0], auxPto[1], rotation + math.pi * 0.5, height * 0.5)
    p1 = getPolarPoint(p2[0], p2[1], rotation + math.pi, width)
    p4 = getPolarPoint(p1[0], p1[1], rotation - math.pi * 0.5, height)
    p3 = getPolarPoint(p2[0], p2[1], rotation - math.pi * 0.5, height)
    return [p1, p2, p3, p4]


def pointToLine2D(px, py, x1, y1, x2, y2):
    try:
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / \
            ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        if False:
            if (u < 0):
                return [x1, y1]
            if (u > 1):
                return [x2, y2]
        return QgsPointXY(x1 + u * (x2 - x1), y1 + u * (y2 - y1))
    except ZeroDivisionError as err:
        print('POINT In LINE:', err)
        return QgsPointXY(px, py)


def lineAzimut2p(v1, v2):
    return math.atan2(v2.x() - v1.x(), v2.y() - v1.y())


def normalizeAngle(angle):
    maxValue = math.pi * 2
    if abs(angle) <= 0.000001:
        return 0
    if abs(angle - maxValue) <= 0.000001:
        return maxValue
    if (angle < 0):
        return angle % maxValue + maxValue
    if angle > maxValue:
        return angle % maxValue
    return angle


def getPolarPoint(x0, y0, angle, dist):
    x = x0 + dist * math.cos(angle)
    y = y0 + dist * math.sin(angle)
    return [x, y]
