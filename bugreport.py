# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/bug-report.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_bugReportDialog(object):
    def setupUi(self, bugReportDialog):
        bugReportDialog.setObjectName("bugReportDialog")
        bugReportDialog.resize(450, 142)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(bugReportDialog.sizePolicy().hasHeightForWidth())
        bugReportDialog.setSizePolicy(sizePolicy)
        bugReportDialog.setMinimumSize(QtCore.QSize(0, 100))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/gpibcs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        bugReportDialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(bugReportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.bugFileLabel = QtWidgets.QLabel(bugReportDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.bugFileLabel.setFont(font)
        self.bugFileLabel.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.bugFileLabel.setText("")
        self.bugFileLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bugFileLabel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.bugFileLabel.setObjectName("bugFileLabel")
        self.verticalLayout.addWidget(self.bugFileLabel)
        self.bugFileLink = QtWidgets.QCommandLinkButton(bugReportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bugFileLink.sizePolicy().hasHeightForWidth())
        self.bugFileLink.setSizePolicy(sizePolicy)
        self.bugFileLink.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.bugFileLink.setObjectName("bugFileLink")
        self.verticalLayout.addWidget(self.bugFileLink)
        self.bugReportLink = QtWidgets.QCommandLinkButton(bugReportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bugReportLink.sizePolicy().hasHeightForWidth())
        self.bugReportLink.setSizePolicy(sizePolicy)
        self.bugReportLink.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.bugReportLink.setObjectName("bugReportLink")
        self.verticalLayout.addWidget(self.bugReportLink)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(bugReportDialog)
        QtCore.QMetaObject.connectSlotsByName(bugReportDialog)

    def retranslateUi(self, bugReportDialog):
        _translate = QtCore.QCoreApplication.translate
        bugReportDialog.setWindowTitle(_translate("bugReportDialog", "gpibcs | Bug Report"))
        self.bugFileLink.setText(_translate("bugReportDialog", "Open containing folder"))
        self.bugReportLink.setText(_translate("bugReportDialog", "File bug report in browser"))

