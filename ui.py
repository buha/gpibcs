import sys
import os
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import (QThread, QSize, pyqtSignal, pyqtSlot)
import design
from types import MethodType
from visa import *
import telhacks

sys.settrace

class GpibConnectThread(QThread):
    def __init__(self, cfg, parent=None):
        super().__init__()
        self.cfg = cfg
        self.parent = parent

    def showCriticalDialog(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Critical")
        msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        msg.exec_()
        self.parent.close()
        sys.exit()

    def start(self):
        self.sleep(1)
        rm = None
        instr = None

        if(os.name == 'posix'):
            rm = ResourceManager('@py')
        else:
            rm = ResourceManager()

        i = self.cfg['gpibDevice']
        r = None
        try:
            r = rm.list_resources()
        except:
            logging.critical(i + ' is not connected')
            self.showCriticalDialog(i + ' is not connected')

        if i not in r:
            logging.critical(i + ' is not connected')
            self.showCriticalDialog(i + ' is not connected')

        instr = rm.open_resource(i)

        instr.read_stb = MethodType(telhacks.read_stb_with_previous, instr)
        instr.timeout = 1000 # in miliseconds

        return rm, instr

class GpibCommandThread(QThread):

    finished = pyqtSignal()

    # we can't print to the QPlainTextEdit from within the thread so we pass the messages using signals/slots
    # to the main thread
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    critical = pyqtSignal(str)

    def __init__(self, instr, cmd, arg=None):
        super().__init__()
        #self.started.connect(self.run)
        self.instr = instr
        self.cmd = cmd
        self.arg = arg

    def run(self):
        if self.cmd == 'query':
            if self.arg == '' or self.arg == None:
                self.error.emit('Missing input string for query operation.')
            else:
                res = self.instr.query(self.arg)
                self.info.emit('Query \"{0}\" -> \"{1}\"'.format(self.arg, res.rstrip('\r\n')))

        elif self.cmd == 'write':
            if self.arg == '' or self.arg == None:
                self.error.emit('Missing input string for write operation.')
            else:
                res = self.instr.write(self.arg)
                self.info.emit('Write \"{0}\" -> {1}'.format(self.arg, constants.StatusCode(res[1]).name))

        elif self.cmd == 'read':
            res = self.instr.read()
            self.info.emit('Read -> {0}'.format(res.rstrip('\r\n')))

        elif self.cmd == 'serial_poll':
            res = self.instr.read_stb()
            self.info.emit('Serial poll -> 0x{0:X}'.format(res))

        elif self.cmd == 'clear':
            self.instr.clear()
            self.info.emit('Performed bus clear')

        self.finished.emit()

class GPIBTesterWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, cfg, parent=None):
        super(GPIBTesterWindow, self).__init__(parent)
        self.setupUi(self)
        self.queryButton.clicked.connect(lambda: self.cmdButtonClicked('query'))
        self.writeButton.clicked.connect(lambda: self.cmdButtonClicked('write'))
        self.readButton.clicked.connect(lambda: self.cmdButtonClicked('read'))
        self.serialPollButton.clicked.connect(lambda: self.cmdButtonClicked('serial_poll'))
        self.clearButton.clicked.connect(lambda: self.cmdButtonClicked('clear'))
        self.runButton.clicked.connect(self.runButtonClicked)
        self.sidePanel.setHidden(True)
        self.sidePanelButton.clicked.connect(self.sidePanelButtonClicked)
        self.thread = GpibConnectThread(cfg, self)
        self.rm, self.instr = self.thread.start()
        self.itemsToXable = (self.queryButton, self.writeButton, self.readButton, self.clearButton, self.runButton,
                             self.serialPollButton)

    @pyqtSlot(str)
    def info(self, message):
        logging.info(message)

    @pyqtSlot(str)
    def error(self, message):
        logging.error(message)

    @pyqtSlot(str)
    def warning(self, message):
        logging.warning(message)

    @pyqtSlot(str)
    def critical(self, message):
        logging.critical(message)

    def sidePanelButtonClicked(self):
        h = self.sidePanel.isHidden()
        sw = self.size()
        sp = self.sidePanel.size()
        if h:
            self.resize(QSize(sw.width() + sp.width() + self.sidePaneLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(False)
            self.sidePanelButton.setText('<\n<\n<\n')
        else:
            self.resize(QSize(sw.width() - sp.width() - self.sidePaneLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(True)
            self.sidePanelButton.setText('>\n>\n>\n')

    def runButtonClicked(self):
        # t = GpibSequenceThread(self.instr, sequence)
        pass

    def cmdButtonClicked(self, cmd):
        for item in self.itemsToXable:
            item.setDisabled(True)

        self.thread = GpibCommandThread(self.instr, cmd, self.commandEdit.text())
        self.thread.finished.connect(self.onFinished)
        self.thread.info.connect(self.info)
        self.thread.warning.connect(self.warning)
        self.thread.error.connect(self.error)
        self.thread.critical.connect(self.critical)
        self.thread.start()

    @pyqtSlot()
    def onFinished(self):
        for item in self.itemsToXable:
            item.setDisabled(False)
        #logging.info('...')
        self.thread.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instr.close()
        self.rm.close()
