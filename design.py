# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(607, 496)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.canvas = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.canvas.setEnabled(True)
        self.canvas.setMinimumSize(QtCore.QSize(0, 300))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(220, 220, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(220, 220, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(220, 220, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        self.canvas.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setBold(False)
        font.setWeight(50)
        self.canvas.setFont(font)
        self.canvas.setStyleSheet("")
        self.canvas.setFrameShape(QtWidgets.QFrame.Box)
        self.canvas.setFrameShadow(QtWidgets.QFrame.Raised)
        self.canvas.setLineWidth(1)
        self.canvas.setUndoRedoEnabled(False)
        self.canvas.setReadOnly(True)
        self.canvas.setPlainText("")
        self.canvas.setBackgroundVisible(False)
        self.canvas.setPlaceholderText("")
        self.canvas.setObjectName("canvas")
        self.verticalLayout_3.addWidget(self.canvas)
        self.commandEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.commandEdit.setStyleSheet("background-color: transparent; border: 1px solid grey;")
        self.commandEdit.setFrame(False)
        self.commandEdit.setClearButtonEnabled(False)
        self.commandEdit.setObjectName("commandEdit")
        self.verticalLayout_3.addWidget(self.commandEdit)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.queryButton = QtWidgets.QPushButton(self.centralwidget)
        self.queryButton.setObjectName("queryButton")
        self.verticalLayout.addWidget(self.queryButton)
        self.queryResponseButton = QtWidgets.QPushButton(self.centralwidget)
        self.queryResponseButton.setObjectName("queryResponseButton")
        self.verticalLayout.addWidget(self.queryResponseButton)
        spacerItem = QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.writeButton = QtWidgets.QPushButton(self.centralwidget)
        self.writeButton.setObjectName("writeButton")
        self.verticalLayout_2.addWidget(self.writeButton)
        self.readButton = QtWidgets.QPushButton(self.centralwidget)
        self.readButton.setObjectName("readButton")
        self.verticalLayout_2.addWidget(self.readButton)
        self.serialPollButton = QtWidgets.QPushButton(self.centralwidget)
        self.serialPollButton.setObjectName("serialPollButton")
        self.verticalLayout_2.addWidget(self.serialPollButton)
        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setObjectName("clearButton")
        self.verticalLayout_2.addWidget(self.clearButton)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.sidePanelButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidePanelButton.sizePolicy().hasHeightForWidth())
        self.sidePanelButton.setSizePolicy(sizePolicy)
        self.sidePanelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sidePanelButton.setMaximumSize(QtCore.QSize(14, 16777215))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans Unicode")
        font.setPointSize(5)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.sidePanelButton.setFont(font)
        self.sidePanelButton.setCheckable(True)
        self.sidePanelButton.setChecked(False)
        self.sidePanelButton.setFlat(False)
        self.sidePanelButton.setObjectName("sidePanelButton")
        self.horizontalLayout_3.addWidget(self.sidePanelButton)
        self.sidePanel = QtWidgets.QWidget(self.centralwidget)
        self.sidePanel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidePanel.sizePolicy().hasHeightForWidth())
        self.sidePanel.setSizePolicy(sizePolicy)
        self.sidePanel.setMinimumSize(QtCore.QSize(400, 0))
        self.sidePanel.setMaximumSize(QtCore.QSize(400, 16777215))
        self.sidePanel.setStyleSheet("")
        self.sidePanel.setObjectName("sidePanel")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.sidePanel)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.sidePanelLayout = QtWidgets.QVBoxLayout()
        self.sidePanelLayout.setObjectName("sidePanelLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sequenceBox = QtWidgets.QComboBox(self.sidePanel)
        self.sequenceBox.setObjectName("sequenceBox")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/document-open.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sequenceBox.addItem(icon, "")
        self.horizontalLayout.addWidget(self.sequenceBox)
        self.saveButton = QtWidgets.QToolButton(self.sidePanel)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/document-save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon1)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.saveAsButton = QtWidgets.QToolButton(self.sidePanel)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/document-save-as.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveAsButton.setIcon(icon2)
        self.saveAsButton.setArrowType(QtCore.Qt.NoArrow)
        self.saveAsButton.setObjectName("saveAsButton")
        self.horizontalLayout.addWidget(self.saveAsButton)
        self.sidePanelLayout.addLayout(self.horizontalLayout)
        self.tableWidget = QCustomTableWidget(self.sidePanel)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.tableWidget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideLeft)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(QtCore.Qt.DotLine)
        self.tableWidget.setCornerButtonEnabled(True)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.sidePanelLayout.addWidget(self.tableWidget)
        self.runButton = QtWidgets.QPushButton(self.sidePanel)
        self.runButton.setObjectName("runButton")
        self.sidePanelLayout.addWidget(self.runButton)
        self.gridLayout_2.addLayout(self.sidePanelLayout, 0, 0, 1, 1)
        self.horizontalLayout_3.addWidget(self.sidePanel)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GPIB Tester"))
        self.commandEdit.setPlaceholderText(_translate("MainWindow", "Example: F, Ft ..."))
        self.queryButton.setText(_translate("MainWindow", "ibwrt | ibrd"))
        self.queryResponseButton.setText(_translate("MainWindow", "ibwrt |ibrsp"))
        self.writeButton.setText(_translate("MainWindow", "ibwrt"))
        self.readButton.setText(_translate("MainWindow", "ibrd"))
        self.serialPollButton.setText(_translate("MainWindow", "ibrsp"))
        self.clearButton.setText(_translate("MainWindow", "ibclr"))
        self.sidePanelButton.setText(_translate("MainWindow", ">\n"
">\n"
">\n"
"", "More"))
        self.sequenceBox.setItemText(0, _translate("MainWindow", "Load sequence ..."))
        self.saveButton.setToolTip(_translate("MainWindow", "Save"))
        self.saveButton.setText(_translate("MainWindow", "S"))
        self.saveAsButton.setToolTip(_translate("MainWindow", "Save As"))
        self.saveAsButton.setText(_translate("MainWindow", "..."))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "action"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "command"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "timeout"))
        self.runButton.setText(_translate("MainWindow", "Run"))

from qcustomtablewidget import QCustomTableWidget
