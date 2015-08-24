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
import os

from PyQt4 import QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import Qt

from PrintingSettings_dialog_base import Ui_PrinterSettingsDialogBase, _fromUtf8


class Dialog(QDialog, Ui_PrinterSettingsDialogBase):
    def __init__(self, parameters, printer):
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.ui = Ui_PrinterSettingsDialogBase()
        self.ui.setupUi(self)

        self.parameters = parameters
        self.printer = printer
        self.slicer_settings = None

        self.upload_printer()
        printer = os.path.split(self.printer)[1]
        printer = os.path.splitext(printer)[0]
        i = self.ui.PrinterComboBox.findText(printer)
        self.ui.PrinterComboBox.setCurrentIndex(i)
        self.upload_filament()
        self.upload_printing()

        QtCore.QObject.connect(self.ui.PrintButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.do_gcode)
        QtCore.QObject.connect(self.ui.CancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.reject)

    def upload_printer(self):
        dir_printer = os.getenv("HOME") + '\\AppData\\Roaming\\Slic3r\\printer\\'
        files = os.listdir(dir_printer)
        self.ui.PrinterComboBox.clear()
        for f in files:
            name = os.path.splitext(f)[0]
            self.ui.PrinterComboBox.addItem(name)

    def upload_filament(self):
        try:
            dir_filament = os.getenv("HOME") + '\\AppData\\Roaming\\Slic3r\\filament\\'
            files = os.listdir(dir_filament)
            self.ui.FilamentComboBox.clear()
            for f in files:
                name = os.path.splitext(f)[0]
                self.ui.FilamentComboBox.addItem(name)
        except WindowsError:
            pass

    def upload_printing(self):
        try:
            dir_print = os.getenv("HOME") + '\\AppData\\Roaming\\Slic3r\\print\\'
            files = os.listdir(dir_print)
            self.ui.PrintingComboBox.clear()
            for f in files:
                name = os.path.splitext(f)[0]
                self.ui.PrintingComboBox.addItem(name)
        except WindowsError:
            pass

    def do_gcode(self):
        reply = QMessageBox.question(self, self.tr('Export model to Gcode'), self.tr(
            "The construction of the G-CODE file could takes several minutes. Do you want to continue?"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            printer = os.getenv(
                "HOME") + '\\AppData\\Roaming\\Slic3r\\printer\\' + self.ui.PrinterComboBox.currentText() + '.ini'
            filament = os.getenv(
                "HOME") + '\\AppData\\Roaming\\Slic3r\\filament\\' + self.ui.FilamentComboBox.currentText() + '.ini'
            printing = os.getenv(
                "HOME") + '\\AppData\\Roaming\\Slic3r\\print\\' + self.ui.PrintingComboBox.currentText() + '.ini'
            self.slicer_settings = [printer, filament, printing]
            self.accept()
        else:
            self.reject()

    def get_slicer_settings(self):
        return self.slicer_settings