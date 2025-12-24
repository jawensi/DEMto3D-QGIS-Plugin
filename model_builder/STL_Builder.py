# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2025 by Javier
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
from io import BufferedWriter
import math
import struct
from builtins import range, str
from typing import Any

import numpy as np
from qgis.PyQt.QtCore import QThread, pyqtSignal

from .utils import get_normal_np, point_on_arc

BINARY_HEADER = "80sI"
BINARY_FACET = "12fH"

base_normal: list[float] = [0, 0, -1]
bevel_segments: int = 15

#  self.matrix_dem
#     0,0 ---------------------------> 0,col
#         --------------------------->
#         --------------------------->
#         --------------------------->
#         --------------------------->
#  row, 0 +--------------------------> row, col

#  STL quads triangles
#     P3 ---------------+ P4
#        |-----------+--|
#        |--------+-----|
#        |-----+--------|
#        |--+-----------|
#     P1 +--------------- P2


class STL(QThread):
    """Class where is built the stl file from the mesh point that decribe the model surface"""

    normal = collections.namedtuple("normal", "normal_x normal_y normal_z")
    pto = collections.namedtuple("pto", "x y z")
    updateProgress = pyqtSignal()

    def __init__(self, parameters, stl_file, dem_matrix):
        QThread.__init__(self)
        self.parameters = parameters
        self.stl_file = stl_file
        self.matrix_dem: np.ndarray = dem_matrix
        self.quit = False

    def run(self):
        x_models = self.parameters["divideCols"]
        y_models = self.parameters["divideRow"]

        # if x_models == 1 and y_models == 1:
        #     path = self.stl_file
        #     self.write_binary_np(path, self.matrix_dem)
        # else:
        width_model = self.parameters["width"] / x_models
        high_model = self.parameters["height"] / y_models
        spacing = self.parameters["spacing_mm"]
        for i in range(y_models):
            for j in range(x_models):
                path = self.stl_file
                if y_models * x_models > 1:
                    path = self.stl_file.split(".")[0] + "_" + str(i) + str(j) + ".stl"
                xmin_model = width_model * j
                ymin_model = self.parameters["height"] - i * high_model - high_model
                xmax_model = width_model * j + width_model
                ymax_model = self.parameters["height"] - i * high_model
                # dem_model = self.divide_dem(self.matrix_dem, spacing, xmin_model, ymin_model, xmax_model, ymax_model)
                # self.write_binary(path, dem_model)
                dem_model = self.divide_dem_np(
                    self.matrix_dem,
                    spacing,
                    xmin_model,
                    ymin_model,
                    xmax_model,
                    ymax_model,
                )
                self.write_binary_np(path, dem_model)

    def write_ascii(self):
        f = open(self.stl_file, "w")
        f.write("solid model\n")

        dem = self.face_dem_vector(self.matrix_dem)
        for face in dem:
            self.updateProgress.emit()
            f.write("   facet normal 0 0 -1 " + "\n")
            f.write("       outer loop\n")
            f.write(
                "           vertex "
                + str(getattr(face[1], "x"))
                + " "
                + str(getattr(face[1], "y"))
                + " 0"
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[0], "x"))
                + " "
                + str(getattr(face[0], "y"))
                + " 0"
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[2], "x"))
                + " "
                + str(getattr(face[2], "y"))
                + " 0"
                + "\n"
            )
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        wall = self.face_wall_vector(self.matrix_dem)
        for face in wall:
            f.write(
                "   facet normal "
                + str(getattr(face[3], "normal_x"))
                + " "
                + str(getattr(face[3], "normal_y"))
                + " "
                + str(getattr(face[3], "normal_z"))
                + "\n"
            )
            f.write("       outer loop\n")
            f.write(
                "           vertex "
                + str(getattr(face[0], "x"))
                + " "
                + str(getattr(face[0], "y"))
                + " "
                + str(getattr(face[0], "z"))
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[1], "x"))
                + " "
                + str(getattr(face[1], "y"))
                + " "
                + str(getattr(face[1], "z"))
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[2], "x"))
                + " "
                + str(getattr(face[2], "y"))
                + " "
                + str(getattr(face[2], "z"))
                + "\n"
            )
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        for face in dem:
            self.updateProgress.emit()
            f.write(
                "   facet normal "
                + str(getattr(face[3], "normal_x"))
                + " "
                + str(getattr(face[3], "normal_y"))
                + " "
                + str(getattr(face[3], "normal_z"))
                + "\n"
            )
            f.write("       outer loop\n")
            f.write(
                "           vertex "
                + str(getattr(face[0], "x"))
                + " "
                + str(getattr(face[0], "y"))
                + " "
                + str(getattr(face[0], "z"))
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[1], "x"))
                + " "
                + str(getattr(face[1], "y"))
                + " "
                + str(getattr(face[1], "z"))
                + "\n"
            )
            f.write(
                "           vertex "
                + str(getattr(face[2], "x"))
                + " "
                + str(getattr(face[2], "y"))
                + " "
                + str(getattr(face[2], "z"))
                + "\n"
            )
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        f.write("endsolid model\n")
        f.close()

    def write_binary(self, fileName: str, demData: list[list[pto]]):
        try:
            counter = 0
            stream = open(fileName, "wb")
            stream.seek(0)
            stream.write(
                struct.pack(BINARY_HEADER, b"Python Binary STL Writer", counter)
            )

            dem = self.face_dem_vector(demData)
            for face in dem:
                self.updateProgress.emit()
                counter += 1
                data = [
                    0,
                    0,
                    -1,
                    getattr(face[1], "x"),
                    getattr(face[1], "y"),
                    0,
                    getattr(face[0], "x"),
                    getattr(face[0], "y"),
                    0,
                    getattr(face[2], "x"),
                    getattr(face[2], "y"),
                    0,
                    0,
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            wall = self.face_wall_vector(demData)
            for face in wall:
                counter += 1
                data = [
                    getattr(face[3], "normal_x"),
                    getattr(face[3], "normal_y"),
                    getattr(face[3], "normal_z"),
                    getattr(face[0], "x"),
                    getattr(face[0], "y"),
                    getattr(face[0], "z"),
                    getattr(face[1], "x"),
                    getattr(face[1], "y"),
                    getattr(face[1], "z"),
                    getattr(face[2], "x"),
                    getattr(face[2], "y"),
                    getattr(face[2], "z"),
                    0,
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            for face in dem:
                self.updateProgress.emit()
                counter += 1
                data = [
                    getattr(face[3], "normal_x"),
                    getattr(face[3], "normal_y"),
                    getattr(face[3], "normal_z"),
                    getattr(face[0], "x"),
                    getattr(face[0], "y"),
                    getattr(face[0], "z"),
                    getattr(face[1], "x"),
                    getattr(face[1], "y"),
                    getattr(face[1], "z"),
                    getattr(face[2], "x"),
                    getattr(face[2], "y"),
                    getattr(face[2], "z"),
                    0,
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            stream.seek(0)
            stream.write(
                struct.pack(BINARY_HEADER, b"Python Binary STL Writer", counter)
            )
            stream.close()
        except:
            stream.close()

    def face_wall_vector(self, matrix_dem: list[list[pto]]):
        borders = self.parameters["borders"]
        hasBorders = borders > 0
        if hasBorders:
            return self.face_wall_borders_vector(matrix_dem)
        else:
            return self.face_wall_No_borders_vector(matrix_dem)

    def face_wall_No_borders_vector(self, matrix_dem: list[list[pto]]):
        rows = matrix_dem.__len__()
        cols = matrix_dem[0].__len__()
        vector_face = []
        d = 0
        for j in range(rows - 1):
            p1 = matrix_dem[j][0]
            p1 = p1._replace(z=d)
            p2 = matrix_dem[j + 1][0]
            p3 = matrix_dem[j][0]
            p4 = matrix_dem[j + 1][0]
            p4 = p4._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=-1, normal_z=0)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p1, p4, p2, v_normal])

            p1 = matrix_dem[j][cols - 1]
            p2 = matrix_dem[j + 1][cols - 1]
            p3 = matrix_dem[j][cols - 1]
            p3 = p3._replace(z=d)
            p4 = matrix_dem[j + 1][cols - 1]
            p4 = p4._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=1, normal_z=0)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p2, p4, p3, v_normal])
        for j in range(cols - 1):
            p3 = matrix_dem[0][j]
            p3 = p3._replace(z=d)
            p2 = matrix_dem[0][j + 1]
            p1 = matrix_dem[0][j]
            p4 = matrix_dem[0][j + 1]
            p4 = p4._replace(z=d)
            v_normal = self.normal(normal_x=-1, normal_y=0, normal_z=0)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p2, p4, p3, v_normal])
            p1 = matrix_dem[rows - 1][j]
            p1 = p1._replace(z=d)
            p2 = matrix_dem[rows - 1][j + 1]
            p3 = matrix_dem[rows - 1][j]
            p4 = matrix_dem[rows - 1][j + 1]
            p4 = p4._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=1, normal_z=0)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p1, p4, p2, v_normal])
        return vector_face

    def face_wall_borders_vector(self, matrix_dem: list[list[pto]]):
        borders = self.parameters["borders"]
        rows = matrix_dem.__len__()
        cols = matrix_dem[0].__len__()
        vector_face = []
        d = 0

        # UPPER RIGHT CORNER
        p0 = matrix_dem[0][cols - 1]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x + borders, y=p0y + borders, z=d)
        p3 = self.pto(x=p0x, y=p0y + borders, z=d)
        p4 = self.pto(x=p0x + borders, y=p0y, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # UPPER LEFT CORNER
        p0 = matrix_dem[0][0]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x - borders, y=p0y + borders, z=d)
        p3 = self.pto(x=p0x - borders, y=p0y, z=d)
        p4 = self.pto(x=p0x, y=p0y + borders, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # BOTTOM LEFT CORNER
        p0 = matrix_dem[rows - 1][0]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x - borders, y=p0y - borders, z=d)
        p3 = self.pto(x=p0x, y=p0y - borders, z=d)
        p4 = self.pto(x=p0x - borders, y=p0y, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # BOTTOM RIGHT CORNER
        p0 = matrix_dem[rows - 1][cols - 1]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x + borders, y=p0y - borders, z=d)
        p3 = self.pto(x=p0x + borders, y=p0y, z=d)
        p4 = self.pto(x=p0x, y=p0y - borders, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # LEFT & RIGHT BORDERS
        for j in range(rows - 1):
            p3 = matrix_dem[j][0]
            p2 = matrix_dem[j + 1][0]
            p1 = p3._replace(z=d, x=getattr(p3, "x") - borders)
            p4 = p2._replace(z=d, x=getattr(p2, "x") - borders)
            v_normal = self.get_normal(p1, p2, p3)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p1, p4, p2, v_normal])
            p2 = p2._replace(z=d)
            p3 = p3._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
            vector_face.append([p1, p3, p2, v_normal])
            vector_face.append([p1, p2, p4, v_normal])

            p1 = matrix_dem[j][cols - 1]
            p2 = matrix_dem[j + 1][cols - 1]
            p3 = p1._replace(z=d, x=getattr(p1, "x") + borders)
            p4 = p2._replace(z=d, x=getattr(p2, "x") + borders)
            v_normal = self.get_normal(p1, p2, p3)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p2, p4, p3, v_normal])
            p1 = p1._replace(z=d)
            p2 = p2._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
            vector_face.append([p1, p3, p2, v_normal])
            vector_face.append([p2, p3, p4, v_normal])

        # UPPER & BOTTOM BORDERS
        for j in range(cols - 1):
            p1 = matrix_dem[0][j]
            p2 = matrix_dem[0][j + 1]
            p3 = p1._replace(z=d, y=getattr(p1, "y") + borders)
            p4 = p2._replace(z=d, y=getattr(p2, "y") + borders)
            v_normal = self.get_normal(p1, p2, p3)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p2, p4, p3, v_normal])
            p1 = p1._replace(z=d)
            p2 = p2._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
            vector_face.append([p1, p3, p2, v_normal])
            vector_face.append([p2, p3, p4, v_normal])

            p2 = matrix_dem[rows - 1][j + 1]
            p3 = matrix_dem[rows - 1][j]
            p1 = p3._replace(z=d, y=getattr(p3, "y") - borders)
            p4 = p2._replace(z=d, y=getattr(p2, "y") - borders)
            v_normal = self.get_normal(p1, p2, p3)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p1, p4, p2, v_normal])
            p2 = p2._replace(z=d)
            p3 = p3._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
            vector_face.append([p1, p3, p2, v_normal])
            vector_face.append([p1, p2, p4, v_normal])
        return vector_face

    def face_dem_vector(self, matrix_dem: list[list[pto]]):
        rows = matrix_dem.__len__()
        cols = matrix_dem[0].__len__()
        vector_face = []
        for j in range(rows - 1):
            for k in range(cols - 1):
                p3 = matrix_dem[j][k]
                p2 = matrix_dem[j][k + 1]
                p1 = matrix_dem[j + 1][k]
                p4 = matrix_dem[j + 1][k + 1]
                normal = self.get_normal(p1, p2, p3)
                vector_face.append([p1, p2, p3, normal])
                normal = self.get_normal(p1, p4, p2)
                vector_face.append([p1, p4, p2, normal])
        return vector_face

    def get_normal(self, p1, p2, p3):
        try:
            v = [
                getattr(p2, "x") - getattr(p1, "x"),
                getattr(p2, "y") - getattr(p1, "y"),
                getattr(p2, "z") - getattr(p1, "z"),
            ]
            w = [
                getattr(p3, "x") - getattr(p1, "x"),
                getattr(p3, "y") - getattr(p1, "y"),
                getattr(p3, "z") - getattr(p1, "z"),
            ]

            x = (v[1] * w[2]) - (v[2] * w[1])
            y = (v[2] * w[0]) - (v[0] * w[2])
            z = (v[0] * w[1]) - (v[1] * w[0])
            modulo = math.sqrt(x * x + y * y + z * z)

            v_normal = self.normal(
                normal_x=x / modulo, normal_y=y / modulo, normal_z=z / modulo
            )
            return v_normal
        except ZeroDivisionError:
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=0)
        return v_normal

    def divide_dem(
        self, matrix_dem_build: np.ndarray, resolution, x_min, y_min, x_max, y_max
    ):
        rows, cols = matrix_dem_build.shape[:2]
        rowIndex = 0
        colIndex = 0
        dem = []
        for i in range(rows):
            aux = []
            for j in range(cols):
                isValid = False
                x = matrix_dem_build[i, j, 0]
                y = matrix_dem_build[i, j, 1]
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    pto = self.pto(x=x, y=y, z=matrix_dem_build[i, j, 2])
                    aux.append(pto)
                    isValid = True
                elif 0 < (x - x_max) < resolution and y_min <= y <= y_max:
                    pto = self.pto(x=x, y=y, z=matrix_dem_build[i, j, 2])
                    aux.append(pto)
                    isValid = True
                elif -resolution < (y - y_min) < 0 and x_min <= x <= x_max:
                    pto = self.pto(x=x, y=y, z=matrix_dem_build[i, j, 2])
                    aux.append(pto)
                    isValid = True
                elif 0 < (x - x_max) < resolution and -resolution < (y - y_min) < 0:
                    pto = self.pto(x=x, y=y, z=matrix_dem_build[i, j, 2])
                    aux.append(pto)
                    isValid = True
                if isValid:
                    rowIndex = i if rowIndex < i else rowIndex

            if aux:
                dem.append(aux)
        return dem

    # ----------------- numPy methods -----------------

    @staticmethod
    def divide_dem_np(
        matrix_dem_build: np.ndarray, resolution, x_min, y_min, x_max, y_max
    ):
        # Obtener las coordenadas x e y de la matriz DEM
        x_coords = matrix_dem_build[:, :, 0]
        y_coords = matrix_dem_build[:, :, 1]

        # Crear máscaras booleanas para cada condición
        isInArea_mask = (
            (x_coords >= x_min)
            & (x_coords <= x_max)
            & (y_coords >= y_min)
            & (y_coords <= y_max)
        )
        isRightBorder_mask = (
            (0 < (x_coords - x_max))
            & ((x_coords - x_max) < resolution)
            & (y_coords >= y_min)
            & (y_coords <= y_max)
        )
        isDownBorder_mask = (
            (-resolution < (y_coords - y_min))
            & ((y_coords - y_min) < 0)
            & (x_coords >= x_min)
            & (x_coords <= x_max)
        )
        isCorner_mask = (
            (resolution > (x_coords - x_max))
            & ((x_coords - x_max) > 0)
            & (resolution > (y_coords - y_min))
            & ((y_coords - y_min) > -resolution)
        )

        # Combinar las máscaras utilizando operadores lógicos
        combined_mask = (
            isInArea_mask | isRightBorder_mask | isDownBorder_mask | isCorner_mask
        )
        # Encontrar los índices de fila y columna donde la máscara es True
        row_indices, col_indices = np.where(combined_mask)
        # Obtener los índices mínimo y máximo de fila y columna
        rowIndex0, rowIndexN = row_indices.min(), row_indices.max()
        colIndex0, colIndexN = col_indices.min(), col_indices.max()
        return matrix_dem_build[rowIndex0 : rowIndexN + 1, colIndex0 : colIndexN + 1]

        # rows, cols = matrix_dem_build.shape[:2]
        # rowIndex0 = None
        # rowIndexN = 0
        # colIndex0 = None
        # colIndexN = 0
        # for i in range(rows):
        #     for j in range(cols):
        #         x = matrix_dem_build[i, j, 0]
        #         y = matrix_dem_build[i, j, 1]
        #
        #         isInArea = x_min <= x <= x_max and y_min <= y <= y_max
        #         isRigthBorder = 0 < (x - x_max) < resolution and y_min <= y <= y_max
        #         isDownBorder = -resolution < (y - y_min) < 0 and x_min <= x <= x_max
        #         isCorner = resolution > (x - x_max) > 0 > (y - y_min) > - resolution
        #
        #         if isInArea or isRigthBorder or isDownBorder or isCorner:
        #             if rowIndex0 is None:
        #                 rowIndex0 = i
        #             if rowIndexN < i:
        #                 rowIndexN = i
        #             if colIndex0 is None:
        #                 colIndex0 = j
        #             if colIndexN < j:
        #                 colIndexN = j
        # return matrix_dem_build[rowIndex0:rowIndexN + 1, colIndex0:colIndexN + 1]

    def write_binary_np(self, fileName: str, demData: np.ndarray):
        stream = open(fileName, "wb")
        try:
            counter = 0
            stream.seek(0)
            stream.write(
                struct.pack(BINARY_HEADER, b"Python Binary STL Writer", counter)
            )

            counter += self.write_face_dem_np(demData, stream)
            has_borders = self.parameters["has_borders"]
            if has_borders:
                counter += self.write_face_base_np(demData, stream)
                counter += self.write_face_wall_np(demData, stream)

            stream.seek(0)
            stream.write(
                struct.pack(BINARY_HEADER, b"Python Binary STL Writer", counter)
            )
            stream.close()
        except:
            stream.close()    

    def writeStlBaseFace(self, stream, p1, p2, p3):
        self.updateProgress.emit()
        data = [0, 0, -1, p2[0], p2[1], 0, p1[0], p1[1], 0, p3[0], p3[1], 0, 0]
        stream.write(struct.pack(BINARY_FACET, *data))
        if self.quit:
            stream.close()
            return 0

    def write_face_base_np(self, matrix_dem: np.ndarray, stream: BufferedWriter):
        rows, cols = matrix_dem.shape[:2]
        min_x = matrix_dem[0, 0, 0]
        min_y = matrix_dem[0, 0, 1]
        max_x = matrix_dem[rows - 1, cols - 1, 0]
        max_y = matrix_dem[rows - 1, cols - 1, 1]
        mean_pto = [(max_x + min_x) * 0.5, (max_y + min_y) * 0.5, 0]
        count = 0
        for j in range(rows - 1):
            p1 = matrix_dem[j, 0]
            p2 = matrix_dem[j + 1, 0]
            self.writeStlBaseFace(stream, p1, p2, mean_pto)
            count += 1
            p1 = matrix_dem[j, cols - 1]
            p2 = matrix_dem[j + 1, cols - 1]
            self.writeStlBaseFace(stream, p2, p1, mean_pto)
            count += 1
        for j in range(cols - 1):
            p1 = matrix_dem[0, j]
            p2 = matrix_dem[0, j + 1]
            self.writeStlBaseFace(stream, p2, p1, mean_pto)
            count += 1
            p1 = matrix_dem[rows - 1, j]
            p2 = matrix_dem[rows - 1, j + 1]
            self.writeStlBaseFace(stream, p1, p2, mean_pto)
            count += 1
        return count

    ####################################################

    def writeStlFace(self, stream: BufferedWriter, p1: list[float], p2: list[float], p3: list[float], normal: list[float]):
        self.updateProgress.emit()
        data = [
            normal[0],
            normal[1],
            normal[2],
            p1[0],
            p1[1],
            p1[2],
            p2[0],
            p2[1],
            p2[2],
            p3[0],
            p3[1],
            p3[2],
            0,
        ]
        stream.write(struct.pack(BINARY_FACET, *data))
        if self.quit:
            stream.close()
            return 0

    def write_face_dem_np(self, matrix_dem: np.ndarray, stream: BufferedWriter):
        rows, cols = matrix_dem.shape[:2]
        count = 0
        for j in range(rows - 1):
            for k in range(cols - 1):
                p3 = matrix_dem[j, k]
                p2 = matrix_dem[j, k + 1]
                p1 = matrix_dem[j + 1, k]
                p4 = matrix_dem[j + 1, k + 1]
                normal1 = get_normal_np(p1, p2, p3)
                self.writeStlFace(stream, p1, p2, p3, normal1)
                normal2 = get_normal_np(p1, p4, p2)
                self.writeStlFace(stream, p1, p4, p2, normal2)
                count += 2
        return count

    ####################################################

    def write_face_wall_np(self, matrix_dem: np.ndarray, stream: BufferedWriter):
        borders = self.parameters["borders"]
        hasBorders = borders > 0
        if hasBorders:
            return self.write_face_wall_borders_np(matrix_dem, stream)
        else:
            return self.write_face_wall_No_borders_np(matrix_dem, stream)

    def write_face_wall_No_borders_np(self, matrix_dem: np.ndarray, stream: BufferedWriter):
        rows, cols = matrix_dem.shape[:2]
        count = 0   
        d = 0
        v_normal_y_neg: list[float] = [0, -1, 0]
        v_normal_y_pos: list[float] = [0, 1, 0]
        v_normal_x_neg: list[float] = [-1, 0, 0]
        for j in range(rows - 1):
            p1 = [matrix_dem[j, 0, 0], matrix_dem[j, 0, 1], 0]
            p2 = matrix_dem[j + 1, 0]
            p3 = matrix_dem[j, 0]
            p4 = [matrix_dem[j + 1, 0, 0], matrix_dem[j + 1, 0, 1], d]
            self.writeStlFace(stream, p1, p2, p3, v_normal_y_neg)
            self.writeStlFace(stream, p1, p4, p2, v_normal_y_neg)
            count += 2

            p1 = matrix_dem[j, cols - 1]
            p2 = matrix_dem[j + 1, cols - 1]
            p3 = [matrix_dem[j, cols - 1, 0], matrix_dem[j, cols - 1, 1], d]
            p4 = [matrix_dem[j + 1, cols - 1, 0], matrix_dem[j + 1, cols - 1, 1], d]
            self.writeStlFace(stream, p1, p2, p3, v_normal_y_pos)
            self.writeStlFace(stream, p2, p4, p3, v_normal_y_pos)
            count += 2

        for j in range(cols - 1):
            p3 = [matrix_dem[0, j, 0], matrix_dem[0, j, 1], d]
            p2 = matrix_dem[0, j + 1]
            p1 = matrix_dem[0, j]
            p4 = [matrix_dem[0, j + 1, 0], matrix_dem[0, j + 1, 1], d]
            self.writeStlFace(stream, p1, p2, p3, v_normal_x_neg)
            self.writeStlFace(stream, p2, p4, p3, v_normal_x_neg)
            count += 2

            p1 = [matrix_dem[rows - 1, j, 0], matrix_dem[rows - 1, j, 1], d]
            p2 = matrix_dem[rows - 1, j + 1]
            p3 = matrix_dem[rows - 1, j]
            p4 = [matrix_dem[rows - 1, j + 1, 0], matrix_dem[rows - 1, j + 1, 1], d]
            self.writeStlFace(stream, p1, p2, p3, v_normal_y_pos)
            self.writeStlFace(stream, p1, p4, p2, v_normal_y_pos)
            count += 2

        return count

    def write_face_wall_borders_np(self, matrix_dem: np.ndarray, stream: BufferedWriter):
        borders = self.parameters["borders"]
        rows, cols = matrix_dem.shape[:2]
        count = 0
        bevel = True

        if bevel:
            p0 = matrix_dem[0, cols - 1]
            count += self.writeUpperRightCornerBevel(p0, stream, borders)
            p0 = matrix_dem[0, 0]
            count += self.writeUpperLeftCornerBevel(p0, stream, borders)
            p0 = matrix_dem[rows - 1, 0]
            count += self.writeBottomLeftCornerBevel(p0, stream, borders)
            p0 = matrix_dem[rows - 1, cols - 1]
            count += self.writeBottomRightCornerBevel(p0, stream, borders)
        else:
            p0 = matrix_dem[0, cols - 1]
            count += self.writeUpperRightCorner(p0, stream, borders)
            p0 = matrix_dem[0, 0]
            count += self.writeUpperLeftCorner(p0, stream, borders)
            p0 = matrix_dem[rows - 1, 0]
            count += self.writeBottomLeftCorner(p0, stream, borders)
            p0 = matrix_dem[rows - 1, cols - 1]
            count += self.writeBottomRightCorner(p0, stream, borders)

        # LEFT & RIGHT BORDERS
        for j in range(rows - 1):
            p3 = [matrix_dem[j, 0, 0], matrix_dem[j, 0, 1], matrix_dem[j, 0, 2]]
            p2 = [
                matrix_dem[j + 1, 0, 0],
                matrix_dem[j + 1, 0, 1],
                matrix_dem[j + 1, 0, 2],
            ]
            p1 = [p3[0] - borders, p3[1], 0]
            p4 = [p2[0] - borders, p2[1], 0]
            v_normal = get_normal_np(p1, p2, p3)
            self.writeStlFace(stream, p1, p2, p3, v_normal)
            self.writeStlFace(stream, p1, p4, p2, v_normal)
            p2[2] = 0
            p3[2] = 0
            self.writeStlFace(stream, p1, p3, p2, base_normal)
            self.writeStlFace(stream, p1, p2, p4, base_normal)
            count += 4

            p1 = [
                matrix_dem[j, cols - 1, 0],
                matrix_dem[j, cols - 1, 1],
                matrix_dem[j, cols - 1, 2],
            ]
            p2 = [
                matrix_dem[j + 1, cols - 1, 0],
                matrix_dem[j + 1, cols - 1, 1],
                matrix_dem[j + 1, cols - 1, 2],
            ]
            p3 = [p1[0] + borders, p1[1], 0]
            p4 = [p2[0] + borders, p2[1], 0]
            v_normal = get_normal_np(p1, p2, p3)
            self.writeStlFace(stream, p1, p2, p3, v_normal)
            self.writeStlFace(stream, p2, p4, p3, v_normal)
            p1[2] = 0
            p2[2] = 0
            self.writeStlFace(stream, p1, p3, p2, base_normal)
            self.writeStlFace(stream, p2, p3, p4, base_normal)
            count += 4

        # UPPER & BOTTOM BORDERS
        for j in range(cols - 1):
            p1 = [matrix_dem[0, j, 0], matrix_dem[0, j, 1], matrix_dem[0, j, 2]]
            p2 = [
                matrix_dem[0, j + 1, 0],
                matrix_dem[0, j + 1, 1],
                matrix_dem[0, j + 1, 2],
            ]
            p3 = [p1[0], p1[1] + borders, 0]
            p4 = [p2[0], p2[1] + borders, 0]
            v_normal = get_normal_np(p1, p2, p3)
            self.writeStlFace(stream, p1, p2, p3, v_normal)
            self.writeStlFace(stream, p2, p4, p3, v_normal)
            p1[2] = 0
            p2[2] = 0
            self.writeStlFace(stream, p1, p3, p2, base_normal)
            self.writeStlFace(stream, p2, p3, p4, base_normal)
            count += 4

            p2 = [
                matrix_dem[rows - 1, j + 1, 0],
                matrix_dem[rows - 1, j + 1, 1],
                matrix_dem[rows - 1, j + 1, 2],
            ]
            p3 = [
                matrix_dem[rows - 1, j, 0],
                matrix_dem[rows - 1, j, 1],
                matrix_dem[rows - 1, j, 2],
            ]
            p1 = [p3[0], p3[1] - borders, 0]
            p4 = [p2[0], p2[1] - borders, 0]
            v_normal = get_normal_np(p1, p2, p3)
            self.writeStlFace(stream, p1, p2, p3, v_normal)
            self.writeStlFace(stream, p1, p4, p2, v_normal)
            p2[2] = 0
            p3[2] = 0
            self.writeStlFace(stream, p1, p3, p2, base_normal)
            self.writeStlFace(stream, p1, p2, p4, base_normal)
            count += 4

        return count

    def writeUpperRightCornerBevel(self, p0, stream, borders):
        count = 0        
        p1 = [p0[0], p0[1], p0[2]]
        p3 = [p0[0], p0[1] + borders, 0]
        p4 = [p0[0] + borders, p0[1], 0]

        offset = 5.0  # if 5.0 < borders else borders * 0.7
        center = [p0[0] + borders - offset, p0[1] + borders - offset, 0]
        radius = offset
        theta_start = np.pi / 2
        theta_end = 0

        arc_points: list[list[float]] = [p3]
        for i in range(bevel_segments + 1):
            theta = theta_start + (theta_end - theta_start) * i / bevel_segments
            arc_points.append(point_on_arc(center, radius, theta))
        arc_points.append(p4)

        # Triangula el arco con p1
        for i in range(bevel_segments + 2):
            v_normal = get_normal_np(p1, arc_points[i], arc_points[i + 1])
            self.writeStlFace(stream, p1, arc_points[i + 1], arc_points[i], v_normal)
            count += 1
        # Base faces (opcional, igual que antes)
        p1_base = [p0[0], p0[1], 0]
        for i in range(bevel_segments + 2):
            self.writeStlFace(
                stream, p1_base, arc_points[i], arc_points[i + 1], base_normal
            )
            count += 1
        return count

    def writeUpperLeftCornerBevel(self, p0, stream, borders):
        count = 0
        p1 = [p0[0], p0[1], p0[2]]
        p3 = [p0[0] - borders, p0[1], 0]
        p4 = [p0[0], p0[1] + borders, 0]

        offset = 5.0  # if 5.0 < borders else borders * 0.7
        center = [p0[0] - borders + offset, p0[1] + borders - offset, 0]
        radius = offset
        theta_start = np.pi
        theta_end = np.pi / 2

        arc_points: list[list[float]] = [p3]
        for i in range(bevel_segments + 1):
            theta = theta_start + (theta_end - theta_start) * i / bevel_segments
            arc_points.append(point_on_arc(center, radius, theta))
        arc_points.append(p4)

        # Triangula el arco con p1
        for i in range(bevel_segments + 2):
            v_normal = get_normal_np(p1, arc_points[i], arc_points[i + 1])
            self.writeStlFace(stream, p1, arc_points[i + 1], arc_points[i], v_normal)
            count += 1
        # Base faces (opcional, igual que antes)
        p1_base = [p0[0], p0[1], 0]
        for i in range(bevel_segments + 2):
            self.writeStlFace(
                stream, p1_base, arc_points[i], arc_points[i + 1], base_normal
            )
            count += 1
        return count

    def writeBottomLeftCornerBevel(self, p0, stream, borders):
        count = 0           
        p1 = [p0[0], p0[1], p0[2]]
        p3 = [p0[0], p0[1] - borders, 0]
        p4 = [p0[0] - borders, p0[1], 0]

        offset = 5  #  if 5.0 < borders else borders * 0.7
        center = [p0[0] - borders + offset, p0[1] - borders + offset, 0]
        radius = offset
        theta_start = 3 * np.pi / 2
        theta_end = np.pi

        arc_points: list[list[float]] = [p3]
        for i in range(bevel_segments + 1):
            theta = theta_start + (theta_end - theta_start) * i / bevel_segments
            arc_points.append(point_on_arc(center, radius, theta))
        arc_points.append(p4)

        # Triangula el arco con p1
        for i in range(bevel_segments + 2):
            v_normal = get_normal_np(p1, arc_points[i], arc_points[i + 1])
            self.writeStlFace(stream, p1, arc_points[i + 1], arc_points[i], v_normal)
            count += 1
        # Base faces (opcional, igual que antes)
        p1_base = [p0[0], p0[1], 0]
        for i in range(bevel_segments + 2):
            self.writeStlFace(
                stream, p1_base, arc_points[i], arc_points[i + 1], base_normal
            )
            count += 1
        return count

    def writeBottomRightCornerBevel(self, p0, stream, borders):
        count = 0        
        p1 = [p0[0], p0[1], p0[2]]
        p3 = [p0[0] + borders, p0[1], 0]
        p4 = [p0[0], p0[1] - borders, 0]

        offset = 5.0  # if 5.0 < borders else borders * 0.7
        center = [p0[0] + borders - offset, p0[1] - borders + offset, 0]
        radius = offset
        theta_start = 0
        theta_end = -np.pi / 2

        arc_points: list[list[float]] = [p3]
        for i in range(bevel_segments + 1):
            theta = theta_start + (theta_end - theta_start) * i / bevel_segments
            arc_points.append(point_on_arc(center, radius, theta))
        arc_points.append(p4)

        # Triangula el arco con p1
        for i in range(bevel_segments + 2):
            v_normal = get_normal_np(p1, arc_points[i], arc_points[i + 1])
            self.writeStlFace(stream, p1, arc_points[i + 1], arc_points[i], v_normal)
            count += 1
        # Base faces (opcional, igual que antes)
        p1_base = [p0[0], p0[1], 0]
        for i in range(bevel_segments + 2):
            self.writeStlFace(
                stream, p1_base, arc_points[i], arc_points[i + 1], base_normal
            )
            count += 1
        return count

    def writeUpperRightCorner(self, p0, stream, borders):
        p1 = [p0[0], p0[1], p0[2]]
        p2 = [p0[0] + borders, p0[1] + borders, 0]
        p3 = [p0[0], p0[1] + borders, 0]
        p4 = [p0[0] + borders, p0[1], 0]
        v_normal = get_normal_np(p1, p2, p3)
        self.writeStlFace(stream, p1, p2, p3, v_normal)
        v_normal = get_normal_np(p1, p4, p2)
        self.writeStlFace(stream, p1, p4, p2, v_normal)
        p1[2] = 0
        self.writeStlFace(stream, p1, p3, p2, base_normal)
        self.writeStlFace(stream, p1, p2, p4, base_normal)
        return 4

    def writeUpperLeftCorner(self, p0, stream, borders):        
        p1 = [p0[0], p0[1], p0[2]]
        p2 = [p0[0] - borders, p0[1] + borders, 0]
        p3 = [p0[0] - borders, p0[1], 0]
        p4 = [p0[0], p0[1] + borders, 0]
        v_normal = get_normal_np(p1, p2, p3)
        self.writeStlFace(stream, p1, p2, p3, v_normal)
        v_normal = get_normal_np(p1, p4, p2)
        self.writeStlFace(stream, p1, p4, p2, v_normal)
        p1[2] = 0
        self.writeStlFace(stream, p1, p3, p2, base_normal)
        self.writeStlFace(stream, p1, p2, p4, base_normal)
        return 4

    def writeBottomLeftCorner(self, p0, stream, borders):        
        p1 = [p0[0], p0[1], p0[2]]
        p2 = [p0[0] - borders, p0[1] - borders, 0]
        p3 = [p0[0], p0[1] - borders, 0]
        p4 = [p0[0] - borders, p0[1], 0]
        v_normal = get_normal_np(p1, p2, p3)
        self.writeStlFace(stream, p1, p2, p3, v_normal)
        v_normal = get_normal_np(p1, p4, p2)
        self.writeStlFace(stream, p1, p4, p2, v_normal)
        p1[2] = 0
        self.writeStlFace(stream, p1, p3, p2, base_normal)
        self.writeStlFace(stream, p1, p2, p4, base_normal)
        return 4

    def writeBottomRightCorner(self, p0, stream, borders):        
        p1 = [p0[0], p0[1], p0[2]]
        p2 = [p0[0] + borders, p0[1] - borders, 0]
        p3 = [p0[0] + borders, p0[1], 0]
        p4 = [p0[0], p0[1] - borders, 0]
        v_normal = get_normal_np(p1, p2, p3)
        self.writeStlFace(stream, p1, p2, p3, v_normal)
        v_normal = get_normal_np(p1, p4, p2)
        self.writeStlFace(stream, p1, p4, p2, v_normal)
        p1[2] = 0
        self.writeStlFace(stream, p1, p3, p2, base_normal)
        self.writeStlFace(stream, p1, p2, p4, base_normal)
        return 4
