import sys
import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem)
from PyQt5.QtCore import (Qt, QThread, QSize, pyqtSignal, pyqtSlot)
import design
from types import MethodType
from visa import *
from telcommands import *
import telhacks
import queue

class GPIBTesterWindow(QMainWindow, design.Ui_MainWindow):
    def __init__(self, cfg, parent=None):
        super(GPIBTesterWindow, self).__init__(parent)
        self.setupUi(self)
        self.queryButton.clicked.connect(lambda: self.cmdButtonClicked(self.queryButton.text()))
        self.queryResponseButton.clicked.connect(lambda: self.cmdButtonClicked(self.queryResponseButton.text()))
        self.writeButton.clicked.connect(lambda: self.cmdButtonClicked(self.writeButton.text()))
        self.readButton.clicked.connect(lambda: self.cmdButtonClicked(self.readButton.text()))
        self.serialPollButton.clicked.connect(lambda: self.cmdButtonClicked(self.serialPollButton.text()))
        self.clearButton.clicked.connect(lambda: self.cmdButtonClicked(self.clearButton.text()))
        self.runButton.clicked.connect(self.runButtonClicked)
        self.sidePanelButton.clicked.connect(self.sidePanelButtonClicked)
        self.saveAsButton.clicked.connect(self.saveAsButtonClicked)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.sequenceBox.setCurrentIndex(-1)
        self.sequenceBox.currentIndexChanged.connect(self.sequenceBoxChanged)

        # start with a hidden right panel
        self.sidePanel.setHidden(True)

        # these are GUI widgets to disable while performing a command
        self.itemsToXable = (self.queryButton, self.queryResponseButton, self.writeButton, self.readButton, self.runButton,
                             self.serialPollButton, self.saveButton, self.saveAsButton, self.sequenceBox, self.clearButton)

        # initialize the sequence queue
        self.sequence = queue.Queue()

        # connect to the device
        self.rm, self.instr = self.connect(cfg)
    def save(self, filename):
        # compute a list with all the lines in the sequence table
        lines = []
        for i in range(self.tableWidget.rowCount() - 1):
            lines.append(self.tableWidget.item(i, 0).text())

        # dump the list contents to the selected file
        with open(filename, 'w') as f:
            for line in lines:
                f.write("{}\n".format(line))

    def saveAsButtonClicked(self):
        # select a file to save to using the dialog
        fname = QFileDialog.getSaveFileName(None, 'Save As', '.seq', filter='GPIB Sequence (*.seq)')
        if fname[0] == '':
            return

        # save to the selected file
        self.save(fname[0])

        # add this file to the combobox
        self.sequenceBox.blockSignals(True)
        last = self.sequenceBox.count() - 1
        self.sequenceBox.insertItem(last, fname[0])
        self.sequenceBox.setCurrentIndex(last)
        self.sequenceBox.blockSignals(False)

    def saveButtonClicked(self):
        filename = self.sequenceBox.currentText()
        self.save(filename)

    def sequenceBoxChanged(self):
        self.sequenceBox.blockSignals(True)

        current = self.sequenceBox.currentIndex()
        last = self.sequenceBox.count() - 1

        # user wants to load a sequence from a file
        if self.sequenceBox.currentText() == 'Load sequence ...':
            fname = QFileDialog.getOpenFileName(filter='GPIB Sequence (*.seq);;All Files (*)')[0]

            # check if we don't deal with a file already in the list
            repeat = False
            for i in range(self.sequenceBox.count()):
                if self.sequenceBox.itemText(i) == fname:
                    self.sequenceBox.setCurrentIndex(i)
                    repeat = True
                    break

            if fname == '':
                self.sequenceBox.setCurrentIndex(-1)
            elif repeat == False:
                self.sequenceBox.insertItem(last, fname)
                self.sequenceBox.setCurrentIndex(last)

        # user selected another sequence file already in the list
        else:
            fname = self.sequenceBox.currentText()

        # whatever the user picked above, repopulate the table
        try:
            # read selected file to a list
            with open(fname) as f:
                lines = f.readlines()
            f.close()

            # delete all rows in sequence table
            self.tableWidget.setRowCount(0)

            # add each line to the sequence table
            for line in lines:
                i = self.tableWidget.rowCount()
                self.tableWidget.insertRow(i) # insert row at end
                item = QTableWidgetItem(line.rstrip('\r\n'))
                self.tableWidget.setItem(i, 0, item)

        except FileNotFoundError:
            pass

        self.sequenceBox.blockSignals(False)

    def sidePanelButtonClicked(self):
        h = self.sidePanel.isHidden()
        sw = self.size()
        sp = self.sidePanel.size()
        if h:
            self.resize(QSize(sw.width() + sp.width() + self.sidePanelLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(False)
            self.sidePanelButton.setText('<\n<\n<\n')
        else:
            self.resize(QSize(sw.width() - sp.width() - self.sidePanelLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(True)
            self.sidePanelButton.setText('>\n>\n>\n')

    def runButtonClicked(self):
        for row in range(self.tableWidget.rowCount()):
            # get each command from the table, line by line
            try:
                command = self.tableWidget.item(row, 0).text()
            except AttributeError:
                break

            if command[0] in ['A', 'O']:
                self.sequence.put(('ibwrt', command))
                self.sequence.put(('ibrd', None))
            elif command[0] in ['C', 'Q', 'U', 'V']:
                self.sequence.put(('ibwrt', command))
                self.sequence.put(('ibwait', None))
                self.sequence.put(('ibrsp', None))
            elif command == '':
                pass
            else:
                logging.warning('Ignoring unknown (not implemented?) command ' + command)

        for item in self.itemsToXable:
            item.setDisabled(True)

        self.sequenceBox.setFocus(Qt.MouseFocusReason)
        self.onStepFinished(constants.StatusCode.success)

    def cmdButtonClicked(self, text):
        if text == self.queryButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text()))
            self.sequence.put(('ibrd', None))
        elif text == self.queryResponseButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text()))
            self.sequence.put(('ibwait', None))
            self.sequence.put(('ibrsp', None))
        elif text == self.writeButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text()))
        elif text == self.readButton.text():
            self.sequence.put(('ibrd', None))
        elif text == self.serialPollButton.text():
            self.sequence.put(('ibrsp', None))
        elif text == self.clearButton.text():
            self.sequence.put(('ibclr', None))

        for item in self.itemsToXable:
            item.setDisabled(True)

        self.onStepFinished(constants.StatusCode.success)

    def showCriticalDialog(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Critical")
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()
        self.close()
        sys.exit()

    def connect(self, cfg):
        rm = None
        instr = None

        if(os.name == 'posix'):
            rm = ResourceManager('@py')
        else:
            rm = ResourceManager()

        i = cfg['gpibDevice']
        if i != '':
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
            instr.timeout = 300 # in miliseconds

        return rm, instr

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instr.close()
        self.rm.close()


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

    @pyqtSlot(int)
    def onStepFinished(self, status):
        # if status is not success, abort sequence
        if 'success' not in constants.StatusCode(status).name:
            self.sequence.queue.clear()

        # for our purpose. there can be two types of commands: a write followed by a read or a write followed by
        # a serial poll
        try:
            seqi = self.sequence.get_nowait()
        except queue.Empty:
            for item in self.itemsToXable:
                item.setDisabled(False)
            return

        # arm and start the thread
        self.thread = TELCommandThread(self.instr, seqi[0], seqi[1])
        self.thread.info.connect(self.info)
        self.thread.warning.connect(self.warning)
        self.thread.error.connect(self.error)
        self.thread.critical.connect(self.critical)
        self.thread.finished.connect(self.onStepFinished)
        self.thread.start()

    @pyqtSlot()
    def onFinished(self):
        pass