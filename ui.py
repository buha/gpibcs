from PyQt5 import QtGui, QtCore, QtWidgets
import design
from visa import *
import telhacks

class GpibConnectThread(QtCore.QThread):
    def __init__(self, cfg, parent=None):
        super().__init__()
        self.cfg = cfg
        self.parent = parent
        # todo de-activate all parent widgets

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
        '''
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
        '''
        return rm, instr

class GpibCommandThread(QtCore.QThread):
    done = QtCore.pyqtSignal(object)

    def __init__(self, instr, cmd, arg=None):
        super().__init__()
        self.instr = instr
        self.cmd = cmd
        self.arg = arg

    def start(self):
        if self.cmd == 'query':
            if self.arg == '' or self.arg == None:
                logging.error('Missing input string for query operation.')
                return

            res = self.instr.query(self.arg)
            logging.info('Query \"{0}\" -> \"{1}\"'.format(self.arg, res.rstrip('\r\n')))

        elif self.cmd == 'write':
            if self.arg == '' or self.arg == None:
                logging.error('Missing input string for write operation.')
                return

            res = self.instr.write(self.arg)
            logging.info('Write \"{0}\" -> {1}'.format(self.arg, constants.StatusCode(res[1]).name))

        elif self.cmd == 'read':
            res = self.instr.read()
            logging.info('Read -> {0}'.format(res.rstrip('\r\n')))

        elif self.cmd == 'serial_poll':
            res = self.instr.read_stb()
            logging.info('Serial poll -> 0x{0:X}'.format(res))

class GPIBTesterWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, cfg, parent=None):
        super(GPIBTesterWindow, self).__init__(parent)
        self.setupUi(self)
        self.queryButton.clicked.connect(lambda: self.cmdButtonClicked('query'))
        self.writeButton.clicked.connect(lambda: self.cmdButtonClicked('write'))
        self.readButton.clicked.connect(lambda: self.cmdButtonClicked('read'))
        self.serialPollButton.clicked.connect(lambda: self.cmdButtonClicked('serial_poll'))
        self.sidePanel.setHidden(True)
        self.sidePanelButton.clicked.connect(self.sidePanelButtonClicked)
        self.thread = GpibConnectThread(cfg, self)
        self.rm, self.instr = self.thread.start()

    def sidePanelButtonClicked(self):
        h = self.sidePanel.isHidden()
        sw = self.size()
        sp = self.sidePanel.size()
        if h:
            self.resize(QtCore.QSize(sw.width() + sp.width() + self.sidePaneLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(False)
            self.sidePanelButton.setText('<\n<\n<\n')
        else:
            self.resize(QtCore.QSize(sw.width() - sp.width() - self.sidePaneLayout.spacing(), sw.height()))
            self.sidePanel.setHidden(True)
            self.sidePanelButton.setText('>\n>\n>\n')


    def cmdButtonClicked(self, cmd):
        t = GpibCommandThread(self.instr, cmd, self.commandEdit.text())
        self.queryButton.setDisabled(True)
        self.writeButton.setDisabled(True)
        self.readButton.setDisabled(True)
        t.start()
        self.queryButton.setDisabled(False)
        self.writeButton.setDisabled(False)
        self.readButton.setDisabled(False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instr.close()
        self.rm.close()
