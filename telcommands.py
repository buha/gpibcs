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

    commands = ['ibwrt', 'ibrd', 'ibrsp', 'ibclr', 'waitsrq', 'pause']

    def __init__(self, instr, command, data=None, timeout=None):
        super().__init__()
        self.instr = instr
        self.command = command
        self.data = data
        self.timeout = timeout

    def emitFormatted(self, action, message, status=constants.StatusCode.success):
        if 'error' in constants.StatusCode(status).name:
            self.error.emit('{:8} {}-> {}'.format('(' + action + ')', message, constants.StatusCode(status).name))
        elif 'warning' in constants.StatusCode(status).name:
            self.warning.emit('{:8} {}-> {}'.format('(' + action + ')', message, constants.StatusCode(status).name))
        else:
            if action in ['ibrd', 'ibrsp']:
                formatting = '-> '
            else:
                formatting = ''
            self.info.emit('{:8} {}{}'.format('(' + action + ')', formatting, message))

    def run(self):
        status = constants.StatusCode.success
        result = None

        # set the timeout if it was specified before performing any action
        if self.timeout != None:
            self.instr.timeout = self.timeout

        # perform actions
        if self.command == 'ibwrt':
            if self.data == '':
                self.emitFormatted(self.command, 'Command is not specified')
            else:
                try:
                    wr = self.instr.write(self.data)
                except VisaIOError as e:
                    wr = (0, e.error_code)
                status = wr[1]
                self.emitFormatted(self.command, self.data, status)

        elif self.command == 'ibrd':
            result = ''
            try:
                result = self.instr.read()
                self.emitFormatted('ibrd', result.rstrip('\r\n'))
            except VisaIOError as e:
                status = e.error_code
                self.emitFormatted('ibrd', '', status)

        elif self.command == 'ibrsp':
            stb = self.instr.read_stb(previous=self.data)
            result = '0x{0:X}'.format(stb)
            self.emitFormatted(self.command, result)

        elif self.command == 'ibclr':
            self.instr.clear()
            self.emitFormatted(self.command, '')

        elif self.command == 'waitsrq':
            self.emitFormatted('waitsrq', 'Waiting on status byte...')
            try:
                self.instr.wait_for_srq()
            except VisaIOError as e:
                status = e.error_code
                self.emitFormatted('ibrd', '', status)

        elif self.command == 'pause':
            try:
                pause = float(self.data)
                self.emitFormatted('pause', 'Pausing execution for {}s...'.format(self.data))
                time.sleep(pause)
            except:
                status = constants.StatusCode.error_invalid_parameter
                self.emitFormatted('pause', 'Missing value for pause command', status)

        self.finished.emit(status, result)