from PyQt5 import QtGui, QtCore, QtWidgets

class QCustomTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__()
        # stretch horizontal header's last item to fill the space
        self.horizontalHeader().setStretchLastSection(True)
        # make the columns proportional
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def keyPressEvent(self, QKeyEvent):
        # delete selected items when pressing the keyboard's delete key
        if QKeyEvent.key() == QtCore.Qt.Key_Delete:
            selected = self.selectedItems()
            for i in selected:
                self.removeRow(i.row())
        QtWidgets.QTableWidget.keyPressEvent(self, QKeyEvent)

    def mousePressEvent(self, event):
        # overwrite the mouse press event so that it inserts a new row when clicking on the empty space
        # (provided there is no empty last row already)
        if self.itemAt(event.pos()) is None and (self.model().index(self.rowCount() - 1, 0).data() != None):
            self.clearSelection()
            self.insertRow(self.rowCount())
        QtWidgets.QTableWidget.mousePressEvent(self, event)