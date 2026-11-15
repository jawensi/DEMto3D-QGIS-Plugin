# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2026 by Jawensi
        email                : info@demto3d.com
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
from decimal import Decimal
from io import BufferedWriter
import math
import os
import struct
from builtins import range, str
from typing import Union

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


class _ExportCancelled(Exception):
    """Stop writing the current mesh when the user cancels export."""


class _ClippedTile:
    """A terrain patch clipped to exact bounds, with its boundary polylines."""

    def __init__(self, matrix, bounds):
        self.matrix = matrix
        self.bounds = bounds
        # Counterclockwise: bottom, right, top, left.
        self.boundaries = [{}, {}, {}, {}]

    def add_boundary_point(self, point):
        x_min, y_min, x_max, y_max = self.bounds
        x, y, _ = point
        if y == y_min:
            self.boundaries[0][x] = point
        if x == x_max:
            self.boundaries[1][y] = point
        if y == y_max:
            self.boundaries[2][x] = point
        if x == x_min:
            self.boundaries[3][y] = point

    def edges(self):
        return [
            [points[key] for key in sorted(points, reverse=i >= 2)]
            for i, points in enumerate(self.boundaries)
        ]


DEMData = Union[np.ndarray, _ClippedTile]


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
        self.output_files = []

    def run(self):
        x_models = self.parameters["divideCols"]
        y_models = self.parameters["divideRow"]

        x_cuts = self._division_positions(self.parameters["width"], x_models)
        y_cuts = self._division_positions(self.parameters["height"], y_models)[::-1]
        for i in range(y_models):
            for j in range(x_models):
                if self.quit:
                    return
                path = self.stl_file
                if y_models * x_models > 1:
                    path = os.path.splitext(self.stl_file)[0] + "_" + str(i) + str(j) + ".stl"
                dem_model = self.divide_dem_np(
                    self.matrix_dem,
                    x_cuts[j],
                    y_cuts[i + 1],
                    x_cuts[j + 1],
                    y_cuts[i],
                )
                self.output_files.append(path)
                if self.parameters.get("stl_format", "binary") == "ascii":
                    self.write_ascii(path, dem_model)
                else:
                    self.write_binary_np(path, dem_model)

    def write_ascii(self, fileName, demData):
        """Write the same terrain, base and walls as the binary NumPy exporter."""
        with open(fileName, "w", encoding="ascii") as stream:
            stream.write("solid model\n")
            try:
                self.write_face_dem_np(demData, stream)
                if self.parameters["has_borders"]:
                    self.write_face_base_np(demData, stream)
                    self.write_face_wall_np(demData, stream)
            except _ExportCancelled:
                return
            stream.write("endsolid model\n")

    def write_binary(self, fileName: str, demData: list[list[pto]]):
        with open(fileName, "wb") as stream:
            counter = 0
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
                    return 0

            stream.seek(0)
            stream.write(
                struct.pack(BINARY_HEADER, b"Python Binary STL Writer", counter)
            )

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
    def _division_positions(length, parts):
        """Locate cuts from model dimensions, independent of the sampling grid."""
        size = Decimal(str(length))
        return np.array([float(size * i / parts) for i in range(parts + 1)])

    @staticmethod
    def divide_dem_np(
        matrix_dem_build: np.ndarray, x_min, y_min, x_max, y_max
    ) -> DEMData:
        """Select intersecting cells and clip their triangles at the requested bounds."""
        xs = matrix_dem_build[0, :, 0]
        ys = -matrix_dem_build[:, 0, 1]
        col0 = max(0, np.searchsorted(xs, x_min, side="right") - 1)
        col1 = min(len(xs) - 1, np.searchsorted(xs, x_max, side="left"))
        row0 = max(0, np.searchsorted(ys, -y_max, side="right") - 1)
        row1 = min(len(ys) - 1, np.searchsorted(ys, -y_min, side="left"))
        matrix = matrix_dem_build[row0:row1 + 1, col0:col1 + 1]
        if (matrix[0, 0, 0] == x_min and matrix[-1, -1, 0] == x_max
                and matrix[0, 0, 1] == y_max and matrix[-1, -1, 1] == y_min):
            return matrix
        return _ClippedTile(matrix, (x_min, y_min, x_max, y_max))

    @staticmethod
    def _clip_cell(p1, p2, p3, p4, bounds):
        """Intersect a grid cell's two original triangles with a rectangle."""
        x0, y0, z0 = p1
        x1, y1, z1 = p2
        dx, dy = x1 - x0, y1 - y0
        x_min, y_min, x_max, y_max = bounds
        left, right = max(x0, x_min), min(x1, x_max)
        bottom, top = max(y0, y_min), min(y1, y_max)
        if left >= right or bottom >= top:
            return
        rectangle = [(left, bottom), (right, bottom), (right, top), (left, top)]

        def diagonal_distance(point):
            distance = (point[0] - x0) * dy - (point[1] - y0) * dx
            # Treat numerical noise at a diagonal corner as an exact intersection.
            tolerance = 8 * np.finfo(float).eps * dx * dy
            return 0 if abs(distance) <= tolerance else distance

        # Clip the intersection rectangle against each side of the original diagonal.
        for upper in (True, False):
            polygon = []
            previous = rectangle[-1]
            previous_d = diagonal_distance(previous)
            previous_inside = previous_d <= 0 if upper else previous_d >= 0
            for current in rectangle:
                distance = diagonal_distance(current)
                inside = distance <= 0 if upper else distance >= 0
                if inside != previous_inside:
                    # Use the original diagonal so adjacent tiles compute identical points.
                    if previous[0] == current[0]:
                        x = current[0]
                        y = min(top, max(bottom, y0 + (x - x0) * dy / dx))
                    else:
                        y = current[1]
                        x = min(right, max(left, x0 + (y - y0) * dx / dy))
                    polygon.append((x, y, True))
                if inside:
                    polygon.append((*current, distance == 0))
                previous, previous_inside = current, inside

            points = []
            for x, y, diagonal in polygon:
                if points and points[-1][0] == x and points[-1][1] == y:
                    continue
                u, v = (x - x0) / dx, (y - y0) / dy
                # Evaluate original edges consistently from either neighboring cell.
                if x == x0 and y == y0:
                    z = z0
                elif x == x1 and y == y1:
                    z = z1
                elif x == x0 and y == y1:
                    z = p3[2]
                elif x == x1 and y == y0:
                    z = p4[2]
                elif x == x0:
                    z = z0 + v * (p3[2] - z0)
                elif x == x1:
                    z = p4[2] + v * (z1 - p4[2])
                elif y == y0:
                    z = z0 + u * (p4[2] - z0)
                elif y == y1:
                    z = p3[2] + u * (z1 - p3[2])
                elif diagonal:
                    z = z0 + u * (z1 - z0)
                elif upper:
                    z = z0 + u * (z1 - p3[2]) + v * (p3[2] - z0)
                else:
                    z = z0 + u * (p4[2] - z0) + v * (z1 - p4[2])
                points.append((x, y, z))
            if len(points) > 1 and points[0][:2] == points[-1][:2]:
                points.pop()
            for k in range(1, len(points) - 1):
                a, b, c = points[0], points[k], points[k + 1]
                area2 = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                if area2 > 0:
                    yield a, b, c

    def _write_clipped_dem(self, tile, stream):
        matrix = tile.matrix
        x_min, y_min, x_max, y_max = tile.bounds
        count = 0
        for j in range(matrix.shape[0] - 1):
            for k in range(matrix.shape[1] - 1):
                p1, p2 = matrix[j + 1, k], matrix[j, k + 1]
                p3, p4 = matrix[j, k], matrix[j + 1, k + 1]
                if (x_min <= p1[0] and p2[0] <= x_max
                        and y_min <= p1[1] and p2[1] <= y_max):
                    faces = ((p1, p2, p3), (p1, p4, p2))
                else:
                    faces = self._clip_cell(p1, p2, p3, p4, tile.bounds)
                boundary_cell = (p1[0] <= x_min or p2[0] >= x_max
                                 or p1[1] <= y_min or p2[1] >= y_max)
                for face in faces:
                    self.writeStlFace(stream, *face, get_normal_np(*face))
                    count += 1
                    if boundary_cell:
                        for point in face:
                            tile.add_boundary_point(point)
        return count

    def _write_clipped_base(self, tile, stream):
        x_min, y_min, x_max, y_max = tile.bounds
        center = [(x_min + x_max) / 2, (y_min + y_max) / 2, 0]
        count = 0
        for edge in tile.edges():
            for p1, p2 in zip(edge, edge[1:]):
                self.writeStlBaseFace(stream, p1, p2, center)
                count += 1
        return count

    def _write_clipped_walls(self, tile, stream):
        edges = tile.edges()
        borders = self.parameters["borders"]
        count = 0
        offsets = ((0, -borders), (borders, 0), (0, borders), (-borders, 0))
        for edge, (ox, oy) in zip(edges, offsets):
            for p1, p2 in zip(edge, edge[1:]):
                outer1, outer2 = [p1[0] + ox, p1[1] + oy, 0], [p2[0] + ox, p2[1] + oy, 0]
                for face in ((outer1, outer2, p2), (outer1, p2, p1)):
                    self.writeStlFace(stream, *face, get_normal_np(*face))
                    count += 1
                if borders > 0:
                    self.writeStlBaseFace(stream, p1, outer1, outer2)
                    self.writeStlBaseFace(stream, p1, outer2, p2)
                    count += 2
        if borders > 0:
            count += self.writeUpperRightCornerBevel(edges[1][-1], stream, borders)
            count += self.writeUpperLeftCornerBevel(edges[2][-1], stream, borders)
            count += self.writeBottomLeftCornerBevel(edges[3][-1], stream, borders)
            count += self.writeBottomRightCornerBevel(edges[0][-1], stream, borders)
        return count

    def write_binary_np(self, fileName: str, demData: DEMData):
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
        except (IOError, OSError, _ExportCancelled):
            stream.close()

    def writeStlBaseFace(self, stream, p1, p2, p3):
        self.writeStlFace(
            stream,
            [p2[0], p2[1], 0],
            [p1[0], p1[1], 0],
            [p3[0], p3[1], 0],
            base_normal,
        )

    def write_face_base_np(self, matrix_dem: DEMData, stream: BufferedWriter):
        if isinstance(matrix_dem, _ClippedTile):
            return self._write_clipped_base(matrix_dem, stream)
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

    def writeStlFace(self, stream, p1, p2, p3, normal):
        if self.quit:
            raise _ExportCancelled()
        self.updateProgress.emit()
        if "b" in stream.mode:
            data = [*normal, *p1, *p2, *p3, 0]
            stream.write(struct.pack(BINARY_FACET, *data))
        else:
            stream.write("   facet normal {} {} {}\n".format(*normal))
            stream.write("       outer loop\n")
            for point in (p1, p2, p3):
                stream.write("           vertex {} {} {}\n".format(*point))
            stream.write("       endloop\n   endfacet\n")

    def write_face_dem_np(self, matrix_dem: DEMData, stream: BufferedWriter):
        if isinstance(matrix_dem, _ClippedTile):
            return self._write_clipped_dem(matrix_dem, stream)
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

    def write_face_wall_np(self, matrix_dem: DEMData, stream: BufferedWriter):
        if isinstance(matrix_dem, _ClippedTile):
            return self._write_clipped_walls(matrix_dem, stream)
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

        offset = 5  # if 5.0 < borders else borders * 0.7
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
