# -*- coding: utf-8 -*-
"""
RectangleMapTool - extracted from DEMto3D_dialog.py
"""
import math
from typing import Any, Callable, Optional

from qgis.core import Qgis, QgsPointXY
from qgis.gui import QgsMapCanvas, QgsMapTool, QgsRubberBand
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication

from .geometry_utils import getPointsFromRectangleParams, rectangleHWCenterFrom2pCreate

geometryType = Qgis.GeometryType.Line


class RectangleMapTool(QgsMapTool):

    square_mode: bool = False
    startPoint: Optional[QgsPointXY] = None
    endPoint: Optional[QgsPointXY] = None
    isEmittingPoint: bool = True
    rotation: float = 0.0

    def __init__(self, canvas: QgsMapCanvas, callback: Callable[[dict], None]) -> None:
        super().__init__(canvas)
        self.canvas: QgsMapCanvas = canvas
        self.callback: Callable[[dict], None] = callback
        self.rubberBand: QgsRubberBand = QgsRubberBand(self.canvas, geometryType)
        self.rubberBand.setColor(QColor(227, 26, 28, 255))
        self.rubberBand.setWidth(3)
        self.rubberBand.setLineStyle(Qt.PenStyle(Qt.DashLine))
        self.rotation: float = self.canvas.rotation() * math.pi / 180
        self.reset()

    def reset(self) -> None:
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(geometryType)

    def canvasPressEvent(self, e: Any) -> None:
        assert e is not None
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e: Any) -> Optional[None]:
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.rubberBand.hide()
            self.callback(r)
        return None

    def canvasMoveEvent(self, e: Any) -> None:
        if not self.isEmittingPoint:
            return
        assert e is not None
        self.endPoint = self.toMapCoordinates(e.pos())
        # Dynamically check shift key state
        self.square_mode = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)
        if self.startPoint is not None and self.endPoint is not None:
            self.showRect(self.startPoint, self.endPoint)

    def keyReleaseEvent(self, e: Any) -> None:
        if e.key() == Qt.Key_Shift and self.square_mode:
            self.square_mode = False
            # Redraw as rectangle if currently drawing
            if (
                self.isEmittingPoint
                and self.startPoint is not None
                and self.endPoint is not None
            ):
                self.showRect(self.startPoint, self.endPoint)
        super().keyReleaseEvent(e)

    def showRect(
        self,
        start_point: QgsPointXY,
        end_point: QgsPointXY,
    ) -> None:
        self.rubberBand.reset(geometryType)
        if start_point is None or end_point is None:
            return
        # Use square mode if enabled
        if self.square_mode:
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()
            side = max(abs(dx), abs(dy))
            end_x = start_point.x() + side * (1 if dx >= 0 else -1)
            end_y = start_point.y() + side * (1 if dy >= 0 else -1)
            end_point = QgsPointXY(end_x, end_y)
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return
        rectParams = rectangleHWCenterFrom2pCreate(
            start_point, end_point, self.rotation
        )
        points = getPointsFromRectangleParams(rectParams)
        self.rubberBand.addPoint(QgsPointXY(points[0][0], points[0][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[1][0], points[1][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[2][0], points[2][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[3][0], points[3][1]), False)
        self.rubberBand.addPoint(QgsPointXY(points[0][0], points[0][1]), True)
        self.rubberBand.show()

    def rectangle(self) -> Optional[dict]:
        if self.startPoint is None or self.endPoint is None:
            return None
        if (
            self.startPoint.x() == self.endPoint.x()
            or self.startPoint.y() == self.endPoint.y()
        ):
            return None
        if self.square_mode:
            dx = self.endPoint.x() - self.startPoint.x()
            dy = self.endPoint.y() - self.startPoint.y()
            side = max(abs(dx), abs(dy))
            end_x = self.startPoint.x() + side * (1 if dx >= 0 else -1)
            end_y = self.startPoint.y() + side * (1 if dy >= 0 else -1)
            self.endPoint = QgsPointXY(end_x, end_y)
        rectParams = rectangleHWCenterFrom2pCreate(
            self.startPoint, self.endPoint, self.rotation
        )
        return rectParams
