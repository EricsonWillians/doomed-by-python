from PyQt5.QtWidgets import QAction, QFileDialog, QDialog, QFileSystemModel
from PyQt5.QtCore import QSortFilterProxyModel
from os import path


class ExecutableFilterModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_index):
        if isinstance(self.sourceModel(), QFileSystemModel):
            index = self.sourceModel().index(source_row, 0, source_index)
            fi = self.sourceModel().fileInfo(index)
            return fi.isDir() or fi.isExecutable()
        return super().filterAcceptsRow(source_row, source_index)


class OpenSourcePortAction(QAction):
    def __init__(self, widget, setSourcePort, config, saveSourcePortPath):
        super().__init__("&Open Source Port", widget)
        self.widget = widget
        self.setShortcut("Ctrl+O")
        self.setStatusTip("Select a source port")
        self.triggered.connect(self._open)
        self.setSourcePort = setSourcePort
        self.config = config
        self.saveSourcePortPath = saveSourcePortPath

    def _open(self):
        proxy_model = ExecutableFilterModel()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dialog = QFileDialog(
            self.widget, "Select a source port", self.config.get(
                "sourcePortDir")
        )
        dialog.setOptions(options)
        dialog.setProxyModel(proxy_model)
        if dialog.exec_() == QDialog.Accepted:
            filename = dialog.selectedUrls()[0].toLocalFile()
            self.saveSourcePortPath(filename)
            self.setSourcePort(filename)
