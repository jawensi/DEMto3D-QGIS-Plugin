# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SelectLayer_dialog_base.ui'
#
# Created: Sun Aug 23 19:32:50 2015
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

class Ui_SelectLayer_dialog_base(object):
    def setupUi(self, SelectLayer_dialog_base):
        SelectLayer_dialog_base.setObjectName(_fromUtf8("SelectLayer_dialog_base"))
        SelectLayer_dialog_base.resize(227, 144)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/DEMto3D/icons/demto3d.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SelectLayer_dialog_base.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(SelectLayer_dialog_base)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(SelectLayer_dialog_base)
        self.label.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.LayerList = QtGui.QListWidget(SelectLayer_dialog_base)
        self.LayerList.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LayerList.setObjectName(_fromUtf8("LayerList"))
        self.verticalLayout.addWidget(self.LayerList)
        self.buttonBox = QtGui.QDialogButtonBox(SelectLayer_dialog_base)
        self.buttonBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectLayer_dialog_base)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SelectLayer_dialog_base.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SelectLayer_dialog_base.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectLayer_dialog_base)
        SelectLayer_dialog_base.setTabOrder(self.label, self.LayerList)
        SelectLayer_dialog_base.setTabOrder(self.LayerList, self.buttonBox)

    def retranslateUi(self, SelectLayer_dialog_base):
        SelectLayer_dialog_base.setWindowTitle(_translate("SelectLayer_dialog_base", "Layer extent", None))
        self.label.setText(_translate("SelectLayer_dialog_base", "Select a layer:", None))

from .. import resources_rc
