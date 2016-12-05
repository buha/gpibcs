from PyQt5.QtCore import (QThread, pyqtSignal)
from telhacks import *
from time import sleep

class TELCommandThread(QThread):

    finished = pyqtSignal()

    # we can't print to the QPlainTextEdit from within the thread so we pass the messages using signals/slots
    # to the main thread
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    critical = pyqtSignal(str)

    def __init__(self, instr, actiontype, command=None):
        super().__init__()
        self.instr = instr
        self.actiontype = actiontype
        self.command = command

    def run(self):
        if self.actiontype == 'query':
            res = self.instr.query(self.command)
            self.info.emit('{0} -> {1}'.format(self.command, res.rstrip('\r\n')))

        elif self.actiontype == 'write':
            res = self.instr.write(self.command)
            self.info.emit('{0} -> {1}'.format(self.command, constants.StatusCode(res[1]).name))

        elif self.actiontype == 'write_poll':
            res = self.instr.write(self.command)
            self.info.emit('{0} -> {1}'.format(self.command, constants.StatusCode(res[1]).name))
            self.info.emit('Waiting on status byte...')
            self.instr.wait_for_srq()
            stb = self.instr.read_stb(previous=True)
            self.info.emit('STB: 0x{0:X}'.format(stb))

        elif self.actiontype == 'read':
            res = self.instr.read()
            self.info.emit('Read -> {0}'.format(res.rstrip('\r\n')))

        elif self.actiontype == 'serial_poll':
            res = self.instr.read_stb()
            self.info.emit('Serial poll -> 0x{0:X}'.format(res))

        elif self.actiontype == 'clear':
            self.instr.clear()
            self.info.emit('Performed bus clear')

        self.finished.emit()
