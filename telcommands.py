from PyQt5.QtCore import (QThread, pyqtSignal)
from telhacks import *

class TELCommandThread(QThread):

    finished = pyqtSignal()

    # we can't print to the QPlainTextEdit from within the thread so we pass the messages using signals/slots
    # to the main thread
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    critical = pyqtSignal(str)

    def __init__(self, instr, cmd, arg=None):
        super().__init__()
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
