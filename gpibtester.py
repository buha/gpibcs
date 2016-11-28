import configparser
import logging
import os
import sys
from types import MethodType
from logging.handlers import RotatingFileHandler
from PyQt5 import QtGui, QtCore, QtWidgets
import design
from visa import *
import telhacks

def confparse(filename, cfg):
    '''
    Function that handles configuration file parsing.
    :param filename: the .conf file path
    :param cfg: a dictionary to populate with parsed configuration (typically empty)
    :return: nothing
    '''

    def confparseExHandle(filename, e):
        if type(e) is ValueError:
            sys.exit(filename + ': ' + str(e))

        elif type(e) is configparser.NoOptionError or type(e) is configparser.NoSectionError:
            # We have hardcoded default values for the configuration logging
            # so it's safe to ignore this exception
            pass
        else:
            gpibtester = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = gpibtester.format(type(e).__name__, e.args)
            sys.exit(message)

    # Initialize a config
    config = configparser.RawConfigParser(delimiters=('='),
                                          comment_prefixes=('#'),
                                          inline_comment_prefixes=('#'),
                                          empty_lines_in_values=False)

    # try to open the configuration file
    try:
        config.read(filename)
    except IOError:
        sys.exit('Configuration file ' + filename + ' could not be found.')
    except configparser.ParsingError as e:
        sys.exit('{0}, line {1}: file has no sections defined.'.format(e.args[0], e.args[1]))
    except configparser.DuplicateOptionError as e:
        sys.exit('{0}, line {1}: \"{2}\" is defined more than once.'.format(e.args[2], e.args[3], e.args[1]))
    except configparser.DuplicateSectionError as e:
        sys.exit('{0}, line {1}: \"[{2}]\" is defined more than once.'.format(e.args[1], e.args[2], e.args[0]))
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileName'] = config.get('logging', 'logFileName')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileSize'] = config.getint('logging', 'logFileSize')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileLevel'] = 10 * config.getint('logging', 'logFileLevel')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logConsoleLevel'] = 10 * config.getint('logging', 'logConsoleLevel')
        if (cfg['logConsoleLevel'] > logging.CRITICAL or
                    cfg['logConsoleLevel'] == logging.NOTSET or
                    cfg['logFileLevel'] > logging.CRITICAL or
                    cfg['logFileLevel'] == logging.NOTSET):
            raise ValueError('logConsoleLevel must be an integer in the range [1...5]')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['gpibDevice'] = config.get('gpib', 'gpibDevice')
    except Exception as e:
        confparseExHandle(filename, e)

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, instance):
        super().__init__()
        self.widget = instance
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass

def loggingsetup(cfg, logginghandler):
    '''
    Function that initializes the logging service.
    :param cfg: a pre-populated dictionary
    :return: nothing
    '''
    # create a rotating logger to a file
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(cfg['logFileLevel'])
    fileHandler = RotatingFileHandler(cfg['logFileName'], maxBytes=cfg['logFileSize'], backupCount=5)
    fileHandler.setLevel(cfg['logFileLevel'])
    fileFormatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%d/%m %H:%M:%S')
    fileHandler.setFormatter(fileFormatter)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    consoleLogger = QPlainTextEditLogger(logginghandler)
    # set the console logger level
    consoleLogger.setLevel(cfg['logConsoleLevel'])
    # set a simpler format
    consoleFormatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s', datefmt='%H:%M:%S')
    # tell the handler to use this format
    consoleLogger.setFormatter(consoleFormatter)

    # add the handlers to the root logger
    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleLogger)

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
        #self.connect(self.button, SIGNAL("clicked()"), self.clicked)
        msg.exec_()
        self.parent.close()
        sys.exit()

    def start(self):
        self.sleep(1)
        rm = None
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
        self.thread = GpibConnectThread(cfg, self)
        self.rm, self.instr = self.thread.start()

        #self.cSpinBox.lineEdit().setAlignment(QtCore.Qt.AlignHCenter)

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

def main():
    # default configuration
    cfg = {}
    cfg['logFileName'] = os.path.basename(__file__).split('.')[0] + '.log'
    cfg['logFileSize'] = 1024000
    cfg['logFileLevel'] = logging.DEBUG
    cfg['logConsoleLevel'] = logging.INFO
    cfg['logConsoleLevel'] = 'GPIB0::0::INSTR'

    # find out which .conf file we are using
    filename = os.path.basename(__file__).split('.')[0] + '.conf'

    # overwrite configuration with the contents of .conf file
    confparse(filename, cfg)

    # set up graphics
    app = QtWidgets.QApplication(sys.argv)
    form = GPIBTesterWindow(cfg)

    # set up logging
    loggingsetup(cfg, form.canvas)

    # print active configuration
    logging.debug("Started " + os.path.basename(__file__) + " with the following configuration:" + str(cfg))

    # draw
    form.show()
    s = app.exec_()

    # finish properly
    sys.exit(s)

if __name__ == '__main__':
    main()
