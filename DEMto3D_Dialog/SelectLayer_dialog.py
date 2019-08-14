# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
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

from __future__ import absolute_import

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog
from .SelectLayer_dialog_base import Ui_SelectLayer_dialog_base


class Dialog(QDialog, Ui_SelectLayer_dialog_base):
    def __init__(self):
        """Constructor for the dialog."""
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.ui = Ui_SelectLayer_dialog_base()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def get_layer(self):
        return self.ui.mMapLayerComboBox.currentLayer()
