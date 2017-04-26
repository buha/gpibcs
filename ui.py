import sys
from os import listdir, path, getcwd
import logging
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QHeaderView, QDialog
from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
import mainwindow
from types import MethodType
from telcommands import *
import telhacks
import queue
from gpibcs import loggingsetup
import bugreport
import webbrowser
import zipfile as zf
import time
import glob

class GPIBTesterWindow(QMainWindow, mainwindow.Ui_MainWindow):
    '''
    The main window.
    '''
    def __init__(self, cfg, parser, parent=None):
        super(GPIBTesterWindow, self).__init__(parent)
        self.setupUi(self)
        self._cfg = cfg
        self._parser = parser

        # set up logging
        loggingsetup(cfg, self.canvas)

        # print active configuration
        logging.debug("Started " + os.path.basename(__file__) + " with the following configuration:" + str(cfg))

        # button actions
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
        self.bugButton.clicked.connect(self.bugButtonClicked)

        # auto-load some sequences
        for dir in cfg['autoLoadDirs']:
            try:
                sequences = [path.join(dir, f) for f in listdir(dir) if path.isfile(path.join(dir, f)) and f[-4:] == '.csv']
                for s in sequences:
                    self.sequenceBox.addAndSelect(s)
            except FileNotFoundError:
                if dir is not '':
                    logging.info("Could not auto-load sequence files from \"{}\"".format(dir))

        self.sequenceBox.setModified(False)
        self.sequenceBox.setCurrentIndex(-1)
        self.sequenceBox.currentIndexChanged.connect(self.sequenceBoxChanged)

        # table header policies
        h = self.tableWidget.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # start with a hidden right panel
        self.sidePanel.setHidden(True)

        # these are GUI widgets to disable while performing a command
        self.itemsToXable = (self.queryButton, self.queryResponseButton, self.writeButton, self.readButton,
                             self.serialPollButton, self.saveButton, self.saveAsButton, self.sequenceBox,
                             self.clearButton, self.repeatBox)

        # initialize the sequence queue
        self.sequence = queue.Queue()
        self.sequenceCopy = queue.Queue()
        self.runRequestActive = False
        self.stopRequestActive = False

        # connect to the device
        self.rm, self.instr = self.connect(cfg)

    def saveAsButtonClicked(self):
        '''
        Open a file selector dialog for the user to pick a file, then use this file to save the tablewidget content
        into it.
        :return:
        '''
        # select a file to save to using the dialog
        dir = self._cfg['lastUsedDir']
        fname = QFileDialog.getSaveFileName(None, 'Save As', dir, filter='Comma separated values file (*.csv)')
        if fname[0] == '':
            return
        else:
            self._cfg['lastUsedDir'] = path.dirname(fname)

        # save to the selected file
        self.tableWidget.save(fname[0])

        # add this file to the combobox
        self.sequenceBox.addAndSelect(fname[0])

    def saveButtonClicked(self):
        '''
        Handler for the save button click.
        Pick the currently selected file and save the table contents into it.
        If no file is selected, bring the Save As dialog instead.
        '''
        self.saveButton.setFocus(Qt.MouseFocusReason) # this is needed de-focus any cell currently being edited
        filename = self.tableWidget.file()
        if filename != '' and filename != 'Load sequence ...':
            self.tableWidget.save(filename)
        else:
            self.saveAsButtonClicked()

    def sequenceBoxChanged(self):
        '''
        Handler for the sequence file selection dialog.
        '''
        load = not self.sequenceBox.isSelectionAFile()

        if not self.tableWidget.isSaved():
            confirmation_message = "There are unsaved changes in your sequence. Would you like to save them first?"
            reply = QMessageBox.question(self, 'Save changes?',
                                         confirmation_message, QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.saveButtonClicked()
            else:
                pass

        # user wants to load a sequence from a file
        if load:
            dir = self._cfg['lastUsedDir']
            fname = QFileDialog.getOpenFileName(self, 'Load sequence', dir, filter='Comma separated values file (*.csv);;All Files (*)')[0]
            if fname == '':
                self.sequenceBox.addAndSelect(self.tableWidget.file())
                return
            else:
                self._cfg['lastUsedDir'] = path.dirname(fname)
        # user selected another sequence file already in the list
        else:
            fname = self.sequenceBox.currentFile()

        # whatever the user picked above, select it in the combo box and repopulate the table
        self.sequenceBox.addAndSelect(fname)
        self.tableWidget.load(fname)

    def sidePanelButtonClicked(self):
        '''
        Handler for the button that exposes the advanced right panel with the sequence table.
        '''
        h = self.sidePanel.isHidden()

        sw = self.size()
        sp = self.sidePanel.size()
        offset = 32
        if h:
            self.resize(QSize(sw.width() * 2 - offset, sw.height()))
            self.sidePanel.setHidden(False)
            self.sidePanelButton.setText('<\n<\n<\n')
        else:
            self.resize(QSize((sw.width() + offset) / 2, sw.height()))
            self.sidePanel.setHidden(True)
            self.sidePanelButton.setText('>\n>\n>\n')

        logging.debug('Side panel: {} x {} -> {} x {}'.format(self.size().width(), self.size().height(),
                                                              self.size().width(), self.size().height()))

    def runButtonClicked(self):
        '''
        Handler for the Run button click. A thread queue is created here which contains information to execute the
        commands in the sequence table. The first thread is also launched here.
        :return:
        '''
        if self.runButton.text() == 'Stop':
            self.thread.wait()
            while self.sequence.qsize() != 0:
                dummy = self.sequence.get_nowait()
            self.repeatBox.setValue(1)
            self.xableItems(False)
            self.stopRequestActive = True
            return
        else:
            for row in range(self.tableWidget.rowCount()):
                command = None
                data = None
                timeout = None

                # try to get the command field
                try:
                    command = self.tableWidget.item(row, 0).text().lower()
                    if command not in TELCommandThread.commands:
                        if command == '':
                            continue # skip the line
                        else:
                            raise ValueError
                except ValueError:
                    logging.error('Invalid command {} at line {}'.format(command, str(row + 1)))
                    while self.sequence.qsize() != 0: self.sequence.get_nowait()
                    self.repeatBox.setValue(1)
                    return
                except AttributeError:
                    continue # skip the line

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

            while self.sequenceCopy.qsize() != 0: self.sequenceCopy.get_nowait()
            for i in self.sequence.queue: self.sequenceCopy.put(i) # make a copy in case we need to repeat
            self.xableItems(True)
            self.onStepFinished(constants.StatusCode.success, None)
            self.runRequestActive = True
            logging.info('{:-^50}'.format(' Sequence start '))

    def xableItems(self, disable):
        '''
        Enable/Disable GUI items that should be enabled/disabled when a sequence is executing/finished.
        '''
        for item in self.itemsToXable:
            item.setDisabled(disable)
        
        if disable == True:
            self.runButton.setIcon(QIcon('icons/gtk-media-stop.svg'))
            self.runButton.setText('Stop')
        else:
            self.runButton.setIcon(QIcon('icons/gtk-media-play-ltr.svg'))
            self.runButton.setText('Run')
            self.runButton.setChecked(False)

        self.sequenceBox.setFocus(Qt.MouseFocusReason)

    def cmdButtonClicked(self, text):
        logging.debug('clicked ' + self.queryButton.text())

        if text == self.queryButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
            self.sequence.put(('ibrd', None, None))
        elif text == self.queryResponseButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
            self.sequence.put(('waitsrq', None, None))
        elif text == self.writeButton.text():
            self.sequence.put(('ibwrt', self.commandEdit.text(), None))
        elif text == self.readButton.text():
            self.sequence.put(('ibrd', None, None))
        elif text == self.serialPollButton.text():
            self.sequence.put(('ibrsp', False, None))
        elif text == self.clearButton.text():
            confirmation_message = "This will restart the GPIB task on the prober. Are you sure?"
            reply = QMessageBox.question(self, 'ibclr',
                                         confirmation_message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.sequence.put(('ibclr', None, None))
            else:
                pass


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

    def bugButtonClicked(self):
        self.dialog = BugReportDialog(self._cfg)
        self.dialog.show()

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
                s = i + ' is not connected.'
                logging.critical(s)
                self.showCriticalDialog(s)

            if i not in r:
                s = i + ' is not connected.'
                for i in r:
                    if 'GPIB' in i:
                        s += '\nDetected device ' + i 
                logging.critical(s)
                self.showCriticalDialog(s)
                

            instr = rm.open_resource(i)

            instr.read_stb = MethodType(telhacks.read_stb_with_previous, instr)
            instr.timeout = float(cfg['gpibTimeout']) * 1000 # in milliseconds

        logging.debug('connected to ' + i)
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
        try:
            while not self.thread.isFinished():
                # wait for the thread to terminate
                # it is certain that it will terminate but maybe there is a better way to do this
                pass
        except AttributeError:
            # if the thread is finished, the object may have been garbage collected
            pass

        # if status is not success, clear sequence in order to abort
        if 'success' not in constants.StatusCode(status).name:
            self.sequence.queue.clear()
            self.sequenceCopy.queue.clear()
            self.xableItems(False)
            self.repeatBox.setValue(1)
            if self.runRequestActive:
                self.runRequestActive = False
                logging.error('{:-^50}'.format(' Sequence aborted '))
            return

        # get the next action from sequence
        try:
            seqi = self.sequence.get_nowait()
        except queue.Empty:
            if self.repeatBox.value() > 1:
                for i in self.sequenceCopy.queue: self.sequence.put(i)
                seqi = self.sequence.get_nowait()
                self.repeatBox.setValue(self.repeatBox.value() - 1)
            else:
                self.sequenceCopy.queue.clear()
                if self.runRequestActive:
                    self.runRequestActive = False
                    if self.stopRequestActive:
                        self.stopRequestActive = False
                        logging.info('{:-^50}'.format(' Sequence stopped by user '))
                    else:
                        logging.info('{:-^50}'.format(' Sequence end '))
                self.xableItems(False)
                return

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

    def showEvent(self, QShowEvent):
        # print software version
        logging.debug('gpibcs version: ' + self.versionLabel.text())
        QMainWindow.showEvent(self, QShowEvent)

    # This implementation properly saves the config to the .conf but also deletes the comments
    def closeEvent(self, event):
        self._parser.set('gui', 'lastUsedDir', self._cfg['lastUsedDir'])
        try:
            with open('gpibcs.conf', 'w') as configfile:
                self._parser.write(configfile)
        except Exception as e:
            quit_msg = "Some settings could not be saved, most likely due to insufficient permissions for gpibcs.conf."
            reply = QMessageBox.question(self, '', quit_msg, QMessageBox.Ok)

            event.accept()

class BugReportDialog(QDialog, bugreport.Ui_bugReportDialog):
    def __init__(self, cfg):
        super(BugReportDialog, self).__init__()
        self.setupUi(self)

        self.bugFileLink.clicked.connect(self.bugFileLinkClicked)
        self.bugReportLink.clicked.connect(self.bugReportLinkClicked)

        self.installationPath = os.path.dirname(os.path.realpath(cfg['logFileName']))
        self.bugReportPath = self.installationPath + '/bugreport-' + time.strftime("%Y%m%d-%H%M%S") + '.zip'

        z = zf.ZipFile(self.bugReportPath, 'w')

        # add the .conf file to the zip
        z.write('gpibcs.conf')

        # add the .log files to the zip
        for f in glob.glob(os.path.basename(cfg['logFileName']) + "*"):
            z.write(f)

        # add the sequence files to the zip
        for f in os.listdir('sequence'):
            z.write('sequence/' + os.path.basename(f))

        self.bugFileLabel.setText(self.bugReportPath)

    def bugFileLinkClicked(self):
        webbrowser.open(self.installationPath)

    def bugReportLinkClicked(self):
        webbrowser.open('https://github.com/buha/gpibcs/issues/new')