import logging

class QPlainTextEditLogger(logging.Handler):
    '''
    Custom PlainTextEdit that works as output for the python's logging system.
    '''
    def __init__(self, instance):
        super().__init__()
        self.widget = instance
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass