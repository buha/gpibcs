from PyQt5.QtCore import (QThread, pyqtSignal)
from telhacks import *
from time import sleep

class TELCommandThread(QThread):

    finished = pyqtSignal(int)

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

    def emitFormatted(self, action, message, status=constants.StatusCode.success):
        if 'error' in constants.StatusCode(status).name:
            self.error.emit('({:5}) {} - {}'.format(action, message, constants.StatusCode(status).name))
        elif 'warning' in constants.StatusCode(status).name:
            self.warning.emit('({:5}) {} - {}'.format(action, message, constants.StatusCode(status).name))
        else:
            self.info.emit('({:5}) {}'.format(action, message))

    def prerun(self):
        if self.command == 'U':
            self.savedTimeout = self.instr.timeout
            self.instr.timeout = 10000

    def postrun(self):
        if self.command == 'U':
            self.instr.timeout = self.savedTimeout

    def run(self):
        status = constants.StatusCode.success
        self.prerun()
        '''
        if self.actiontype == 'ibwrt | ibrd':
            if self.command == '':
                self.emitFormatted('ibwrt', 'Command is not specified')
            else:
                res = self.instr.write(self.command)
                self.emitFormatted('ibwrt', self.command, res[1])
                res = self.instr.read()
                if res == '':
                    self.emitFormatted('ibrd', '', constants.StatusCode.error_timeout)
                else:
                    self.emitFormatted('ibrd', res.rstrip('\r\n'))

        elif self.actiontype == 'ibwrt | ibrsp':
            if self.command == '':
                self.emitFormatted('(ibwrt) Command is not specified')
            else:
                res = self.instr.write(self.command)
                self.emitFormatted('ibwrt', self.command, res[1])
                self.emitFormatted('ibrsp', 'Waiting on status byte...')
                self.instr.wait_for_srq()
                stb = self.instr.read_stb(previous=True)
                self.emitFormatted('ibrsp', '0x{0:X}'.format(stb))
        '''
        if self.actiontype == 'ibwrt':
            if self.command == '':
                self.emitFormatted(self.actiontype, 'Command is not specified')
            else:
                res = self.instr.write(self.command)
                status = res[1]
                self.emitFormatted(self.actiontype, self.command, status)

        elif self.actiontype == 'ibrd':
            res = self.instr.read()
            if res == '':
                status = constants.StatusCode.error_timeout
                self.emitFormatted('ibrd', '', status)
            else:
                self.emitFormatted('ibrd', res.rstrip('\r\n'))

        elif self.actiontype == 'ibrsp':
            res = self.instr.read_stb()
            self.emitFormatted(self.actiontype, '0x{0:X}'.format(res))

        elif self.actiontype == 'ibclr':
            self.instr.clear()
            self.emitFormatted(self.actiontype, '')

        elif self.actiontype == 'ibwait':
            self.emitFormatted('wait', 'Waiting on status byte...')
            self.instr.wait_for_srq()

        self.postrun()

        self.finished.emit(status)
