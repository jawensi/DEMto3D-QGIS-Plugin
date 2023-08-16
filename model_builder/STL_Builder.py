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

from builtins import str
from builtins import range
import collections
import struct
import math

from qgis.PyQt.QtCore import QThread, pyqtSignal

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

    def run(self):
        x_models = self.parameters["divideCols"]
        y_models = self.parameters["divideRow"]

        width_model = self.parameters["width"] / x_models
        high_model = self.parameters["height"] / y_models

        for i in range(y_models):
            for j in range(x_models):
                path = self.stl_file
                if (y_models * x_models > 1):
                    path = self.stl_file.split(".")[0] + '_' + str(i) + str(j) + '.stl'
                x_min_model = width_model * j
                y_min_model = self.parameters["height"] - i * high_model - high_model
                x_max_model = width_model * j + width_model
                y_max_model = self.parameters["height"] - i * high_model
                dem_model = self.cut_dem(self.matrix_dem, self.parameters["spacing_mm"], x_min_model, y_min_model, x_max_model, y_max_model)
                self.write_binary(path, dem_model)

        # self.write_binary(self.stl_file, self.matrix_dem)

    def write_ascii(self):
        f = open(self.stl_file, "w")
        f.write("solid model\n")

        dem = self.face_dem_vector(self.matrix_dem)
        for face in dem:
            self.updateProgress.emit()
            f.write("   facet normal 0 0 -1 " + "\n")
            f.write("       outer loop\n")
            f.write("           vertex " + str(getattr(face[1], "x")) + " " + str(getattr(face[1], "y")) +
                    " " + "0" + "\n")
            f.write("           vertex " + str(getattr(face[0], "x")) + " " + str(getattr(face[0], "y")) +
                    " " + "0" + "\n")
            f.write("           vertex " + str(getattr(face[2], "x")) + " " + str(getattr(face[2], "y")) +
                    " " + "0" + "\n")
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        wall = self.face_wall_vector(self.matrix_dem)
        for face in wall:
            f.write("   facet normal " + str(getattr(face[3], "normal_x")) + " " +
                    str(getattr(face[3], "normal_y")) + " " + str(getattr(face[3], "normal_z")) + "\n")
            f.write("       outer loop\n")
            f.write("           vertex " + str(getattr(face[0], "x")) + " " + str(getattr(face[0], "y")) +
                    " " + str(getattr(face[0], "z")) + "\n")
            f.write("           vertex " + str(getattr(face[1], "x")) + " " + str(getattr(face[1], "y")) +
                    " " + str(getattr(face[1], "z")) + "\n")
            f.write("           vertex " + str(getattr(face[2], "x")) + " " + str(getattr(face[2], "y")) +
                    " " + str(getattr(face[2], "z")) + "\n")
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        for face in dem:
            self.updateProgress.emit()
            f.write("   facet normal " + str(getattr(face[3], "normal_x")) + " " +
                    str(getattr(face[3], "normal_y")) + " " + str(getattr(face[3], "normal_z")) + "\n")
            f.write("       outer loop\n")
            f.write("           vertex " + str(getattr(face[0], "x")) + " " + str(getattr(face[0], "y")) +
                    " " + str(getattr(face[0], "z")) + "\n")
            f.write("           vertex " + str(getattr(face[1], "x")) + " " + str(getattr(face[1], "y")) +
                    " " + str(getattr(face[1], "z")) + "\n")
            f.write("           vertex " + str(getattr(face[2], "x")) + " " + str(getattr(face[2], "y")) +
                    " " + str(getattr(face[2], "z")) + "\n")
            f.write("       endloop\n")
            f.write("   endfacet\n")
            if self.quit:
                f.close()
                return 0

        f.write("endsolid model\n")
        f.close()

    def write_binary(self, fileName, demData):
        try:
            counter = 0
            stream = open(fileName, "wb")
            stream.seek(0)
            stream.write(struct.pack(BINARY_HEADER, b'Python Binary STL Writer', counter))

            dem = self.face_dem_vector(demData)
            for face in dem:
                self.updateProgress.emit()
                counter += 1
                data = [
                    0, 0, -1,
                    getattr(face[1], "x"), getattr(face[1], "y"), 0,
                    getattr(face[0], "x"), getattr(face[0], "y"), 0,
                    getattr(face[2], "x"), getattr(face[2], "y"), 0,
                    0
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            wall = self.face_wall_vector(demData)
            for face in wall:
                counter += 1
                data = [
                    getattr(face[3], "normal_x"), getattr(face[3], "normal_y"), getattr(face[3], "normal_z"),
                    getattr(face[0], "x"), getattr(face[0], "y"), getattr(face[0], "z"),
                    getattr(face[1], "x"), getattr(face[1], "y"), getattr(face[1], "z"),
                    getattr(face[2], "x"), getattr(face[2], "y"), getattr(face[2], "z"),
                    0
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            for face in dem:
                self.updateProgress.emit()
                counter += 1
                data = [
                    getattr(face[3], "normal_x"), getattr(face[3], "normal_y"), getattr(face[3], "normal_z"),
                    getattr(face[0], "x"), getattr(face[0], "y"), getattr(face[0], "z"),
                    getattr(face[1], "x"), getattr(face[1], "y"), getattr(face[1], "z"),
                    getattr(face[2], "x"), getattr(face[2], "y"), getattr(face[2], "z"),
                    0
                ]
                stream.write(struct.pack(BINARY_FACET, *data))
                if self.quit:
                    stream.close()
                    return 0

            stream.seek(0)
            stream.write(struct.pack(BINARY_HEADER, b'Python Binary STL Writer', counter))
            stream.close()
        except:
            stream.close()

    def face_wall_vector(self, matrix_dem):
        borders = self.parameters["borders"]
        hasBorders = borders > 0
        if hasBorders:
            return self.face_wall_borders_vector(matrix_dem)
        else:
            return self.face_wall_No_borders_vector(matrix_dem)

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
            p4 = p2._replace(z=d,x=getattr(p2, 'x')-borders)
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
            p3 = p1._replace(z=d,x=getattr(p1, 'x')+borders)            
            p4 = p2._replace(z=d,x=getattr(p2, 'x')+borders)
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
            p3 = p1._replace(z=d,y=getattr(p1, 'y')+borders)            
            p4 = p2._replace(z=d,y=getattr(p2, 'y')+borders)
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
            p1 = p3._replace(z=d,y=getattr(p3, 'y')-borders)
            p4 = p2._replace(z=d,y=getattr(p2, 'y')-borders)
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
        rows = matrix_dem_build.__len__()
        cols = matrix_dem_build[0].__len__()
        dem = []
        for i in range(rows):
            aux = []
            for j in range(cols):
                x = getattr(matrix_dem_build[i][j], "x")
                y = getattr(matrix_dem_build[i][j], "y")
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    aux.append(matrix_dem_build[i][j])
                elif 0 < (x - x_max) < resolution and y_min <= y <= y_max:
                    aux.append(matrix_dem_build[i][j])
                elif -resolution < (y - y_min) < 0 and x_min <= x <= x_max:
                    aux.append(matrix_dem_build[i][j])
                elif 0 < (x - x_max) < resolution and - resolution < (y - y_min) < 0:
                    aux.append(matrix_dem_build[i][j])
            if aux:
                dem.append(aux)
        return dem
