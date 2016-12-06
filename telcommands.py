from PyQt5.QtCore import (QThread, pyqtSignal)
from telhacks import *
from time import sleep

class TELCommandThread(QThread):

    finished = pyqtSignal(int, str)

    # we can't print to the QPlainTextEdit from within the thread so we pass the messages using signals/slots
    # to the main thread
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    error = pyqtSignal(str)
    critical = pyqtSignal(str)

    def __init__(self, instr, action, command=None):
        super().__init__()
        self.instr = instr
        self.action = action
        self.command = command

    def emitFormatted(self, action, message, status=constants.StatusCode.success):
        if 'error' in constants.StatusCode(status).name:
            self.error.emit('({:5}) {} - {}'.format(action, message, constants.StatusCode(status).name))
        elif 'warning' in constants.StatusCode(status).name:
            self.warning.emit('({:5}) {} - {}'.format(action, message, constants.StatusCode(status).name))
        else:
            self.info.emit('({:5}) {}'.format(action, message))

    def run(self):
        status = constants.StatusCode.success
        result = None

        if self.action == 'ibwrt':
            if self.command == '':
                self.emitFormatted(self.action, 'Command is not specified')
            else:
                wr = self.instr.write(self.command)
                status = wr[1]
                self.emitFormatted(self.action, self.command, status)

        elif self.action == 'ibrd':
            result = self.instr.read()
            if result == '':
                status = constants.StatusCode.error_timeout
                self.emitFormatted('ibrd', '', status)
            else:
                self.emitFormatted('ibrd', result.rstrip('\r\n'))

        elif self.action == 'ibrsp':
            stb = self.instr.read_stb(previous=self.command)
            result = '0x{0:X}'.format(stb)
            self.emitFormatted(self.action, result)

        elif self.action == 'ibclr':
            self.instr.clear()
            self.emitFormatted(self.action, '')

        elif self.action == 'ibwait':
            self.emitFormatted('wait', 'Waiting on status byte...')
            self.instr.wait_for_srq()

        self.finished.emit(status, result)
