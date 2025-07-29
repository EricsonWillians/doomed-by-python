from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView


class PWadList(QListWidget):

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                self.takeItem(self.row(item))
        else:
            super().keyPressEvent(event)

    def getItems(self):
        items = []
        for n in range(len(self)):
            items.append(self.item(n))
        return items
