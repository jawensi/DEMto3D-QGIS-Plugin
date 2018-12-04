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

from builtins import str
from builtins import range
import collections

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QThread

import math


class STL(QThread):
    """Class where is built the stl file from the mesh point that decribe the model surface"""
    normal = collections.namedtuple('normal', 'normal_x normal_y normal_z')
    pto = collections.namedtuple('pto', 'x y z')
    updateProgress = QtCore.pyqtSignal()

    def __init__(self, bar, label, button, parameters, stl_file, dem_matrix):
        QThread.__init__(self)
        self.bar = bar
        self.label = label
        self.button = button
        self.parameters = parameters
        self.stl_file = stl_file
        self.matrix_dem = dem_matrix

        self.quit = False
        self.button.clicked.connect(self.cancel)

    def run(self):
        f = open(self.stl_file, "w")
        f.write("solid model\n")

        dem = self.face_dem_vector(self.matrix_dem)
        self.bar.setMaximum(dem.__len__() * 2)
        self.bar.setValue(0)
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

    def face_wall_vector(self, matrix_dem):
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

    def cancel(self):
        self.quit = True
