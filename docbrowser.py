from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWebEngineWidgets
import logging
import os

class DocBrowserDialog(QtWidgets.QDialog):
    closed = QtCore.pyqtSignal()

    def __init__(self, html):
        super().__init__()
        self.setWindowTitle("gpibcs | User Manual")
        self.setObjectName("docBrowser")
        self.resize(480, 640)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/gpibcs.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        logging.debug('creating QWebEngineView')
        self.webView = QtWebEngineWidgets.QWebEngineView(self)
        logging.debug('done creating QWebEngineView')
        logging.debug('setting name')
        self.webView.setObjectName("webView")
        logging.debug('adding to layout')
        self.verticalLayout.addWidget(self.webView)
        dir = os.path.dirname(html)
        logging.debug('load file {}'.format( os.path.realpath(html)))
        try:
            self.webView.load(QtCore.QUrl.fromLocalFile(os.path.realpath(html)))
        except Exception as e:
            logging.debug(e)

    def closeEvent(self, event):
        self.closed.emit()
