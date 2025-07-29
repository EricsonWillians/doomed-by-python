import os
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
)


def _file_size(path: str) -> str:
    """Return file size in kilobytes formatted as a string."""
    try:
        size_kb = os.path.getsize(path) // 1024
        return f"{size_kb} KB"
    except OSError:
        return "?"


class PWadList(QTreeWidget):

    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(["Mod", "Size", "Folder"])
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setRootIsDecorated(False)
        self.setToolTip('Drag to reorder mods. Delete key removes entries.')

    def moveUp(self):
        """Move the selected items up by one position."""
        selected = self.selectedItems()
        if not selected:
            return
        for item in selected:
            idx = self.indexOfTopLevelItem(item)
            if idx > 0:
                self.takeTopLevelItem(idx)
                self.insertTopLevelItem(idx - 1, item)
                self.setCurrentItem(item)

    def moveDown(self):
        """Move the selected items down by one position."""
        selected = self.selectedItems()
        if not selected:
            return
        # process in reverse to avoid leapfrogging
        for item in reversed(selected):
            idx = self.indexOfTopLevelItem(item)
            if idx < self.topLevelItemCount() - 1:
                self.takeTopLevelItem(idx)
                self.insertTopLevelItem(idx + 1, item)
                self.setCurrentItem(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)
        else:
            super().keyPressEvent(event)

    def getItems(self):
        items = []
        for n in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(n))
        return items

    def addWad(self, path: str):
        """Add a wad entry with size information if not already present."""
        paths = [i.data(0, Qt.UserRole) for i in self.getItems()]
        if path in paths:
            return False
        item = QTreeWidgetItem([
            os.path.basename(path),
            _file_size(path),
            os.path.dirname(path),
        ])
        item.setToolTip(0, path)
        item.setData(0, Qt.UserRole, path)
        self.addTopLevelItem(item)
        return True
