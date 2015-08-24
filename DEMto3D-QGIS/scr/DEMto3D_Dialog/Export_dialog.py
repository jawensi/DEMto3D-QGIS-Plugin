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

from PyQt4 import QtCore
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QDialog, QFileDialog
from qgis._core import QgsApplication

from Export_dialog_base import Ui_ExportDialogBase
from ..model_builder.Model_Builder import Model
from ..model_builder.STL_Builder import STL
from ..model_builder.Gcode_Builder import Gcode


class Dialog(QDialog, Ui_ExportDialogBase):
    def __init__(self, parameters, file_name, slicer_settings):
        """Constructor for the dialog."""
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.ui = Ui_ExportDialogBase()
        self.ui.setupUi(self)
        self.parameters = parameters
        self.slicer_settings = slicer_settings

        if not self.slicer_settings:
            self.stl_file = file_name
            self.do_model()

        elif self.slicer_settings:
            self.stl_file = QgsApplication.qgisSettingsDirPath() + 'python/plugins/DEMto3D/temp.stl'
            self.gcode_file = file_name
            self.do_model()

    def do_model(self):
        self.ui.ProgressLabel.setText(self.tr("Building STL geometry ..."))
        self.Model = Model(self.ui.progressBar, self.ui.ProgressLabel, self.parameters)
        self.Model.updateProgress.connect(lambda: self.ui.progressBar.setValue(self.ui.progressBar.value() + 1))
        QtCore.QObject.connect(self.Model, SIGNAL("finished()"), self.do_stl_model)
        self.Model.start()

    def do_stl_model(self):
        self.ui.ProgressLabel.setText(self.tr("Creating STL file ..."))
        dem_matrix = self.Model.get_model()
        self.STL = STL(self.ui.progressBar, self.ui.ProgressLabel, self.parameters, self.stl_file, dem_matrix)
        self.STL.updateProgress.connect(lambda: self.ui.progressBar.setValue(self.ui.progressBar.value() + 1))
        if not self.slicer_settings:
            QtCore.QObject.connect(self.STL, SIGNAL("finished()"), self.finish_model)
        elif self.slicer_settings:
            QtCore.QObject.connect(self.STL, SIGNAL("finished()"), self.do_gcode_model)
        self.STL.start()

    def do_gcode_model(self):
        self.ui.ProgressLabel.setText(self.tr("Creating Gcode file ..."))
        self.gcode = Gcode(self.gcode_file, self.slicer_settings)
        QtCore.QObject.connect(self.gcode, SIGNAL("finished()"), self.finish_model)
        self.gcode.start()
        self.ui.progressBar.setMaximum(0)

    def finish_model(self):
        self.accept()



