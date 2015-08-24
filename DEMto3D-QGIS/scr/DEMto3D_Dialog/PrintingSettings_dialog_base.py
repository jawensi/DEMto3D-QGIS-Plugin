# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PrintingSettings_dialog_base.ui'
#
# Created: Sun Aug 23 19:35:31 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PrinterSettingsDialogBase(object):
    def setupUi(self, PrinterSettingsDialogBase):
        PrinterSettingsDialogBase.setObjectName(_fromUtf8("PrinterSettingsDialogBase"))
        PrinterSettingsDialogBase.setWindowModality(QtCore.Qt.WindowModal)
        PrinterSettingsDialogBase.resize(303, 156)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/DEMto3D/icons/demto3d.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PrinterSettingsDialogBase.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(PrinterSettingsDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(PrinterSettingsDialogBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.printer_label = QtGui.QLabel(self.groupBox)
        self.printer_label.setObjectName(_fromUtf8("printer_label"))
        self.gridLayout_2.addWidget(self.printer_label, 0, 0, 1, 1)
        self.PrinterComboBox = QtGui.QComboBox(self.groupBox)
        self.PrinterComboBox.setObjectName(_fromUtf8("PrinterComboBox"))
        self.gridLayout_2.addWidget(self.PrinterComboBox, 0, 1, 1, 1)
        self.FilamentComboBox = QtGui.QComboBox(self.groupBox)
        self.FilamentComboBox.setObjectName(_fromUtf8("FilamentComboBox"))
        self.gridLayout_2.addWidget(self.FilamentComboBox, 2, 1, 1, 1)
        self.PrintingComboBox = QtGui.QComboBox(self.groupBox)
        self.PrintingComboBox.setObjectName(_fromUtf8("PrintingComboBox"))
        self.gridLayout_2.addWidget(self.PrintingComboBox, 3, 1, 1, 1)
        self.printing_label = QtGui.QLabel(self.groupBox)
        self.printing_label.setObjectName(_fromUtf8("printing_label"))
        self.gridLayout_2.addWidget(self.printing_label, 3, 0, 1, 1)
        self.filament_label = QtGui.QLabel(self.groupBox)
        self.filament_label.setObjectName(_fromUtf8("filament_label"))
        self.gridLayout_2.addWidget(self.filament_label, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self._2 = QtGui.QHBoxLayout()
        self._2.setSpacing(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.PrintButton = QtGui.QToolButton(PrinterSettingsDialogBase)
        self.PrintButton.setMinimumSize(QtCore.QSize(100, 25))
        self.PrintButton.setObjectName(_fromUtf8("PrintButton"))
        self._2.addWidget(self.PrintButton)
        self.CancelButton = QtGui.QToolButton(PrinterSettingsDialogBase)
        self.CancelButton.setMinimumSize(QtCore.QSize(100, 25))
        self.CancelButton.setObjectName(_fromUtf8("CancelButton"))
        self._2.addWidget(self.CancelButton)
        self.verticalLayout.addLayout(self._2)
        self.printer_label.setBuddy(self.PrinterComboBox)
        self.printing_label.setBuddy(self.PrintingComboBox)
        self.filament_label.setBuddy(self.FilamentComboBox)

        self.retranslateUi(PrinterSettingsDialogBase)
        QtCore.QMetaObject.connectSlotsByName(PrinterSettingsDialogBase)
        PrinterSettingsDialogBase.setTabOrder(self.PrinterComboBox, self.FilamentComboBox)
        PrinterSettingsDialogBase.setTabOrder(self.FilamentComboBox, self.PrintingComboBox)
        PrinterSettingsDialogBase.setTabOrder(self.PrintingComboBox, self.PrintButton)
        PrinterSettingsDialogBase.setTabOrder(self.PrintButton, self.CancelButton)

    def retranslateUi(self, PrinterSettingsDialogBase):
        PrinterSettingsDialogBase.setWindowTitle(_translate("PrinterSettingsDialogBase", "DEMto3D", None))
        self.groupBox.setTitle(_translate("PrinterSettingsDialogBase", "Generate Gcode", None))
        self.printer_label.setText(_translate("PrinterSettingsDialogBase", "Printer:", None))
        self.printing_label.setText(_translate("PrinterSettingsDialogBase", "Print settings:", None))
        self.filament_label.setText(_translate("PrinterSettingsDialogBase", "Filament:", None))
        self.PrintButton.setText(_translate("PrinterSettingsDialogBase", "Generate Gcode", None))
        self.CancelButton.setText(_translate("PrinterSettingsDialogBase", "Cancel", None))

from .. import resources_rc
