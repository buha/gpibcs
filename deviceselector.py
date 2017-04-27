# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/device-selector.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_deviceDialog(object):
    def setupUi(self, deviceDialog):
        deviceDialog.setObjectName("deviceDialog")
        deviceDialog.resize(353, 73)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/gpibcs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        deviceDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(deviceDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(deviceDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.selector = QtWidgets.QComboBox(deviceDialog)
        self.selector.setObjectName("selector")
        self.verticalLayout.addWidget(self.selector)

        self.retranslateUi(deviceDialog)
        QtCore.QMetaObject.connectSlotsByName(deviceDialog)

    def retranslateUi(self, deviceDialog):
        _translate = QtCore.QCoreApplication.translate
        deviceDialog.setWindowTitle(_translate("deviceDialog", "gpibcs | device selection"))

