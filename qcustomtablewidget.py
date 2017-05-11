from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QHeaderView, QTableWidget, QTableWidgetItem
import csv

class QCustomTableWidget(QTableWidget):
    '''
    A custom table widget that has a context view to add/remove rows and listens to keyboard/mouse events.
    '''
    def __init__(self, parent):
        super().__init__()

        # keep track of edits
        self.itemChanged.connect(self.itemChangedCallback)
        self.saved = True
        self.currentFile = ''

        # add custom actions in context menu
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        beforeAction = QAction("Add row before", self)
        beforeAction.triggered.connect(lambda: [self.insertRow(self.currentRow()), self.itemChangedCallback()])
        self.addAction(beforeAction)

        afterAction = QAction("Add row after", self)
        afterAction.triggered.connect(lambda: [self.insertRow(self.currentRow() + 1), self.itemChangedCallback()])
        self.addAction(afterAction)

        removeAction = QAction("Remove row", self)
        removeAction.triggered.connect(lambda: [self.removeRow(self.currentRow()), self.itemChangedCallback()])
        self.addAction(removeAction)

        # make the columns proportional
        [self.horizontalHeader(i).setSectionResizeMode(QHeaderView.Stretch) \
            for i in range(self.columnCount())]

    def isSaved(self):
        return self.saved

    def save(self, filename):
        '''
        Save the tablewidget content into a .csv
        :param filename: path to target file
        :return:
        '''
        with open(filename, "w", newline='') as fileOutput:
            writer = csv.writer(fileOutput)
            for rowNumber in range(self.model().rowCount()):
                fields = [
                    self.model().data(
                        self.model().index(rowNumber, columnNumber),
                        Qt.DisplayRole
                    )
                    for columnNumber in range(self.model().columnCount())
                    ]
                writer.writerow(fields)
        self.saved = True

    def load(self, filename):
        try:
            with open(filename, "r") as fileInput:
                self.setRowCount(0)
                for row in csv.reader(fileInput):
                    i = self.rowCount()
                    self.insertRow(i)
                    for col, field in enumerate(row):
                        item = QTableWidgetItem(field)
                        self.setItem(i, col, item)
            self.saved = True
            self.currentFile = filename

        except FileNotFoundError:
            pass

    def file(self):
        return self.currentFile

    def itemChangedCallback(self):
        self.saved = False

    def keyPressEvent(self, QKeyEvent):
        '''
        Overloads method in QTableWidget to remove a row when the user hits Delete key.
        '''
        # delete selected items when pressing the keyboard's delete key
        if QKeyEvent.key() == QtCore.Qt.Key_Delete:
            selected = self.selectedItems()
            for i in selected:
                if i.text() != '':
                    self.itemChangedCallback()
                i.setText('')
        QTableWidget.keyPressEvent(self, QKeyEvent)

    def isLastRowEmpty(self):
        '''
        :return: True if all columns in last row don't contain any data, False otherwise
        '''
        for i in range(self.columnCount()):
            if self.model().index(self.rowCount() - 1, i).data() != None:
                return False
        return True

    def mousePressEvent(self, event):
        '''
        Overloads method in QTableWidget to add a row when the user clicks onto the widget if the last row is non-empty.
        '''
        if self.itemAt(event.pos()) is None and not self.isLastRowEmpty():
            self.clearSelection()
            self.insertRow(self.rowCount())
        QTableWidget.mousePressEvent(self, event)