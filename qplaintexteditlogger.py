import logging

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