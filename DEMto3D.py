# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2025 by Javier
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
from typing import TYPE_CHECKING, Optional

from qgis.core import QgsApplication, QgsProject, QgsRasterLayer
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTimer, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from . import resources
from .DEMto3D_Dialog import DEMto3D_dialog

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


class DEMto3D:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: "QgisInterface") -> None:
        self.iface: "QgisInterface" = iface
        self.plugin_dir: str = os.path.dirname(__file__)
        self.menu = "&DEMto3D"
        self.action: Optional[QAction] = None
        self._translator: Optional[QTranslator] = None
        self._running: bool = False

        self._install_translator()

        # React to language change (QGIS >= 3.22)
        try:
            QgsApplication.localeChanged.connect(self._on_locale_changed)  # type: ignore
        except Exception:
            pass

    def _install_translator(self) -> None:
        """
        Install the appropriate .qm file according to current QGIS locale.
        """
        if self._translator:
            QCoreApplication.removeTranslator(self._translator)
            self._translator = None

        locale = QgsApplication.locale() or "en"
        lang = locale.split("_", 1)[0]

        qm_path = os.path.join(self.plugin_dir, "i18n", f"DEMto3D_{lang}.qm")
        if os.path.exists(qm_path):
            translator = QTranslator()
            if translator.load(qm_path):
                QCoreApplication.installTranslator(translator)
                self._translator = translator

    def _on_locale_changed(self):
        """
        Reinstall translator and update UI strings when QGIS locale changes.
        """
        self._install_translator()
        if self.action:
            text = self.tr("DEM 3D printing")
            self.action.setText(text)
            self.action.setStatusTip(text)

    def tr(self, message: str) -> str:
        """Translate a string using Qt's translation system."""
        return QCoreApplication.translate("DEMto3D", message)

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

        self._update_action_enabled()

        project = QgsProject.instance()
        assert project is not None
        root = project.layerTreeRoot()
        assert root is not None
        canvas = self.iface.mapCanvas()

        if canvas:
            canvas.layersChanged.connect(lambda *_: self._update_action_enabled())

        project.layersAdded.connect(lambda *_: self._update_action_enabled())
        project.layersRemoved.connect(lambda *_: self._update_action_enabled())
        root.addedChildren.connect(lambda *_: self._update_action_enabled())
        root.removedChildren.connect(lambda *_: self._update_action_enabled())
        try:
            root.visibilityChanged.connect(lambda *_: self._update_action_enabled())
        except Exception:
            pass

        QTimer.singleShot(0, self._update_action_enabled)

    def unload(self) -> None:
        """Remove UI elements when the plugin is disabled/uninstalled."""
        if self.action:
            self.iface.removePluginRasterMenu(self.menu, self.action)
            self.iface.removeRasterToolBarIcon(self.action)
            self.action = None

    def _has_visible_raster(self) -> bool:
        """
        Return True if there is at least one *visible* raster layer in the project.
        """
        project = QgsProject.instance()
        assert project is not None
        root = project.layerTreeRoot()
        assert root is not None

        for lyr in project.mapLayers().values():
            if isinstance(lyr, QgsRasterLayer):
                node = root.findLayer(lyr.id())
                if node is not None and node.isVisible():
                    return True
        return False

    def _update_action_enabled(self) -> None:
        """Enable/disable the action depending on whether a visible raster exists."""
        if self.action:
            self.action.setEnabled(self._has_visible_raster())

    def _cleanup_canvas_items(self, dlg: "DEMto3D_dialog.DEMto3DDialog") -> None:
        """
        Remove canvas overlays (extent/divisions) created by the dialog, if any.
        """
        canvas = self.iface.mapCanvas()
        if not canvas:
            return
        scene = canvas.scene()
        for attr in ("extent", "divisions"):
            item = getattr(dlg, attr, None)
            if item is not None:
                try:
                    scene.removeItem(item)  # type: ignore[arg-type]
                except Exception:
                    pass
                finally:
                    setattr(dlg, attr, None)

    def run(self) -> None:
        """
        Entry point for the plugin action.
        Prevents re-entry, ensures there's a visible raster, and opens dialog modally.
        """
        if self._running:
            return

        if not self._has_visible_raster():
            QMessageBox.information(
                self.iface.mainWindow(),
                "DEMto3D",
                self.tr("No visible raster layer loaded"),
            )
            return

        self._running = True
        demto3d_dlg = None
        try:
            demto3d_dlg = DEMto3D_dialog.DEMto3DDialog(self.iface)
            demto3d_dlg.exec_()
        finally:
            if demto3d_dlg is not None:
                self._cleanup_canvas_items(demto3d_dlg)
            self._running = False
            self._update_action_enabled()
