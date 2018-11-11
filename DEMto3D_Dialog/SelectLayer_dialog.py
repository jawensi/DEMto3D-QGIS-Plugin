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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog
from SelectLayer_dialog_base import Ui_SelectLayer_dialog_base

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Dialog(QDialog, Ui_SelectLayer_dialog_base):
    def __init__(self, layers):
        """Constructor for the dialog."""
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.ui = Ui_SelectLayer_dialog_base()
        self.ui.setupUi(self)

        self.ui.LayerList.clear()
        for layer in layers:
            item = QtGui.QListWidgetItem()
            item.setText(layer.name())
            self.ui.LayerList.addItem(item)

        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)

    def get_layer(self):
        try:
            return self.ui.LayerList.currentItem().text()
        except AttributeError:
            pass
