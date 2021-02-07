from PyQt5.QtWidgets import QPushButton
import os
import stat
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
        print(iwadArgument)
        subprocess.call(
            f'{self.portPathInput.text()} {iwadArgument}', shell=True)
        # os.system(f'"{self.portPathInput.text()}" {iwadArgument}')
