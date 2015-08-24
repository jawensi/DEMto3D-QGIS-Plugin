# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DEMto3D
                                 A QGIS plugin
 Impresión 3D de MDE
                             -------------------
        begin                : 2015-08-02
        copyright            : (C) 2015 by Francisco Javier Venceslá Simón
        email                : demto3d@gmail.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DEMto3D class from file DEMto3D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .DEMto3D import DEMto3D
    return DEMto3D(iface)
