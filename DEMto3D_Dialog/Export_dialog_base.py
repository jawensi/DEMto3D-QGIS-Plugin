# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DEMto3D_Dialog\Export_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ExportDialogBase(object):
    def setupUi(self, ExportDialogBase):
        ExportDialogBase.setObjectName("ExportDialogBase")
        ExportDialogBase.setWindowModality(QtCore.Qt.WindowModal)
        ExportDialogBase.resize(417, 91)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/demto3d.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExportDialogBase.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(ExportDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ProgressLabel = QtWidgets.QLabel(ExportDialogBase)
        self.ProgressLabel.setText("")
        self.ProgressLabel.setObjectName("ProgressLabel")
        self.verticalLayout.addWidget(self.ProgressLabel)
        self.progressBar = QtWidgets.QProgressBar(ExportDialogBase)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancelButton = QtWidgets.QToolButton(ExportDialogBase)
        self.cancelButton.setMinimumSize(QtCore.QSize(100, 25))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ExportDialogBase)
        QtCore.QMetaObject.connectSlotsByName(ExportDialogBase)

    def retranslateUi(self, ExportDialogBase):
        _translate = QtCore.QCoreApplication.translate
        ExportDialogBase.setWindowTitle(_translate("ExportDialogBase", "DEMto3D"))
        self.cancelButton.setText(_translate("ExportDialogBase", "Cancel"))

