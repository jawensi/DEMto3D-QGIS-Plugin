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

from __future__ import absolute_import

import logging
import math
import os
import time

from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from ..model_builder.Model_Builder import Model
from ..model_builder.STL_Builder import STL
from .geometry_utils import ParametersDict


class Export(QDialog):
    start_time: float = 0
    ModelBuilder: Model = None  # type: ignore
    STLBuilder: STL = None  # type: ignore

    def __init__(self, mainDialog, parameters: ParametersDict, file_name: str) -> None:
        # Import here to avoid circular import
        from .DEMto3D_dialog import DEMto3DDialog

        QDialog.__init__(self)
        self.mainDlg: DEMto3DDialog = mainDialog
        self.parameters: ParametersDict = parameters
        self.stl_file: str = file_name
        self.prepareUi(True)
        self.do_model()

    def do_model(self) -> None:
        self.start_time = time.perf_counter()
        maxVal = int(
            math.ceil(self.parameters["height"] / self.parameters["spacing_mm"]) + 1
        )
        self.mainDlg.ui.progressBar.setMaximum(maxVal)
        self.mainDlg.ui.progressBar.setValue(0)
        self.mainDlg.ui.cancelProgressToolButton.clicked.connect(self.cancel_model)
        self.mainDlg.ui.ProgressLabel.setText(self.tr("Building STL geometry"))

        self.ModelBuilder = Model(self.parameters)
        self.ModelBuilder.updateProgress.connect(
            lambda: self.mainDlg.ui.progressBar.setValue(
                self.mainDlg.ui.progressBar.value() + 1
            )
        )
        self.ModelBuilder.finished.connect(self.do_stl_model)
        self.ModelBuilder.start()

    def cancel_model(self) -> None:
        self.ModelBuilder.quit = True

    def do_stl_model(self) -> None:
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        logging.info("Tiempo transcurrido (I): %s segundos", elapsed_time)
        self.start_time = time.perf_counter()
        self.mainDlg.ui.progressBar.setValue(0)
        if self.ModelBuilder.quit:
            self.prepareUi(False)
            QMessageBox.information(
                self.mainDlg,
                self.mainDlg.tr("Attention"),
                self.mainDlg.tr("Process cancelled"),
            )
        else:
            self.mainDlg.ui.cancelProgressToolButton.clicked.connect(
                self.cancel_stl_model
            )
            self.mainDlg.ui.ProgressLabel.setText(self.tr("Creating STL file"))
            dem_matrix = self.ModelBuilder.get_model()
            rows, cols = dem_matrix.shape[:2]
            maxVal = rows * cols * 2
            self.mainDlg.ui.progressBar.setMaximum(maxVal)

            self.STLBuilder = STL(self.parameters, self.stl_file, dem_matrix)
            self.STLBuilder.updateProgress.connect(
                lambda: self.mainDlg.ui.progressBar.setValue(
                    self.mainDlg.ui.progressBar.value() + 1
                )
            )
            self.STLBuilder.finished.connect(self.finish_model)
            self.STLBuilder.start()

    def cancel_stl_model(self) -> None:
        self.STLBuilder.quit = True

    def finish_model(self) -> None:
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        logging.info("Tiempo transcurrido (II): %s segundos", elapsed_time)
        self.prepareUi(False)
        self.mainDlg.ui.progressBar.setValue(0)
        if self.STLBuilder.quit:
            os.remove(self.stl_file)
            QMessageBox.information(
                self.mainDlg,
                self.mainDlg.tr("Attention"),
                self.mainDlg.tr("Process cancelled"),
            )
        else:
            QMessageBox.information(
                self.mainDlg,
                self.mainDlg.tr("Attention"),
                self.mainDlg.tr("STL model generated"),
            )

    def prepareUi(self, start: bool) -> None:
        if start:
            self.mainDlg.ui.ProgressLabel.show()
        else:
            self.mainDlg.ui.ProgressLabel.hide()
        self.mainDlg.ui.cancelProgressToolButton.setEnabled(start)
        self.mainDlg.ui.groupBox.setEnabled(not start)
        self.mainDlg.ui.groupBox_1.setEnabled(not start)
        self.mainDlg.ui.groupBox_3.setEnabled(not start)
        self.mainDlg.ui.groupBox_5.setEnabled(not start)
        self.mainDlg.ui.ParamPushButton.setEnabled(not start)
        self.mainDlg.ui.STLToolButton.setEnabled(not start)
        self.mainDlg.ui.ParamPushButton.setEnabled(not start)
        self.mainDlg.ui.CancelToolButton.setEnabled(not start)
        self.mainDlg.ui.CancelToolButton.setEnabled(not start)
        self.mainDlg.ui.CancelToolButton.setEnabled(not start)
        self.mainDlg.ui.CancelToolButton.setEnabled(not start)
