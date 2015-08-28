# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Impresión 3D de MDE
                              -------------------
        begin                : 2015-08-02
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Francisco Javier Venceslá Simón
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
import copy
import os
import subprocess
import sys

from PyQt4.QtCore import QThread

from qgis._core import QgsApplication


class Gcode(QThread):
    def __init__(self, gcode_file, print_settings):
        QThread.__init__(self)
        self.gcode_file = gcode_file
        self.print_settings = copy.deepcopy(print_settings)

    def run(self):
        slicer = QgsApplication.qgisSettingsDirPath() + 'python/plugins/AppONCE/Slic3r/slic3r-console.exe'
        stl_file = QgsApplication.qgisSettingsDirPath() + 'python/plugins/DEMto3D/temp.stl'

        try:
            command = subprocess.check_call(
                [slicer, '-load', self.print_settings[0], '-load', self.print_settings[1], '-load',
                 self.print_settings[2], stl_file, '-output',
                 self.gcode_file], shell=True)
            if command < 0:
                print >> sys.stderr, "Child was terminated by signal", -command
            else:
                print >> sys.stderr, "Child returned", command
        except OSError as e:
            print >> sys.stderr, "Execution failed:", e
        except subprocess.CalledProcessError:
            print 'error in Slic3r setting file '

        os.remove(stl_file)






