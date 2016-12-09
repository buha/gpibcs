from PyQt5 import QtGui, QtCore, QtWidgets

class QCustomTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__()
        # make the columns proportional
        [self.horizontalHeader(i).setSectionResizeMode(QtWidgets.QHeaderView.Stretch) \
            for i in range(self.columnCount())]

    def keyPressEvent(self, QKeyEvent):
        # delete selected items when pressing the keyboard's delete key
        if QKeyEvent.key() == QtCore.Qt.Key_Delete:
            selected = self.selectedItems()
            for i in selected:
                i.setText('')
        QtWidgets.QTableWidget.keyPressEvent(self, QKeyEvent)

    def isLastRowEmpty(self):
        for i in range(self.columnCount()):
            if self.model().index(self.rowCount() - 1, i).data() != None:
                return False
        return True

    def mousePressEvent(self, event):
        # overwrite the mouse press event so that it inserts a new row when clicking on the empty space
        # (provided there is no empty last row already)
        if self.itemAt(event.pos()) is None and not self.isLastRowEmpty():
            self.clearSelection()
            self.insertRow(self.rowCount())
        QtWidgets.QTableWidget.mousePressEvent(self, event)