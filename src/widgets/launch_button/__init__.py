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