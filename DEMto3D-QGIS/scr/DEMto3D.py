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
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMessageBox
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from DEMto3D_Dialog import DEMto3D_dialog
import os.path


class DEMto3D:
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
        # try:
        #     _encoding = QtGui.QApplication.UnicodeUTF8
        #     return QCoreApplication.translate('DEMto3D', message, None, _encoding)
        # except AttributeError:
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

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(self.menu, self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        layers = self.iface.legendInterface().layers()
        raster = False
        if layers:
            for layer in layers:
                if layer.type() == 1 and self.iface.legendInterface().isLayerVisible(layer):
                    raster = True
                    break
            if raster and self.window:
                self.window = False
                demto3d_dlg = DEMto3D_dialog.DEMto3DDialog(self.iface)
                if demto3d_dlg.exec_():
                    pass
                if demto3d_dlg.extension:
                    canvas = self.iface.mapCanvas()
                    canvas.scene().removeItem(demto3d_dlg.extension)
                self.window = True
            elif not raster:
                QMessageBox.information(self.iface.mainWindow(), "DEMto3D", self.tr("No visible raster layer loaded"))
        elif not layers:
            QMessageBox.information(self.iface.mainWindow(), "DEMto3D", self.tr("No layer loaded"))
