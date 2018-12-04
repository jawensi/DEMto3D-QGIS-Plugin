# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DEMto3D_Dialog\SelectLayer_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SelectLayer_dialog_base(object):
    def setupUi(self, SelectLayer_dialog_base):
        SelectLayer_dialog_base.setObjectName("SelectLayer_dialog_base")
        SelectLayer_dialog_base.resize(227, 144)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/demto3d.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SelectLayer_dialog_base.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectLayer_dialog_base)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SelectLayer_dialog_base)
        self.label.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.LayerList = QtWidgets.QListWidget(SelectLayer_dialog_base)
        self.LayerList.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LayerList.setObjectName("LayerList")
        self.verticalLayout.addWidget(self.LayerList)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectLayer_dialog_base)
        self.buttonBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectLayer_dialog_base)
        self.buttonBox.accepted.connect(SelectLayer_dialog_base.accept)
        self.buttonBox.rejected.connect(SelectLayer_dialog_base.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectLayer_dialog_base)
        SelectLayer_dialog_base.setTabOrder(self.label, self.LayerList)
        SelectLayer_dialog_base.setTabOrder(self.LayerList, self.buttonBox)

    def retranslateUi(self, SelectLayer_dialog_base):
        _translate = QtCore.QCoreApplication.translate
        SelectLayer_dialog_base.setWindowTitle(_translate("SelectLayer_dialog_base", "Layer extent"))
        self.label.setText(_translate("SelectLayer_dialog_base", "Select a layer:"))

