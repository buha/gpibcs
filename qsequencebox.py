from PyQt5.QtWidgets import QComboBox
from PyQt5 import QtCore

class QSequenceBox(QComboBox):
    def keyPressEvent(self, QKeyEvent):
        '''
        Overloads method in QComboBox to prevent keyboard selection of last index (Load sequence...)
        '''
        emit = True
        # prevent selection via Arrow Down/Page Down key
        if QKeyEvent.key() == QtCore.Qt.Key_Down or QKeyEvent.key() == QtCore.Qt.Key_PageDown:
            ci = self.currentIndex()
            # check if currently selected item is next to last one
            if ci == self.count() - 2:
                emit = False
        # prevent selection via End key
        elif QKeyEvent.key() == QtCore.Qt.Key_End:
            emit = False
            self.setCurrentIndex(self.count() - 2)

        if emit:
            QComboBox.keyPressEvent(self, QKeyEvent)