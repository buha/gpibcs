# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/doc-browser.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_docBrowser(object):
    def setupUi(self, docBrowser):
        docBrowser.setObjectName("docBrowser")
        docBrowser.resize(480, 640)
        self.verticalLayout = QtWidgets.QVBoxLayout(docBrowser)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebEngineWidgets.QWebEngineView(docBrowser)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)

        self.retranslateUi(docBrowser)
        QtCore.QMetaObject.connectSlotsByName(docBrowser)

    def retranslateUi(self, docBrowser):
        _translate = QtCore.QCoreApplication.translate
        docBrowser.setWindowTitle(_translate("docBrowser", "User Manual"))

from PyQt5 import QtWebEngineWidgets
