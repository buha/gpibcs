from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QHeaderView, QTableWidget

class QCustomTableWidget(QTableWidget):
    '''
    A custom table widget that has a context view to add/remove rows and listens to keyboard/mouse events.
    '''
    def __init__(self, parent):
        super().__init__()

        # add custom actions in context menu
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        beforeAction = QAction("Add row before", self)
        beforeAction.triggered.connect(lambda: self.insertRow(self.currentRow()))
        self.addAction(beforeAction)

        afterAction = QAction("Add row after", self)
        afterAction.triggered.connect(lambda: self.insertRow(self.currentRow() + 1))
        self.addAction(afterAction)

        removeAction = QAction("Remove row", self)
        removeAction.triggered.connect(lambda: self.removeRow(self.currentRow()))
        self.addAction(removeAction)

        # make the columns proportional
        [self.horizontalHeader(i).setSectionResizeMode(QHeaderView.Stretch) \
            for i in range(self.columnCount())]

    def keyPressEvent(self, QKeyEvent):
        '''
        Overloads method in QTableWidget to remove a row when the user hits Delete key.
        '''
        # delete selected items when pressing the keyboard's delete key
        if QKeyEvent.key() == QtCore.Qt.Key_Delete:
            selected = self.selectedItems()
            for i in selected:
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