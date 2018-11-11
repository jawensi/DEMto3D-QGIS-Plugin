# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AppONCE
                                 A QGIS plugin
 Creación de mapas en 3D
                              -------------------
        begin                : 2015-03-17
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Francisco Javier Venceslá Simón
        email                : jawensi@gmail.com
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
from PyQt4 import QtCore
import collections
import copy

from PyQt4.QtCore import QThread
from PyQt4.QtGui import QApplication
from qgis._core import QgsPoint, QgsCoordinateTransform
import math
from osgeo import gdal
import struct

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class Model(QThread):
    """Class where is built the mesh point that describe the surface model """
    pto = collections.namedtuple('pto', 'x y z')
    updateProgress = QtCore.pyqtSignal()

    def __init__(self, bar, label, button, parameters):
        QThread.__init__(self)
        self.bar = bar
        self.label = label
        self.button = button
        self.parameters = parameters
        self.matrix_dem = []

        self.quit = False
        QtCore.QObject.connect(self.button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.cancel)

    def run(self):
        row_stl = int(math.ceil(self.parameters["height"] / self.parameters["spacing_mm"]) + 1)
        self.bar.setMaximum(row_stl)
        self.bar.setValue(0)
        QApplication.processEvents()

        dem_dataset = gdal.Open(self.parameters["layer"])
        self.matrix_dem = self.matrix_dem_build(dem_dataset, self.parameters["height"], self.parameters["width"],
                                                self.parameters["scale"], self.parameters["spacing_mm"],
                                                self.parameters["roi_x_max"], self.parameters["roi_x_min"],
                                                self.parameters["roi_y_min"], self.parameters["z_base"],
                                                self.parameters["z_scale"], self.parameters["projected"])
        if self.parameters["z_inv"]:
            self.matrix_dem = self.matrix_dem_inverse_build(self.matrix_dem)
        dem_dataset = None

    def matrix_dem_build(self, dem_dataset, height, width, scale, spacing_mm,
                         roi_x_max, roi_x_min, roi_y_min, h_base, z_scale, projected):

        # Calculate DEM parameters
        dem_col = dem_dataset.RasterXSize
        dem_row = dem_dataset.RasterYSize
        geotransform = dem_dataset.GetGeoTransform()
        dem_x_min = geotransform[0]
        dem_y_max = geotransform[3]
        dem_y_min = dem_y_max + dem_row * geotransform[5]
        dem_x_max = dem_x_min + dem_col * geotransform[1]

        if not projected:
            spacing_deg = spacing_mm * (roi_x_max - roi_x_min) / width

        row_stl = int(math.ceil(height / spacing_mm) + 1)
        col_stl = int(math.ceil(width / spacing_mm) + 1)
        matrix_dem = [range(col_stl) for i in range(row_stl)]

        var_y = height
        for i in range(row_stl):
            self.updateProgress.emit()
            QApplication.processEvents()
            var_x = 0
            for j in range(col_stl):
                # Model coordinate x(mm), y(mm)
                x_model = round(var_x, 2)
                y_model = round(var_y, 2)

                # Model maps geo_coordinates
                if projected:
                    x = x_model * scale / 1000 + roi_x_min
                    y = y_model * scale / 1000 + roi_y_min
                else:
                    x = x_model * spacing_deg / spacing_mm + roi_x_min
                    y = y_model * spacing_deg / spacing_mm + roi_y_min

                # Model layer geo_coordinates to query z value
                point = QgsPoint(x, y)
                source = self.parameters["crs_map"]
                target = self.parameters["crs_layer"]
                if source != target:
                    transform = QgsCoordinateTransform(source, target)
                    point = transform.transform(point)
                    x = point.x()
                    y = point.y()

                # From x(m) get Column in DEM file
                col_dem = (x - dem_x_min) * dem_col / (dem_x_max - dem_x_min)
                col_dem = int(math.floor(col_dem))
                if col_dem == dem_col:
                    col_dem -= 1
                # From y(m) get Row in DEM file
                row_dem = (dem_y_max - y) * dem_row / (dem_y_max - dem_y_min)
                row_dem = int(math.floor(row_dem))
                if row_dem == dem_row:
                    row_dem -= 1

                # Model coordinate z(mm)
                if col_dem < 0 or row_dem < 0:
                    z_model = 2
                elif self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0] <= h_base:
                    z_model = 2
                elif math.isnan(self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0]):
                    z_model = 2
                else:
                    z_model = round((self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0] - h_base) /
                                    scale * 1000 * z_scale, 2) + 2

                matrix_dem[i][j] = self.pto(x=x_model, y=y_model, z=z_model)

                var_x += spacing_mm
                if var_x > width:
                    var_x = width
            var_y = spacing_mm * (row_stl - (i + 2))
            if self.quit:
                return 0
        return matrix_dem

    @staticmethod
    def matrix_dem_inverse_build(matrix_dem_build):
        rows = matrix_dem_build.__len__()
        cols = matrix_dem_build[0].__len__()

        matrix_dem = copy.deepcopy(matrix_dem_build)
        z_max = getattr(matrix_dem_build[0][0], "z")
        for i in range(rows):
            for j in range(cols):
                if getattr(matrix_dem_build[i][j], "z") > z_max:
                    z_max = getattr(matrix_dem_build[i][j], "z")
        for i in range(rows):
            for j in range(cols):
                new_z = z_max - getattr(matrix_dem_build[i][j], "z") + 2
                matrix_dem[i][j] = matrix_dem[i][j]._replace(z=new_z)
        return matrix_dem

    @staticmethod
    def get_dem_z(dem_dataset, x_off, y_off, col_size, row_size):
        try:
            band = dem_dataset.GetRasterBand(1)
            data_types = {'Byte': 'B', 'UInt16': 'H', 'Int16': 'h', 'UInt32': 'I', 'Int32': 'i', 'Float32': 'f',
                          'Float64': 'd'}
            data_type = band.DataType
            data = band.ReadRaster(x_off, y_off, col_size, row_size, col_size, row_size, data_type)
            data = struct.unpack(data_types[gdal.GetDataTypeName(band.DataType)] * col_size * row_size, data)
            return data
        except struct.error:
            return [0]

    def get_model(self):
        return self.matrix_dem

    def cancel(self):
        self.quit = True