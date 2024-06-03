from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from commonUI import VTabWidget, recipeSearch

class adminMenu(VTabWidget):
    def __init__(self, user, parent = None):
        super().__init__(parent)
        self.user = user
        self.addTab(recipeSearch(), 'tab1')
        self.addTab(None, 'tab3')
        self.addTab(QWidget(), 'tab2')
