# -*- coding: utf-8 -*-
"""
Utility functions for rectangle and geometry operations used in DEMto3D.
"""

import math
from typing import Any, Dict, List

from qgis.core import QgsPointXY


def rectangle2pCreate(
    firstPoint: QgsPointXY, secondPoint: QgsPointXY, azimutO: float
) -> List[QgsPointXY]:
    templinePoint = QgsPointXY(
        secondPoint.x() + 10 * math.sin(azimutO),
        secondPoint.y() + 10 * math.cos(azimutO),
    )
    p1 = pointToLine2D(
        firstPoint.x(),
        firstPoint.y(),
        secondPoint.x(),
        secondPoint.y(),
        templinePoint.x(),
        templinePoint.y(),
    )
    tempLinePoint2 = QgsPointXY(
        firstPoint.x() + 10 * math.sin(azimutO), firstPoint.y() + 10 * math.cos(azimutO)
    )
    p3 = pointToLine2D(
        secondPoint.x(),
        secondPoint.y(),
        firstPoint.x(),
        firstPoint.y(),
        tempLinePoint2.x(),
        tempLinePoint2.y(),
    )
    azP1 = normalizeAngle(lineAzimut2p(firstPoint, p1))
    azP3 = normalizeAngle(lineAzimut2p(firstPoint, p3))
    azimut100 = normalizeAngle(azimutO + math.pi * 0.5)
    if abs(azP3 - azimutO) <= 0.000001:
        if abs(azP1 - azimut100) <= 0.000001:
            return [p1, firstPoint, p3, secondPoint]
        else:
            return [firstPoint, p1, secondPoint, p3]
    else:
        if abs(azP1 - azimut100) <= 0.000001:
            return [secondPoint, p3, firstPoint, p1]
        else:
            return [p3, secondPoint, p1, firstPoint]


def rectangleHWCenterFrom2pCreate(
    firstPoint: QgsPointXY, secondPoint: QgsPointXY, rotation: float
) -> Dict[str, Any]:
    templinePoint = getPolarPoint(secondPoint.x(), secondPoint.y(), rotation, 10)
    p1 = pointToLine2D(
        firstPoint.x(),
        firstPoint.y(),
        secondPoint.x(),
        secondPoint.y(),
        templinePoint[0],
        templinePoint[1],
    )
    ax = p1.x() - secondPoint.x()
    ay = p1.y() - secondPoint.y()
    width = math.sqrt(ax**2 + ay**2)
    ax = p1.x() - firstPoint.x()
    ay = p1.y() - firstPoint.y()
    height = math.sqrt(ax**2 + ay**2)
    centerX = (firstPoint.x() + secondPoint.x()) * 0.5
    centerY = (firstPoint.y() + secondPoint.y()) * 0.5
    return {
        "center": [centerX, centerY],
        "width": width,
        "height": height,
        "rotation": rotation,
    }


def getPointsFromRectangleParams(rectParam: Dict[str, Any]) -> List[List[float]]:
    center = rectParam["center"]
    width = rectParam["width"]
    height = rectParam["height"]
    rotation = rectParam["rotation"]
    auxPto = getPolarPoint(center[0], center[1], rotation, width * 0.5)
    p2 = getPolarPoint(auxPto[0], auxPto[1], rotation + math.pi * 0.5, height * 0.5)
    p1 = getPolarPoint(p2[0], p2[1], rotation + math.pi, width)
    p4 = getPolarPoint(p1[0], p1[1], rotation - math.pi * 0.5, height)
    p3 = getPolarPoint(p2[0], p2[1], rotation - math.pi * 0.5, height)
    return [p1, p2, p3, p4]


def pointToLine2D(
    px: float, py: float, x1: float, y1: float, x2: float, y2: float
) -> QgsPointXY:
    try:
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (
            (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
        )
        return QgsPointXY(x1 + u * (x2 - x1), y1 + u * (y2 - y1))
    except ZeroDivisionError as err:
        print("POINT In LINE:", err)
        return QgsPointXY(px, py)


def lineAzimut2p(v1: QgsPointXY, v2: QgsPointXY) -> float:
    return math.atan2(v2.x() - v1.x(), v2.y() - v1.y())


def normalizeAngle(angle: float) -> float:
    maxValue = math.pi * 2
    if abs(angle) <= 0.000001:
        return 0
    if abs(angle - maxValue) <= 0.000001:
        return maxValue
    if angle < 0:
        return angle % maxValue + maxValue
    if angle > maxValue:
        return angle % maxValue
    return angle


def getPolarPoint(x0: float, y0: float, angle: float, dist: float) -> List[float]:
    x = x0 + dist * math.cos(angle)
    y = y0 + dist * math.sin(angle)
    return [x, y]
