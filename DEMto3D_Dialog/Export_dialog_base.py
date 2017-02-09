# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Export_dialog_base.ui'
#
# Created: Fri Oct 09 15:17:00 2015
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

class Ui_ExportDialogBase(object):
    def setupUi(self, ExportDialogBase):
        ExportDialogBase.setObjectName(_fromUtf8("ExportDialogBase"))
        ExportDialogBase.setWindowModality(QtCore.Qt.WindowModal)
        ExportDialogBase.resize(417, 91)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/DEMto3D/icons/demto3d.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExportDialogBase.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ExportDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ProgressLabel = QtGui.QLabel(ExportDialogBase)
        self.ProgressLabel.setText(_fromUtf8(""))
        self.ProgressLabel.setObjectName(_fromUtf8("ProgressLabel"))
        self.verticalLayout.addWidget(self.ProgressLabel)
        self.progressBar = QtGui.QProgressBar(ExportDialogBase)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cancelButton = QtGui.QToolButton(ExportDialogBase)
        self.cancelButton.setMinimumSize(QtCore.QSize(100, 25))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ExportDialogBase)
        QtCore.QMetaObject.connectSlotsByName(ExportDialogBase)

    def retranslateUi(self, ExportDialogBase):
        ExportDialogBase.setWindowTitle(_translate("ExportDialogBase", "DEMto3D", None))
        self.cancelButton.setText(_translate("ExportDialogBase", "Cancel", None))
