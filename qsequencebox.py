from PyQt5.QtWidgets import QComboBox
from PyQt5 import QtCore
from os.path import basename, splitext, isfile

class QSequenceBox(QComboBox):
    def __init__(self, parent):
        super().__init__()
        self.setDuplicatesEnabled(False)
        self.files = []
        self._modifiedByUser = False

    def addAndSelect(self, path):
        '''
        Adds a file to the combo box and select it as the current item.
        If the file is already in the list it only selects it.
        In the case of invalid input, it deselects everything.
        :param path: file path
        '''
        self.blockSignals(True)

        if not isfile(path):
            self.setCurrentIndex(-1)
            self.blockSignals(False)
            return

        last = self.count() - 1

        # figure out if we deal with a file already in the list
        fileAlreadyInList = False
        for i in range(last):
            if self.files[i] == path:
                fileAlreadyInList = True
                break

        if fileAlreadyInList == False:
            self.insertItem(last, splitext(basename(path))[0])
            self.files.append(path)
            self.setCurrentIndex(last)
            self._modifiedByUser = True
        else:
            self.setCurrentIndex(i)

        self.setToolTip(path)

        self.blockSignals(False)

    def setModified(self, modified):
        self._modifiedByUser = modified

    def modified(self):
        return self._modifiedByUser

    def currentFile(self):
        try:
            cf = self.files[self.currentIndex()]
        except IndexError:
            cf = ''
        return cf

    def isSelectionAFile(self):
        return self.currentIndex() < self.count() - 1 and \
               self.currentIndex() >= 0

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