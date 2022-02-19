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
 This script initializes the plugin, making it known to QGIS.
"""


def classFactory(iface):
    """Load DEMto3D class from file DEMto3D.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .DEMto3D import DEMto3D
    return DEMto3D(iface)
