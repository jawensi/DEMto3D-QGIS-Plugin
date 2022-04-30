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
import collections
import copy
import math
import struct
from builtins import range

from osgeo import gdal

from qgis.core import QgsCoordinateTransform, QgsPoint, QgsProject
from qgis.PyQt.QtCore import QThread, pyqtSignal


class Model(QThread):
    """Class where is built the mesh point that describe the surface model """
    pto = collections.namedtuple('pto', 'x y z')
    updateProgress = pyqtSignal()

    def __init__(self, parameters):
        QThread.__init__(self)
        self.parameters = parameters
        self.matrix_dem = []
        self.quit = False
        self.baseModel = self.parameters["baseModel"]

    def run(self):
        dem_dataset = gdal.Open(self.parameters["layer"])

        # self.matrix_dem = self.matrix_dem_builder(dem_dataset, self.parameters["height"], self.parameters["width"],
        #                                           self.parameters["scale"], self.parameters["spacing_mm"],
        #                                           self.parameters["roi_x_max"], self.parameters["roi_x_min"],
        #                                           self.parameters["roi_y_min"], self.parameters["z_base"],
        #                                           self.parameters["z_scale"], self.parameters["projected"])

        self.matrix_dem = self.matrix_dem_builder_interpolation(dem_dataset,
                                                                self.parameters["height"], self.parameters["width"],
                                                                self.parameters["scale"], self.parameters["scale_h"],
                                                                self.parameters["scale_w"],
                                                                self.parameters["spacing_mm"],
                                                                self.parameters["roi_x_max"],
                                                                self.parameters["roi_x_min"],
                                                                self.parameters["roi_y_min"],
                                                                self.parameters["z_base"],
                                                                self.parameters["z_scale"],
                                                                self.parameters["projected"])
        if self.parameters["z_inv"]:
            self.matrix_dem = self.matrix_dem_inverse_build(self.matrix_dem)
        dem_dataset = None

    def matrix_dem_builder(self, dem_dataset, height, width, scale, spacing_mm,
                           roi_x_max, roi_x_min, roi_y_min, h_base, z_scale, projected):

        # Calculate DEM parameters
        dem_col = dem_dataset.RasterXSize
        dem_row = dem_dataset.RasterYSize
        geotransform = dem_dataset.GetGeoTransform()
        dem_x_min = geotransform[0]
        dem_y_max = geotransform[3]
        dem_y_min = dem_y_max + dem_row * geotransform[5]
        dem_x_max = dem_x_min + dem_col * geotransform[1]

        rectParam = self.parameters["roi_rect_Param"]
        rotation = rectParam["rotation"]
        if not projected:
            spacing_deg = spacing_mm * rectParam["width"] / width

        row_stl = int(math.ceil(height / spacing_mm) + 1)
        col_stl = int(math.ceil(width / spacing_mm) + 1)
        matrix_dem = [list(range(col_stl)) for i in range(row_stl)]

        source = self.parameters["crs_map"]
        target = self.parameters["crs_layer"]
        if source != target:
            transform = QgsCoordinateTransform(
                source, target, QgsProject.instance())

        #  RECORRIDO
        #  0 ---------------------------> 1
        #    --------------------------->
        #  ^ --------------------------->
        #  | --------------------------->
        #  | --------------------------->
        #  X ---------------------------> 2
        var_y = height
        for i in range(row_stl):
            self.updateProgress.emit()
            var_x = 0
            for j in range(col_stl):
                # Model coordinate x(mm), y(mm)
                x_model = round(var_x, 2)
                y_model = round(var_y, 2)

                # Model maps geo_coordinates
                if projected:
                    x0, y0 = getPolarPoint(
                        roi_x_min, roi_y_min, rotation, x_model * scale / 1000)
                    x, y = getPolarPoint(
                        x0, y0, rotation + math.pi * 0.5, y_model * scale / 1000)
                else:
                    x0, y0 = getPolarPoint(
                        roi_x_min, roi_y_min, rotation, x_model * spacing_deg / spacing_mm)
                    x, y = getPolarPoint(
                        x0, y0, rotation + math.pi * 0.5, y_model * spacing_deg / spacing_mm)

                # Model layer geo_coordinates to query z value
                point = QgsPoint(x, y)
                if source != target:
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
                    z_model = self.baseModel
                elif self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0] <= h_base:
                    z_model = self.baseModel
                elif math.isnan(self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0]):
                    z_model = self.baseModel
                else:
                    z_model = round((self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[
                                    0] - h_base) / scale * 1000 * z_scale, 2) + self.baseModel

                matrix_dem[i][j] = self.pto(x=x_model, y=y_model, z=z_model)

                var_x += spacing_mm
                if var_x > width:
                    var_x = width
            var_y = spacing_mm * (row_stl - (i + 2))
            if self.quit:
                return 0
        return matrix_dem

    def matrix_dem_builder_interpolation(self, dem_dataset, height, width, scale, scale_h, scale_w, spacing_mm,
                                         roi_x_max, roi_x_min, roi_y_min, z_base, z_scale, projected):

        # Calculate DEM parameters
        columns = dem_dataset.RasterXSize
        rows = dem_dataset.RasterYSize
        geotransform = dem_dataset.GetGeoTransform()
        dem_x_min = geotransform[0]  # Limit pixel (not center)
        dem_y_max = geotransform[3]  # Limit pixel (not center)

        # dem_y_min = dem_y_max + rows * geotransform[5]
        # dem_x_max = dem_x_min + columns * geotransform[1]

        spacing_deg = 0
        rectParam = self.parameters["roi_rect_Param"]
        rotation = rectParam["rotation"]
        if not projected:
            spacing_deg = spacing_mm * rectParam["width"] / width

        row_stl = int(math.ceil(height / spacing_mm) + 1)
        col_stl = int(math.ceil(width / spacing_mm) + 1)
        matrix_dem = [list(range(col_stl)) for i in range(row_stl)]

        #  RECORRIDO
        #  0 ---------------------------> 1
        #    --------------------------->
        #  ^ --------------------------->
        #  | --------------------------->
        #  | --------------------------->
        #  X ---------------------------> 2

        var_y = height
        for i in range(row_stl):
            self.updateProgress.emit()

            var_x = 0
            for j in range(col_stl):
                # Model coordinate x(mm), y(mm)
                x_model = round(var_x, 2)
                y_model = round(var_y, 2)

                # Model maps geo_coordinates
                if projected:
                    x0, y0 = getPolarPoint(
                        roi_x_min, roi_y_min, rotation, x_model * scale / 1000)
                    x, y = getPolarPoint(
                        x0, y0, rotation + math.pi * 0.5, y_model * scale / 1000)
                else:
                    x0, y0 = getPolarPoint(
                        roi_x_min, roi_y_min, rotation, x_model * spacing_deg / spacing_mm)
                    x, y = getPolarPoint(
                        x0, y0, rotation + math.pi * 0.5, y_model * spacing_deg / spacing_mm)

                # print('punto cuajado (row - col - x - y)', i, j, x_model, y_model, round(x, 3), round(y, 3), sep=" - ")

                # Model layer geo_coordinates to query z value
                # point = QgsPoint(x, y)
                source = self.parameters["crs_map"]
                target = self.parameters["crs_layer"]
                if source != target:
                    transform = QgsCoordinateTransform(
                        source, target, QgsProject.instance())
                    point = transform.transform(x, y)
                    x = point.x()
                    y = point.y()

                # From x(m) get Column in DEM file
                col_dem = (x - dem_x_min) / geotransform[1]
                if col_dem >= columns:
                    col_dem -= 1
                elif col_dem < 0:
                    col_dem = 0
                # From y(m) get Row in DEM file
                row_dem = (y - dem_y_max) / geotransform[5]
                if row_dem >= rows:
                    row_dem -= 1
                elif row_dem < 0:
                    row_dem = 0
                # region nearest neighbours interpolation
                # row_dem = int(math.floor(row_dem))
                # col_dem = int(math.floor(col_dem))
                #
                # # Model coordinate z(mm)
                # if col_dem < 0 or row_dem < 0:
                #     z_model = self.baseModel
                # elif self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0] <= h_base:
                #     z_model = self.baseModel
                # elif math.isnan(self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0]):
                #     z_model = self.baseModel
                # else:
                #     z_model = round((self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0] - h_base) /
                #                     scale * 1000 * z_scale, 2) + self.baseModel
                #
                # matrix_dem[i][j] = self.pto(x=x_model, y=y_model, z=z_model)
                # endregion

                # region Lineal interpolation
                if 0 < col_dem < columns - 1 and 0 < row_dem < rows - 1:
                    min_col = int(math.floor(col_dem))
                    max_col = int(math.ceil(col_dem))
                    min_row = int(math.floor(row_dem))
                    max_row = int(math.ceil(row_dem))

                    # - From geographic coordinates calculate pixel coordinates
                    # - round up and down to see the 4 pixels neighbours integer

                    xP1 = dem_x_min + min_col * geotransform[1]
                    yP1 = dem_y_max + min_row * geotransform[5]
                    zP1 = self.get_z(min_col, min_row,
                                     dem_dataset, z_base, scale, z_scale)

                    xP2 = dem_x_min + max_col * geotransform[1]
                    yP2 = dem_y_max + min_row * geotransform[5]
                    zP2 = self.get_z(max_col, min_row,
                                     dem_dataset, z_base, scale, z_scale)

                    xP3 = dem_x_min + min_col * geotransform[1]
                    yP3 = dem_y_max + max_row * geotransform[5]
                    zP3 = self.get_z(min_col, max_row,
                                     dem_dataset, z_base, scale, z_scale)

                    xP4 = dem_x_min + max_col * geotransform[1]
                    yP4 = dem_y_max + max_row * geotransform[5]
                    zP4 = self.get_z(max_col, max_row,
                                     dem_dataset, z_base, scale, z_scale)

                    p = self.pto(x=x, y=y, z=0)
                    p1 = self.pto(x=xP1, y=yP1, z=zP1)
                    p2 = self.pto(x=xP2, y=yP2, z=zP2)
                    p3 = self.pto(x=xP3, y=yP3, z=zP3)
                    p4 = self.pto(x=xP4, y=yP4, z=zP4)

                    z_model = self.interp_line(p, p1, p2, p3, p4)
                    matrix_dem[i][j] = self.pto(
                        x=x_model, y=y_model, z=z_model)

                else:
                    # Solution for boundaries when col = 0 or col = Nº cols
                    # Manage Boundary limits:
                    if (isZero(col_dem) or col_dem >= columns - 1) and (isZero(row_dem) or row_dem >= rows - 1):
                        # Corners:
                        col_dem = int(col_dem)
                        row_dem = int(row_dem)
                        z_model = self.get_z(
                            col_dem, row_dem, dem_dataset, z_base, scale, z_scale)
                        matrix_dem[i][j] = self.pto(
                            x=x_model, y=y_model, z=z_model)

                    elif (isZero(col_dem) or col_dem >= columns - 1) and 0 < row_dem < rows - 1:
                        # First and last column
                        min_row = int(math.floor(row_dem))
                        max_row = int(math.ceil(row_dem))
                        col_dem = int(col_dem)

                        if min_row == max_row:
                            z_model = self.get_z(
                                col_dem, max_row, dem_dataset, z_base, scale, z_scale)
                            matrix_dem[i][j] = self.pto(
                                x=x_model, y=y_model, z=z_model)
                        else:
                            yP1 = dem_y_max + min_row * geotransform[5]
                            zP1 = self.get_z(
                                col_dem, min_row, dem_dataset, z_base, scale, z_scale)

                            yP2 = dem_y_max + max_row * geotransform[5]
                            zP2 = self.get_z(
                                col_dem, max_row, dem_dataset, z_base, scale, z_scale)

                            z_model = zP2 + \
                                math.fabs(yP2 - y) * (zP1 - zP2) / \
                                math.fabs(yP2 - yP1)
                            matrix_dem[i][j] = self.pto(
                                x=x_model, y=y_model, z=z_model)

                    elif 0 < col_dem < columns - 1 and (isZero(row_dem) or row_dem >= rows - 1):
                        # First and last row
                        min_col = int(math.floor(col_dem))
                        max_col = int(math.ceil(col_dem))
                        row_dem = int(row_dem)

                        if min_col == max_col:
                            z_model = self.get_z(
                                min_col, row_dem, dem_dataset, z_base, scale, z_scale)
                            matrix_dem[i][j] = self.pto(
                                x=x_model, y=y_model, z=z_model)
                        else:
                            xP1 = dem_x_min + min_col * geotransform[1]
                            zP1 = self.get_z(
                                min_col, row_dem, dem_dataset, z_base, scale, z_scale)

                            xP2 = dem_x_min + max_col * geotransform[1]
                            zP2 = self.get_z(
                                max_col, row_dem, dem_dataset, z_base, scale, z_scale)

                            z_model = zP1 + \
                                math.fabs(xP1 - x) * (zP2 - zP1) / \
                                math.fabs(xP2 - xP1)
                            matrix_dem[i][j] = self.pto(
                                x=x_model, y=y_model, z=z_model)
                    else:
                        print('punto cuajado', x_model, y_model, sep=" ")
                        matrix_dem[i][j] = self.pto(x=x_model, y=y_model, z=0)
                # endregion

                var_x += spacing_mm
                if var_x > width:
                    var_x = width
            var_y = spacing_mm * (row_stl - (i + 2))
            if self.quit:
                return 0

        return matrix_dem

    def get_z(self, col_dem, row_dem, dem_dataset, h_base, scale, z_scale):
        if col_dem < 0 or row_dem < 0:
            return self.baseModel
        else:
            z = self.get_dem_z(dem_dataset, col_dem, row_dem, 1, 1)[0]
            if z <= h_base:
                return self.baseModel
            elif math.isnan(z):
                return self.baseModel
            else:
                return round((z - h_base) / scale * 1000 * z_scale, 2) + self.baseModel

    def get_model(self):
        return self.matrix_dem

    @staticmethod
    def get_dem_z(dem_dataset, x_off, y_off, col_size, row_size):
        try:
            band = dem_dataset.GetRasterBand(1)
            data_types = {'Byte': 'B', 'UInt16': 'H', 'Int16': 'h',
                          'UInt32': 'I', 'Int32': 'i', 'Float32': 'f', 'Float64': 'd'}
            data_type = band.DataType
            data = band.ReadRaster(
                x_off, y_off, col_size, row_size, col_size, row_size, data_type)
            if data is None:
                return [0]
            else:
                return struct.unpack(data_types[gdal.GetDataTypeName(band.DataType)] * col_size * row_size, data)
        except struct.error:
            return [0]

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
            for j in (range(cols)):
                currcol = (cols - 1) - j
                new_z = z_max - getattr(matrix_dem_build[i][currcol], "z") + 2
                matrix_dem[i][j] = matrix_dem[i][j]._replace(z=new_z)
        return matrix_dem

    @staticmethod
    def interp_line(p, p1, p2, p3, p4):
        try:
            d1 = math.fabs(p2.x - p1.x)
            d2 = math.fabs(p1.y - p3.y)
            dif_z1 = p2.z - p1.z
            dif_z2 = p4.z - p3.z
            if isZero(d1) and isZero(d2) and isZero(p.x - p1.x):
                return p1.z
            if isZero(d1) and isZero(p.x - p1.x):
                return math.fabs(p.y - p3.y) * (p1.z - p3.z) / d2 + p3.z
            elif isZero(d2) and isZero(p1.y - p.y):
                return math.fabs(p.x - p1.x) * dif_z1 / d1 + p1.z
            else:
                zt = math.fabs(p.x - p1.x) * dif_z1 / d1 + p1.z
                zb = math.fabs(p.x - p1.x) * dif_z2 / d1 + p3.z
                return (p1.y - p.y) * (zb - zt) / d2 + zt
        except ZeroDivisionError as err:
            print('Bilineal interpolation error:', err)
            print('P', p.x, p.y, sep=" : ")
            print('P1', p1.x, p1.y, p1.z, sep=" : ")
            print('P2', p2.x, p2.y, p2.z, sep=" : ")
            print('P3', p3.x, p3.y, p3.z, sep=" : ")
            print('P4', p4.x, p4.y, p4.z, sep=" : ")
            print('dist', d1, d2, p.x - p1.x, p1.y - p.y, sep=" : ")
            return 0


def isZero(v):
    if v < 0.0:
        v = -v
    return v <= 0.0001


def getPolarPoint(x0, y0, angle, dist):
    x = x0 + dist * math.cos(angle)
    y = y0 + dist * math.sin(angle)
    return [x, y]
