from PyQt5.QtWidgets import QPushButton
import os
import stat
import subprocess


class LaunchButton(QPushButton):

    def __init__(self, portPathInput, iwadInput):
        super().__init__("Launch")
        self.portPathInput = portPathInput
        self.iwadInput = iwadInput
        self.clicked.connect(self.onClick)

    def onClick(self):
        """ wads = [wad.text() for wad in self.iwadInput.getItems()]
        iwadArgument = f'-iwad {" ".join(wads)}' """
        iwadArgument = f'-iwad {self.iwadInput.text()}'
        print(iwadArgument)
        subprocess.call(
            f'{self.portPathInput.text()} {iwadArgument}', shell=True)
        # os.system(f'"{self.portPathInput.text()}" {iwadArgument}')
