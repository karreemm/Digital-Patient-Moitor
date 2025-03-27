import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import pandas as pd

from helper_functions.compile_qrc import compile_qrc
compile_qrc()
from icons_setup.icons import *
from Graph import Graph

from icons_setup.compiledIcons import *
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))

        # data = pd.read_csv("file.csv")

        self.ecgLayout = self.findChild(QVBoxLayout, "ecgLayout")
        self.ecgClassification = self.findChild(QLabel, "ecgClassification")
        self.heartBeatsValue = self.findChild(QLabel, "ecgValue")
        self.ecgStatus = self.findChild(QLabel, "ecgStatus")

        self.graphWidget = pg.PlotWidget(self)
        self.ecgLayout.addWidget(self.graphWidget)
        self.graph = Graph(self.graphWidget)
        self.setWindowTitle('Patient Monitor')

        self.test_data()
    def test_data(self):
        time = np.linspace(0, 10, 400)
        amplitude = np.sin(2 * np.pi * 1 * time)
        self.graph.set_signal(time, amplitude)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())   