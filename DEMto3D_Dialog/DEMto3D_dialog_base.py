# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DEMto3D_Dialog\DEMto3D_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DEMto3DDialogBase(object):
    def setupUi(self, DEMto3DDialogBase):
        DEMto3DDialogBase.setObjectName("DEMto3DDialogBase")
        DEMto3DDialogBase.setWindowModality(QtCore.Qt.WindowModal)
        DEMto3DDialogBase.resize(465, 619)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/demto3d.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DEMto3DDialogBase.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(DEMto3DDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(DEMto3DDialogBase)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -30, 426, 551))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mMapLayerComboBox = QgsMapLayerComboBox(self.groupBox)
        self.mMapLayerComboBox.setShowCrs(True)
        self.mMapLayerComboBox.setObjectName("mMapLayerComboBox")
        self.verticalLayout_2.addWidget(self.mMapLayerComboBox)
        self.verticalLayout_8.addWidget(self.groupBox)
        self.groupBox_1 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_1.setObjectName("groupBox_1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.LimitsAbsGframe = QtWidgets.QFrame(self.groupBox_1)
        self.LimitsAbsGframe.setObjectName("LimitsAbsGframe")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.LimitsAbsGframe)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self._3 = QtWidgets.QGridLayout()
        self._3.setObjectName("_3")
        self.label_3 = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label_3.setObjectName("label_3")
        self._3.addWidget(self.label_3, 0, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label_5.setObjectName("label_5")
        self._3.addWidget(self.label_5, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label_2.setObjectName("label_2")
        self._3.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/downleft.png"))
        self.label_4.setObjectName("label_4")
        self._3.addWidget(self.label_4, 1, 0, 1, 1)
        self.YMaxLineEdit = QtWidgets.QLineEdit(self.LimitsAbsGframe)
        self.YMaxLineEdit.setObjectName("YMaxLineEdit")
        self._3.addWidget(self.YMaxLineEdit, 0, 4, 1, 1)
        self.XMinLineEdit = QtWidgets.QLineEdit(self.LimitsAbsGframe)
        self.XMinLineEdit.setObjectName("XMinLineEdit")
        self._3.addWidget(self.XMinLineEdit, 1, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label_6.setObjectName("label_6")
        self._3.addWidget(self.label_6, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.LimitsAbsGframe)
        self.label.setPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/upright.png"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self._3.addWidget(self.label, 0, 0, 1, 1)
        self.XMaxLineEdit = QtWidgets.QLineEdit(self.LimitsAbsGframe)
        self.XMaxLineEdit.setObjectName("XMaxLineEdit")
        self._3.addWidget(self.XMaxLineEdit, 0, 2, 1, 1)
        self.YMinLineEdit = QtWidgets.QLineEdit(self.LimitsAbsGframe)
        self.YMinLineEdit.setObjectName("YMinLineEdit")
        self._3.addWidget(self.YMinLineEdit, 1, 4, 1, 1)
        self.verticalLayout_7.addLayout(self._3)
        self.verticalLayout_3.addWidget(self.LimitsAbsGframe)
        self.LimitsParamGframe = QtWidgets.QWidget(self.groupBox_1)
        self.LimitsParamGframe.setObjectName("LimitsParamGframe")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.LimitsParamGframe)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_20 = QtWidgets.QLabel(self.LimitsParamGframe)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_2.addWidget(self.label_20)
        self.WidthGeoLineEdit = QtWidgets.QLineEdit(self.LimitsParamGframe)
        self.WidthGeoLineEdit.setObjectName("WidthGeoLineEdit")
        self.horizontalLayout_2.addWidget(self.WidthGeoLineEdit)
        self.label_22 = QtWidgets.QLabel(self.LimitsParamGframe)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_2.addWidget(self.label_22)
        self.HeightGeoLineEdit = QtWidgets.QLineEdit(self.LimitsParamGframe)
        self.HeightGeoLineEdit.setObjectName("HeightGeoLineEdit")
        self.horizontalLayout_2.addWidget(self.HeightGeoLineEdit)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.LimitsParamGframe)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.RotationCheckBox = QtWidgets.QCheckBox(self.groupBox_1)
        self.RotationCheckBox.setObjectName("RotationCheckBox")
        self.horizontalLayout.addWidget(self.RotationCheckBox)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.FullExtToolButton = QtWidgets.QToolButton(self.groupBox_1)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/zoom-extent.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.FullExtToolButton.setIcon(icon1)
        self.FullExtToolButton.setObjectName("FullExtToolButton")
        self.horizontalLayout.addWidget(self.FullExtToolButton)
        self.LayerExtToolButton = QtWidgets.QToolButton(self.groupBox_1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/zoom-layer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.LayerExtToolButton.setIcon(icon2)
        self.LayerExtToolButton.setObjectName("LayerExtToolButton")
        self.horizontalLayout.addWidget(self.LayerExtToolButton)
        self.CustomExtToolButton = QtWidgets.QToolButton(self.groupBox_1)
        self.CustomExtToolButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/plugins/DEMto3D/icons/zoom-region.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CustomExtToolButton.setIcon(icon3)
        self.CustomExtToolButton.setObjectName("CustomExtToolButton")
        self.horizontalLayout.addWidget(self.CustomExtToolButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_8.addWidget(self.groupBox_1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.SpacingLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.SpacingLineEdit.setObjectName("SpacingLineEdit")
        self.horizontalLayout_6.addWidget(self.SpacingLineEdit)
        self.label18 = QtWidgets.QLabel(self.groupBox_3)
        self.label18.setObjectName("label18")
        self.horizontalLayout_6.addWidget(self.label18)
        self.RecomSpacinglabel = QtWidgets.QLabel(self.groupBox_3)
        self.RecomSpacinglabel.setMinimumSize(QtCore.QSize(47, 20))
        self.RecomSpacinglabel.setObjectName("RecomSpacinglabel")
        self.horizontalLayout_6.addWidget(self.RecomSpacinglabel)
        self.gridLayout_3.addLayout(self.horizontalLayout_6, 0, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox_3)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 3, 0, 1, 1)
        self.ScaleLineEdit = QgsScaleWidget(self.groupBox_3)
        self.ScaleLineEdit.setObjectName("ScaleLineEdit")
        self.gridLayout_3.addWidget(self.ScaleLineEdit, 3, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 0, 1, 1)
        self.ZScaleDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.ZScaleDoubleSpinBox.setDecimals(3)
        self.ZScaleDoubleSpinBox.setMaximum(10.0)
        self.ZScaleDoubleSpinBox.setSingleStep(0.1)
        self.ZScaleDoubleSpinBox.setProperty("value", 1.0)
        self.ZScaleDoubleSpinBox.setObjectName("ZScaleDoubleSpinBox")
        self.gridLayout_3.addWidget(self.ZScaleDoubleSpinBox, 4, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.groupBox_3)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 4, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 1, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 2, 0, 1, 1)
        self.WidthLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WidthLineEdit.sizePolicy().hasHeightForWidth())
        self.WidthLineEdit.setSizePolicy(sizePolicy)
        self.WidthLineEdit.setObjectName("WidthLineEdit")
        self.gridLayout_3.addWidget(self.WidthLineEdit, 1, 1, 1, 1)
        self.HeightLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.HeightLineEdit.sizePolicy().hasHeightForWidth())
        self.HeightLineEdit.setSizePolicy(sizePolicy)
        self.HeightLineEdit.setObjectName("HeightLineEdit")
        self.gridLayout_3.addWidget(self.HeightLineEdit, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 5, 0, 1, 1)
        self.RevereseZCheckBox = QtWidgets.QCheckBox(self.groupBox_3)
        self.RevereseZCheckBox.setObjectName("RevereseZCheckBox")
        self.gridLayout_3.addWidget(self.RevereseZCheckBox, 5, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_3)
        self.verticalLayout_8.addWidget(self.groupBox_3)
        self.groupBox_5 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.BaseHeightLineEdit = QtWidgets.QLineEdit(self.groupBox_5)
        self.BaseHeightLineEdit.setMaximumSize(QtCore.QSize(85, 16777215))
        self.BaseHeightLineEdit.setObjectName("BaseHeightLineEdit")
        self.gridLayout_2.addWidget(self.BaseHeightLineEdit, 0, 1, 1, 1)
        self.HeightModelLabel = QtWidgets.QLabel(self.groupBox_5)
        self.HeightModelLabel.setObjectName("HeightModelLabel")
        self.gridLayout_2.addWidget(self.HeightModelLabel, 1, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.groupBox_5)
        self.label_21.setObjectName("label_21")
        self.gridLayout_2.addWidget(self.label_21, 1, 0, 1, 1)
        self.ZMaxLabel = QtWidgets.QLabel(self.groupBox_5)
        self.ZMaxLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ZMaxLabel.setObjectName("ZMaxLabel")
        self.gridLayout_2.addWidget(self.ZMaxLabel, 1, 3, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_5)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 1, 2, 1, 1)
        self.ZMinLabel = QtWidgets.QLabel(self.groupBox_5)
        self.ZMinLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ZMinLabel.setObjectName("ZMinLabel")
        self.gridLayout_2.addWidget(self.ZMinLabel, 0, 3, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.groupBox_5)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 0, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 0, 2, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
        self.verticalLayout_8.addWidget(self.groupBox_5)
        self.groupBox_2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)
        self.ColPartsSpinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.ColPartsSpinBox.setMinimum(1)
        self.ColPartsSpinBox.setProperty("value", 1)
        self.ColPartsSpinBox.setObjectName("ColPartsSpinBox")
        self.gridLayout.addWidget(self.ColPartsSpinBox, 0, 3, 1, 1)
        self.RowPartsSpinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.RowPartsSpinBox.setMinimum(1)
        self.RowPartsSpinBox.setProperty("value", 1)
        self.RowPartsSpinBox.setObjectName("RowPartsSpinBox")
        self.gridLayout.addWidget(self.RowPartsSpinBox, 0, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        self.label_14.setMaximumSize(QtCore.QSize(15, 20))
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 0, 2, 1, 1)
        self.verticalLayout_8.addWidget(self.groupBox_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.progressLayoutV = QtWidgets.QVBoxLayout()
        self.progressLayoutV.setObjectName("progressLayoutV")
        self.ProgressLabel = QtWidgets.QLabel(DEMto3DDialogBase)
        self.ProgressLabel.setObjectName("ProgressLabel")
        self.progressLayoutV.addWidget(self.ProgressLabel)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.progressBar = QtWidgets.QProgressBar(DEMto3DDialogBase)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_3.addWidget(self.progressBar)
        self.cancelProgressToolButton = QtWidgets.QToolButton(DEMto3DDialogBase)
        self.cancelProgressToolButton.setEnabled(False)
        self.cancelProgressToolButton.setMinimumSize(QtCore.QSize(100, 0))
        self.cancelProgressToolButton.setObjectName("cancelProgressToolButton")
        self.horizontalLayout_3.addWidget(self.cancelProgressToolButton)
        self.progressLayoutV.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.progressLayoutV)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.ParamPushButton = QtWidgets.QPushButton(DEMto3DDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ParamPushButton.sizePolicy().hasHeightForWidth())
        self.ParamPushButton.setSizePolicy(sizePolicy)
        self.ParamPushButton.setMinimumSize(QtCore.QSize(100, 25))
        self.ParamPushButton.setAutoDefault(False)
        self.ParamPushButton.setObjectName("ParamPushButton")
        self.horizontalLayout_9.addWidget(self.ParamPushButton)
        spacerItem2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.STLToolButton = QtWidgets.QToolButton(DEMto3DDialogBase)
        self.STLToolButton.setMinimumSize(QtCore.QSize(100, 25))
        self.STLToolButton.setMaximumSize(QtCore.QSize(100, 25))
        self.STLToolButton.setObjectName("STLToolButton")
        self.horizontalLayout_9.addWidget(self.STLToolButton)
        self.CancelToolButton = QtWidgets.QToolButton(DEMto3DDialogBase)
        self.CancelToolButton.setMinimumSize(QtCore.QSize(100, 25))
        self.CancelToolButton.setMaximumSize(QtCore.QSize(100, 25))
        self.CancelToolButton.setObjectName("CancelToolButton")
        self.horizontalLayout_9.addWidget(self.CancelToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.label_3.setBuddy(self.YMaxLineEdit)
        self.label_5.setBuddy(self.XMinLineEdit)
        self.label_2.setBuddy(self.XMaxLineEdit)
        self.label_6.setBuddy(self.YMinLineEdit)
        self.label_9.setBuddy(self.SpacingLineEdit)
        self.label_16.setBuddy(self.ZScaleDoubleSpinBox)
        self.label_12.setBuddy(self.WidthLineEdit)
        self.label_13.setBuddy(self.HeightLineEdit)
        self.label_7.setBuddy(self.RevereseZCheckBox)
        self.label_17.setBuddy(self.BaseHeightLineEdit)

        self.retranslateUi(DEMto3DDialogBase)
        self.RotationCheckBox.clicked['bool'].connect(self.LimitsParamGframe.setVisible)
        QtCore.QMetaObject.connectSlotsByName(DEMto3DDialogBase)
        DEMto3DDialogBase.setTabOrder(self.mMapLayerComboBox, self.XMaxLineEdit)
        DEMto3DDialogBase.setTabOrder(self.XMaxLineEdit, self.YMaxLineEdit)
        DEMto3DDialogBase.setTabOrder(self.YMaxLineEdit, self.XMinLineEdit)
        DEMto3DDialogBase.setTabOrder(self.XMinLineEdit, self.YMinLineEdit)
        DEMto3DDialogBase.setTabOrder(self.YMinLineEdit, self.FullExtToolButton)
        DEMto3DDialogBase.setTabOrder(self.FullExtToolButton, self.LayerExtToolButton)
        DEMto3DDialogBase.setTabOrder(self.LayerExtToolButton, self.CustomExtToolButton)
        DEMto3DDialogBase.setTabOrder(self.CustomExtToolButton, self.SpacingLineEdit)
        DEMto3DDialogBase.setTabOrder(self.SpacingLineEdit, self.WidthLineEdit)
        DEMto3DDialogBase.setTabOrder(self.WidthLineEdit, self.HeightLineEdit)
        DEMto3DDialogBase.setTabOrder(self.HeightLineEdit, self.ZScaleDoubleSpinBox)
        DEMto3DDialogBase.setTabOrder(self.ZScaleDoubleSpinBox, self.RevereseZCheckBox)
        DEMto3DDialogBase.setTabOrder(self.RevereseZCheckBox, self.BaseHeightLineEdit)
        DEMto3DDialogBase.setTabOrder(self.BaseHeightLineEdit, self.ParamPushButton)
        DEMto3DDialogBase.setTabOrder(self.ParamPushButton, self.STLToolButton)
        DEMto3DDialogBase.setTabOrder(self.STLToolButton, self.CancelToolButton)

    def retranslateUi(self, DEMto3DDialogBase):
        _translate = QtCore.QCoreApplication.translate
        DEMto3DDialogBase.setWindowTitle(_translate("DEMto3DDialogBase", "DEM 3D printing"))
        self.groupBox.setTitle(_translate("DEMto3DDialogBase", "Layer to print"))
        self.groupBox_1.setTitle(_translate("DEMto3DDialogBase", "Print extent"))
        self.label_3.setText(_translate("DEMto3DDialogBase", "Y:"))
        self.label_5.setText(_translate("DEMto3DDialogBase", "X:"))
        self.label_2.setText(_translate("DEMto3DDialogBase", "X:"))
        self.label_6.setText(_translate("DEMto3DDialogBase", "Y:"))
        self.label_20.setText(_translate("DEMto3DDialogBase", "Width:"))
        self.label_22.setText(_translate("DEMto3DDialogBase", "Lenght:"))
        self.RotationCheckBox.setText(_translate("DEMto3DDialogBase", "Show width/length"))
        self.FullExtToolButton.setToolTip(_translate("DEMto3DDialogBase", "Select full extent"))
        self.FullExtToolButton.setStatusTip(_translate("DEMto3DDialogBase", "Select full extent"))
        self.FullExtToolButton.setWhatsThis(_translate("DEMto3DDialogBase", "Select full extent"))
        self.FullExtToolButton.setAccessibleName(_translate("DEMto3DDialogBase", "Select full extent"))
        self.LayerExtToolButton.setToolTip(_translate("DEMto3DDialogBase", "Select layer extent"))
        self.LayerExtToolButton.setStatusTip(_translate("DEMto3DDialogBase", "Select layer extent"))
        self.LayerExtToolButton.setWhatsThis(_translate("DEMto3DDialogBase", "Select layer extent"))
        self.LayerExtToolButton.setAccessibleName(_translate("DEMto3DDialogBase", "Select layer extent"))
        self.CustomExtToolButton.setToolTip(_translate("DEMto3DDialogBase", "Draw extent"))
        self.CustomExtToolButton.setStatusTip(_translate("DEMto3DDialogBase", "Draw extent"))
        self.CustomExtToolButton.setWhatsThis(_translate("DEMto3DDialogBase", "Draw extent"))
        self.CustomExtToolButton.setAccessibleName(_translate("DEMto3DDialogBase", "Draw extent"))
        self.groupBox_3.setTitle(_translate("DEMto3DDialogBase", "Model size"))
        self.label18.setText(_translate("DEMto3DDialogBase", "Recommended"))
        self.RecomSpacinglabel.setText(_translate("DEMto3DDialogBase", "0.2 mm"))
        self.label_15.setText(_translate("DEMto3DDialogBase", "Scale:"))
        self.label_9.setText(_translate("DEMto3DDialogBase", "Spacing (mm):"))
        self.ZScaleDoubleSpinBox.setPrefix(_translate("DEMto3DDialogBase", "x "))
        self.label_16.setText(_translate("DEMto3DDialogBase", "Vertical exaggeration:"))
        self.label_12.setText(_translate("DEMto3DDialogBase", "Width (mm):"))
        self.label_13.setText(_translate("DEMto3DDialogBase", "Lenght (mm):"))
        self.label_7.setText(_translate("DEMto3DDialogBase", "Terrain inversion:"))
        self.RevereseZCheckBox.setText(_translate("DEMto3DDialogBase", "enable"))
        self.groupBox_5.setTitle(_translate("DEMto3DDialogBase", "Model height"))
        self.HeightModelLabel.setText(_translate("DEMto3DDialogBase", "0 mm"))
        self.label_21.setText(_translate("DEMto3DDialogBase", "Model height:"))
        self.ZMaxLabel.setText(_translate("DEMto3DDialogBase", "0 m"))
        self.label_10.setText(_translate("DEMto3DDialogBase", "Highest point:"))
        self.ZMinLabel.setText(_translate("DEMto3DDialogBase", "0 m"))
        self.label_17.setText(_translate("DEMto3DDialogBase", "Height (m):"))
        self.label_8.setText(_translate("DEMto3DDialogBase", "Lowest point:"))
        self.groupBox_2.setTitle(_translate("DEMto3DDialogBase", "Divide Model"))
        self.label_11.setText(_translate("DEMto3DDialogBase", "Parts:"))
        self.ColPartsSpinBox.setSuffix(_translate("DEMto3DDialogBase", " column"))
        self.RowPartsSpinBox.setSuffix(_translate("DEMto3DDialogBase", " row"))
        self.label_14.setText(_translate("DEMto3DDialogBase", "X"))
        self.ProgressLabel.setText(_translate("DEMto3DDialogBase", "TextLabel..."))
        self.cancelProgressToolButton.setText(_translate("DEMto3DDialogBase", "Cancel"))
        self.ParamPushButton.setText(_translate("DEMto3DDialogBase", "Settings"))
        self.STLToolButton.setText(_translate("DEMto3DDialogBase", "Export to STL"))
        self.CancelToolButton.setText(_translate("DEMto3DDialogBase", "Close"))

from qgsmaplayercombobox import QgsMapLayerComboBox
from qgsscalewidget import QgsScaleWidget
