import sys

import PyQt5

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

from ucas import *
import AutoLogin

#if __name__ == "__main__":

app = QApplication(sys.argv)
mainWindow = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mainWindow)
mainWindow.show()
sys.exit(app.exec_())
