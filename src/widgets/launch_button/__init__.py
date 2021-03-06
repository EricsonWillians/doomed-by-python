from PyQt5.QtWidgets import QPushButton
import os
import stat
import subprocess


class LaunchButton(QPushButton):

    def __init__(self, portPathInput, iwadInput, pwadList):
        super().__init__("Launch")
        self.portPathInput = portPathInput
        self.iwadInput = iwadInput
        self.pwadList = pwadList
        self.clicked.connect(self.onClick)

    def onClick(self):
        wads = [f'"{wad.text()}"' for wad in self.pwadList.getItems()]
        iwadArgument = f'-iwad {self.iwadInput.text()}'
        pwadArgument = f'-file {" ".join(wads)}'
        print(pwadArgument)
        subprocess.call(
            f'{self.portPathInput.text()} {iwadArgument} {pwadArgument}', shell=True)
        # os.system(f'"{self.portPathInput.text()}" {iwadArgument}')
