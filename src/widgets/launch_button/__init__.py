from PyQt5.QtWidgets import QPushButton
import os, stat
import subprocess

class LaunchButton(QPushButton):

    def __init__(self, portPathInput, wadList):
        super().__init__("Launch")
        self.portPathInput = portPathInput
        self.wadList = wadList
        self.clicked.connect(self.onClick)

    def onClick(self):
        wads = [wad.text() for wad in self.wadList.getItems()]
        iwadArgument = f'-iwad {" ".join(wads)}'
        # subprocess.call([self.portPathInput.text(), iwadArgument])
        os.system(f'"{self.portPathInput.text()}" {iwadArgument}')