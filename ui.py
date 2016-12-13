import sys
import os
import logging
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
import design
from types import MethodType
from telcommands import *
import telhacks
import queue
import csv

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
        self.itemsToXable = (self.queryButton, self.queryResponseButton, self.writeButton, self.readButton,
                             self.serialPollButton, self.saveButton, self.saveAsButton, self.sequenceBox, self.clearButton)

        # initialize the sequence queue
        self.sequence = queue.Queue()

        # connect to the device
        self.rm, self.instr = self.connect(cfg)
    def save(self, filename):
        with open(filename, "w", newline='') as fileOutput:
            writer = csv.writer(fileOutput)
            for rowNumber in range(self.tableWidget.model().rowCount()):
                fields = [
                    self.tableWidget.model().data(
                        self.tableWidget.model().index(rowNumber, columnNumber),
                        Qt.DisplayRole
                    )
                    for columnNumber in range(self.tableWidget.model().columnCount())
                    ]
                writer.writerow(fields)

    def saveAsButtonClicked(self):
        # select a file to save to using the dialog
        fname = QFileDialog.getSaveFileName(None, 'Save As', '.csv', filter='Comma separated values file (*.csv)')
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
            fname = QFileDialog.getOpenFileName(filter='Comma separated values file (*.csv);;All Files (*)')[0]

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
            with open(fname, "r") as fileInput:
                self.tableWidget.setRowCount(0)
                for row in csv.reader(fileInput):
                    i = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(i)
                    for col, field in enumerate(row):
                        item = QTableWidgetItem(field)
                        self.tableWidget.setItem(i, col, item)

        except FileNotFoundError:
            pass

        self.sequenceBox.blockSignals(False)

    def sidePanelButtonClicked(self):
        h = self.sidePanel.isHidden()
        sw = self.size()
        sp = self.sidePanel.size()
        if h:
            self.resize(QSize(sw.width() + sp.width() +  self.sidePanelLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(False)
            self.sidePanelButton.setText('<\n<\n<\n')
        else:
            self.resize(QSize(sw.width() - sp.width() - self.sidePanelLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(True)
            self.sidePanelButton.setText('>\n>\n>\n')

    def runButtonClicked(self):
        if self.runButton.text() == 'Stop':
            self.thread.wait()
            while self.sequence.qsize() != 0:
                dummy = self.sequence.get_nowait()
            self.xableItems(False)
        else:
            for row in range(self.tableWidget.rowCount()):
                command = None
                data = None
                timeout = None

                # try to get the command field
                try:
                    command = self.tableWidget.item(row, 0).text()
                    if command not in TELCommandThread.commands:
                        if command == '':
                            break # skip the line
                        else:
                            raise ValueError
                except ValueError:
                    logging.error('Invalid command {} at line {}'.format(command, str(row + 1)))
                    return
                except AttributeError:
                    break # skip the line

                # try to get the data field
                try:
                    data = self.tableWidget.item(row, 1).text()
                except AttributeError:
                    pass # the data must not necessarily contain something

                # try to get the timeout field
                try:
                    timeout = self.tableWidget.item(row, 2).text()
                    timeout = float(timeout) * 1000 # in milliseconds
                except ValueError:
                    if timeout != '':
                        logging.warning('Ignoring invalid timeout value at line ' + str(row + 1))
                    timeout = None
                except AttributeError:
                    timeout = None

                self.sequence.put((command, data, timeout))

            self.xableItems(True)
            self.sequenceBox.setFocus(Qt.MouseFocusReason)
            self.onStepFinished(constants.StatusCode.success, None)

    def xableItems(self, disable):
        for item in self.itemsToXable:
            item.setDisabled(disable)
        if disable == True:
            self.runButton.setIcon(QIcon('icons/gtk-media-stop.svg'))
            self.runButton.setText('Stop')
        else:
            self.runButton.setIcon(QIcon('icons/gtk-media-play-ltr.svg'))
            self.runButton.setText('Run')
            self.runButton.setChecked(False)

    def cmdButtonClicked(self, text):
        if text == self.queryButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
            self.sequence.put(('ibrd', None, None))
        elif text == self.queryResponseButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
            self.sequence.put(('waitSRQ', None, None))
            self.sequence.put(('ibrsp', True, None))
        elif text == self.writeButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
        elif text == self.readButton.text():
            self.sequence.put(('ibrd', None, None))
        elif text == self.serialPollButton.text():
            self.sequence.put(('ibrsp', False, None))
        elif text == self.clearButton.text():
            self.sequence.put(('ibclr', None, None))

        self.xableItems(True)

        self.onStepFinished(constants.StatusCode.success, None)

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
            instr.timeout = 1000 # in miliseconds

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

    def preExecution(self, action, command):
        if action == 'ibwrt':
            if command == 'U':
                self.savedTimeout = self.instr.timeout
                logging.info('Current timeout is {}, changing to {}'.format(self.savedTimeout, 10000))
                self.instr.timeout = 10000

    def postExecution(self, action, command, status, result):
        if action == 'ibwrt':
            if command == 'U':
                self.instr.timeout = self.savedTimeout
                logging.info('Restored timeout to {}'.format(self.instr.timeout))
            elif command == 'Q':
                if result == '0x47':
                    logging.info('Prober state is READY')
                if result == '0x4B':
                    logging.info('Prober state is LASTDIE')
                elif result == '0x62':
                    logging.info('Prober state is STOP')
                else:
                    # I don't know
                    pass

    @pyqtSlot(int, str)
    def onStepFinished(self, status, result):
        # if status is not success, abort sequence
        if 'success' not in constants.StatusCode(status).name:
            self.sequence.queue.clear()

        # get the next action from sequence
        try:
            seqi = self.sequence.get_nowait()
        except queue.Empty:
            self.xableItems(False)
            return

        '''
        try:
            # execute anything that shoud follow after a certain command
            self.postExecution(self.thread.action, self.thread.command, status, result)
        except:
            # it is possible that we haven't yet executed a thread, so self.thread does not exist
            pass
        '''

        # execute anything that should precede a certain command
        #self.preExecution(seqi[0], seqi[1])

        # arm and start the thread
        self.thread = TELCommandThread(self.instr, seqi[0], seqi[1], seqi[2])
        self.thread.info.connect(self.info)
        self.thread.warning.connect(self.warning)
        self.thread.error.connect(self.error)
        self.thread.critical.connect(self.critical)
        self.thread.finished.connect(self.onStepFinished)
        self.thread.start()

    @pyqtSlot()
    def onFinished(self):
        pass