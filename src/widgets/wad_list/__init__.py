from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


class WadList(QListWidget):

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        for item in self.selectedItems():
            current_row = self.row(item)
            if event.key() == Qt.Key_Delete:
                self.takeItem(current_row)
            elif event.key() == Qt.Key_Down:
                if current_row == len(self)-1:
                    self.setCurrentRow(0)
                else:
                    self.setCurrentRow(current_row+1)
            elif event.key() == Qt.Key_Up:
                if current_row == 0:
                    self.setCurrentRow(len(self)-1)
                else:
                    self.setCurrentRow(current_row-1)