# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2022 by Javier
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
from __future__ import absolute_import
from builtins import object

import os.path

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
# Initialize Qt resources from file resources.py
from . import resources_rc
# Import the code for the dialog
from .DEMto3D_Dialog import DEMto3D_dialog


class DEMto3D(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DEMto3D_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.action = None
        self.menu = '&DEMto3D'

        self.window = True

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DEMto3D', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon = QIcon(":/plugins/DEMto3D/icons/demto3d.png")
        text = self.tr("DEM 3D printing")
        parent = self.iface.mainWindow()
        self.action = QAction(icon, text, parent)
        self.action.setObjectName(text)
        self.action.setStatusTip(text)
        self.action.triggered.connect(self.run)

        self.iface.addRasterToolBarIcon(self.action)
        self.iface.addPluginToRasterMenu(self.menu, self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginRasterMenu(self.menu, self.action)
        self.iface.removeRasterToolBarIcon(self.action)

    def run(self):
        layers = self.iface.mapCanvas().layers()
        raster = False
        if layers:
            for layer in layers:
                if layer.type() == layer.RasterLayer and QgsProject.instance().layerTreeRoot().findLayer(layer).isVisible():
                    raster = True
                    break
            if raster and self.window:
                self.window = False
                demto3d_dlg = DEMto3D_dialog.DEMto3DDialog(self.iface)
                demto3d_dlg.exec_()
                canvas = self.iface.mapCanvas()
                if demto3d_dlg.extent:
                    canvas.scene().removeItem(demto3d_dlg.extent)
                if demto3d_dlg.divisions:
                    canvas.scene().removeItem(demto3d_dlg.divisions)
                self.window = True
            elif not raster:
                QMessageBox.information(self.iface.mainWindow(), "DEMto3D", self.tr("No visible raster layer loaded"))
        elif not layers:
            QMessageBox.information(self.iface.mainWindow(), "DEMto3D", self.tr("No visible raster layer loaded"))
