from PyQt5.QtWidgets import QPushButton
from PyQt5.Qt import Qt
from PyQt5.QtCore import QProcess
import shlex


class LaunchButton(QPushButton):

    def __init__(
        self,
        portPathInput,
        iwadInput,
        pwadList,
        optionsInput,
        logWindow,
    ):
        super().__init__("Launch")
        self.portPathInput = portPathInput
        self.iwadInput = iwadInput
        self.pwadList = pwadList
        self.optionsInput = optionsInput
        self.logWindow = logWindow
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._readOutput)
        self.process.readyReadStandardError.connect(self._readOutput)
        self.process.finished.connect(self._finished)
        self.clicked.connect(self.onClick)

    def onClick(self):
        """Launch the source port and display its output."""
        self.logWindow.textEdit.clear()
        self.logWindow.show()

        wads = [item.data(0, Qt.UserRole) for item in self.pwadList.getItems()]
        args = []
        if self.iwadInput.text():
            args += ['-iwad', self.iwadInput.text()]
        if wads:
            args += ['-file', *wads]
        if self.optionsInput.text():
            args += shlex.split(self.optionsInput.text())

        self.process.setProgram(self.portPathInput.text())
        self.process.setArguments(args)
        self.process.start()

    def _readOutput(self):
        data = bytes(
            self.process.readAllStandardOutput()).decode('utf-8', 'ignore')
        if data:
            for line in data.splitlines():
                self.logWindow.append(line)
        err = bytes(
            self.process.readAllStandardError()).decode('utf-8', 'ignore')
        if err:
            for line in err.splitlines():
                self.logWindow.append(line)

    def _finished(self):
        code = self.process.exitCode()
        self.logWindow.append(f'Process finished with code {code}')
