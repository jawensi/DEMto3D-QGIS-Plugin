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

from builtins import str
from builtins import range
import collections
import struct
import math
import os

from qgis.PyQt.QtCore import QThread, pyqtSignal

from .terrain_clipper import ClippedTerrain, clip_grid, division_positions

BINARY_HEADER = "80sI"
BINARY_FACET = "12fH"

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
    normal = collections.namedtuple('normal', 'normal_x normal_y normal_z')
    pto = collections.namedtuple('pto', 'x y z')
    updateProgress = pyqtSignal()

    def __init__(self, parameters, stl_file, dem_matrix):
        QThread.__init__(self)
        self.parameters = parameters
        self.stl_file = stl_file
        self.matrix_dem = dem_matrix
        self.quit = False
        self.output_files = []

    def run(self):
        x_models = self.parameters["divideCols"]
        y_models = self.parameters["divideRow"]

        x_cuts = division_positions(self.parameters["width"], x_models)
        y_cuts = division_positions(self.parameters["height"], y_models)[::-1]

        for i in range(y_models):
            for j in range(x_models):
                if self.quit:
                    return
                path = self.stl_file
                if (y_models * x_models > 1):
                    path = os.path.splitext(self.stl_file)[0] + '_{}_{}.stl'.format(i, j)
                dem_model = self.cut_dem(
                    self.matrix_dem,
                    self.parameters["spacing_mm"],
                    x_cuts[j],
                    y_cuts[i + 1],
                    x_cuts[j + 1],
                    y_cuts[i]
                )
                self.output_files.append(path)
                if self.parameters.get("stl_format") == "ascii":
                    self.write_ascii(path, dem_model)
                else:
                    self.write_binary(path, dem_model)

    def _export_faces(self, dem_data):
        terrain = self.face_dem_vector(dem_data)
        if self.parameters.get("has_borders", True):
            normal = self.normal(0, 0, -1)
            for p1, p2, p3, _ in terrain:
                yield p2._replace(z=0), p1._replace(z=0), p3._replace(z=0), normal
            yield from self.face_wall_vector(dem_data)
        yield from terrain

    def write_ascii(self, fileName, demData):
        with open(fileName, "w", encoding="ascii") as stream:
            stream.write("solid model\n")
            for p1, p2, p3, normal in self._export_faces(demData):
                if self.quit:
                    return
                self.updateProgress.emit()
                stream.write("   facet normal {} {} {}\n".format(*normal))
                stream.write("       outer loop\n")
                for point in (p1, p2, p3):
                    stream.write("           vertex {} {} {}\n".format(*point))
                stream.write("       endloop\n   endfacet\n")
            stream.write("endsolid model\n")

    def write_binary(self, fileName, demData):
        try:
            with open(fileName, "wb") as stream:
                count = 0
                stream.write(struct.pack(BINARY_HEADER, b"Python Binary STL Writer", count))
                for p1, p2, p3, normal in self._export_faces(demData):
                    if self.quit:
                        return
                    self.updateProgress.emit()
                    stream.write(struct.pack(BINARY_FACET, *normal, *p1, *p2, *p3, 0))
                    count += 1
                stream.seek(0)
                stream.write(struct.pack(BINARY_HEADER, b"Python Binary STL Writer", count))
        except (IOError, OSError):
            return

    def face_wall_vector(self, matrix_dem):
        if isinstance(matrix_dem, ClippedTerrain):
            return self._clipped_walls(matrix_dem)
        borders = self.parameters["borders"]
        hasBorders = borders > 0
        if hasBorders:
            return self.face_wall_borders_vector(matrix_dem)
        else:
            return self.face_wall_No_borders_vector(matrix_dem)

    def _clipped_walls(self, tile):
        edges = tile.edges()
        borders = self.parameters["borders"]
        offsets = ((0, -borders), (borders, 0), (0, borders), (-borders, 0))
        faces = []

        def add_face(p1, p2, p3):
            faces.append([p1, p2, p3, self.get_normal(p1, p2, p3)])

        for edge, (ox, oy) in zip(edges, offsets):
            for p1, p2 in zip(edge, edge[1:]):
                outer1 = self.pto(p1.x + ox, p1.y + oy, 0)
                outer2 = self.pto(p2.x + ox, p2.y + oy, 0)
                add_face(outer1, outer2, p2)
                add_face(outer1, p2, p1)
                if borders > 0:
                    base1, base2 = p1._replace(z=0), p2._replace(z=0)
                    add_face(base1, outer2, outer1)
                    add_face(base1, base2, outer2)

        if borders > 0:
            for i, edge in enumerate(edges):
                corner = edge[0]
                px, py = offsets[(i - 1) % 4]
                ox, oy = offsets[i]
                previous = self.pto(corner.x + px, corner.y + py, 0)
                outer = self.pto(corner.x + px + ox, corner.y + py + oy, 0)
                following = self.pto(corner.x + ox, corner.y + oy, 0)
                add_face(corner, previous, outer)
                add_face(corner, outer, following)
                base = corner._replace(z=0)
                add_face(base, outer, previous)
                add_face(base, following, outer)
        return faces

    def face_wall_No_borders_vector(self, matrix_dem):
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

    def face_wall_borders_vector(self, matrix_dem):
        borders = self.parameters["borders"]
        rows = matrix_dem.__len__()
        cols = matrix_dem[0].__len__()
        vector_face = []
        d = 0

        # UPPER RIGHT CORNER
        p0 = matrix_dem[0][cols-1]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x+borders, y=p0y+borders, z=d)
        p3 = self.pto(x=p0x, y=p0y+borders, z=d)
        p4 = self.pto(x=p0x+borders, y=p0y, z=d)
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
        p2 = self.pto(x=p0x-borders, y=p0y+borders, z=d)
        p3 = self.pto(x=p0x-borders, y=p0y, z=d)
        p4 = self.pto(x=p0x, y=p0y+borders, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # BOTTOM LEFT CORNER
        p0 = matrix_dem[rows-1][0]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x-borders, y=p0y-borders, z=d)
        p3 = self.pto(x=p0x, y=p0y-borders, z=d)
        p4 = self.pto(x=p0x-borders, y=p0y, z=d)
        v_normal = self.get_normal(p1, p2, p3)
        vector_face.append([p1, p2, p3, v_normal])
        v_normal = self.get_normal(p1, p4, p2)
        vector_face.append([p1, p4, p2, v_normal])
        p1 = p1._replace(z=d)
        v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
        vector_face.append([p1, p3, p2, v_normal])
        vector_face.append([p1, p2, p4, v_normal])

        # BOTTOM RIGHT CORNER
        p0 = matrix_dem[rows-1][cols-1]
        p0x = getattr(p0, "x")
        p0y = getattr(p0, "y")
        p0z = getattr(p0, "z")
        p1 = self.pto(x=p0x, y=p0y, z=p0z)
        p2 = self.pto(x=p0x+borders, y=p0y-borders, z=d)
        p3 = self.pto(x=p0x+borders, y=p0y, z=d)
        p4 = self.pto(x=p0x, y=p0y-borders, z=d)
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
            p1 = p3._replace(z=d, x=getattr(p3, 'x')-borders)
            p4 = p2._replace(z=d, x=getattr(p2, 'x')-borders)
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
            p3 = p1._replace(z=d, x=getattr(p1, 'x')+borders)
            p4 = p2._replace(z=d, x=getattr(p2, 'x')+borders)
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
            p3 = p1._replace(z=d, y=getattr(p1, 'y')+borders)
            p4 = p2._replace(z=d, y=getattr(p2, 'y')+borders)
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
            p1 = p3._replace(z=d, y=getattr(p3, 'y')-borders)
            p4 = p2._replace(z=d, y=getattr(p2, 'y')-borders)
            v_normal = self.get_normal(p1, p2, p3)
            vector_face.append([p1, p2, p3, v_normal])
            vector_face.append([p1, p4, p2, v_normal])
            p2 = p2._replace(z=d)
            p3 = p3._replace(z=d)
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=-1)
            vector_face.append([p1, p3, p2, v_normal])
            vector_face.append([p1, p2, p4, v_normal])
        return vector_face

    def face_dem_vector(self, matrix_dem):
        if isinstance(matrix_dem, ClippedTerrain):
            return [[p1, p2, p3, self.get_normal(p1, p2, p3)]
                    for p1, p2, p3 in matrix_dem.triangles]
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
            v = [getattr(p2, "x") - getattr(p1, "x"), getattr(p2, "y") - getattr(p1, "y"),
                 getattr(p2, "z") - getattr(p1, "z")]
            w = [getattr(p3, "x") - getattr(p1, "x"), getattr(p3, "y") - getattr(p1, "y"),
                 getattr(p3, "z") - getattr(p1, "z")]

            x = (v[1] * w[2]) - (v[2] * w[1])
            y = (v[2] * w[0]) - (v[0] * w[2])
            z = (v[0] * w[1]) - (v[1] * w[0])
            modulo = math.sqrt(x * x + y * y + z * z)

            v_normal = self.normal(normal_x=x / modulo, normal_y=y / modulo, normal_z=z / modulo)
            return v_normal
        except ZeroDivisionError:
            v_normal = self.normal(normal_x=0, normal_y=0, normal_z=0)
        return v_normal

    @staticmethod
    def cut_dem(matrix_dem_build, resolution, x_min, y_min, x_max, y_max):
        # Keep the resolution argument for callers; cuts depend only on geometry.
        return clip_grid(matrix_dem_build, x_min, y_min, x_max, y_max)
