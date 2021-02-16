from PyQt5.QtWidgets import *
from src import const
from bs4 import BeautifulSoup
import requests


class WadFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()
        r = requests.get(
            'https://www.doomworld.com/idgames/levels/doom2/deathmatch/a-c/')
        soup = BeautifulSoup(r.text, 'html.parser')
        wadListings = soup.findAll("table", {"class": "wadlisting"})

        print(wadListings)

    def initUi(self):
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.error_dialog = QErrorMessage()

    def findWads(self, searchWord):
        pass
