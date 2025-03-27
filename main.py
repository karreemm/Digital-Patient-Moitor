import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import pandas as pd

from ArrhythmiaClassifier import ArrhythmiaClass
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

        # self.detection_thread = ArrhythmiaDetectionThread(self)
        # self.detection_thread.detection_completed.connect(self.handle_arrhythmia_detection)
        #
        # self.arrhythmia_timer = QTimer(self)
        # self.arrhythmia_timer.timeout.connect(self.trigger_arrhythmia_detection)

        self.graphWidget = pg.PlotWidget(self)
        self.ecgLayout.addWidget(self.graphWidget)
        self.graph = Graph(self.graphWidget, sampling_rate=360, window_size=1500)
        self.setWindowTitle('Patient Monitor')

        # self.test_data()

        self.read_data()

        window_size = 1500  # 2 seconds at 360 Hz
        detection_interval = (window_size * 1000) // 360  # Convert to milliseconds
        # self.arrhythmia_timer.start(detection_interval)

    def read_data(self):
        df = pd.read_csv("ECGs/Atrial Fibrillation.csv")
        amplitude = df["Amplitude"].values
        time = (df["Time (ms)"] / 1000).values
        self.ecg = amplitude
        self.sampling_rate = 360
        self.graph.set_signal(time, amplitude)

    def test_data(self):
        time = np.linspace(0, 10, 400)
        amplitude = np.sin(2 * np.pi * 1 * time)
        self.graph.set_signal(time, amplitude)

    def trigger_arrhythmia_detection(self):
        graph = self.graph

        # Ensure we have enough data
        if len(graph.signal_x) < graph.window_size:
            return

        # Calculate start and end indices for the current window
        end_idx = graph.current_frame
        start_idx = max(0, end_idx - graph.window_size)

        # Set parameters and start the thread
        self.detection_thread.set_parameters(
            graph.signal_y,
            start_idx,
            end_idx,
            sampling_rate=graph.sampling_rate
        )

        # Start the thread if not already running
        if not self.detection_thread.isRunning():
            self.detection_thread.start()

    def handle_arrhythmia_detection(self, classification, irregular_beats, ecg_info):
        """
        Handle the results of arrhythmia detection
        """
        # Update UI with classification
        if classification == ArrhythmiaClass.A_FIB:
            self.ecgClassification.setText("Atrial Fibrillation")
            self.ecgStatus.setStyleSheet("color: red;")
        elif classification == ArrhythmiaClass.TACHYCARDIA:
            self.ecgClassification.setText("Tachycardia")
            self.ecgStatus.setStyleSheet("color: orange;")
        elif classification == ArrhythmiaClass.BRADYCARDIA:
            self.ecgClassification.setText("Bradycardia")
            self.ecgStatus.setStyleSheet("color: orange;")
        else:
            self.ecgClassification.setText("Normal")
            self.ecgStatus.setStyleSheet("color: green;")

        # If there are irregular beats, highlight them
        if irregular_beats:
            # Convert relative indices to x-coordinates
            x_coords = [self.graph.signal_x[beat] for beat in irregular_beats]
            y_coords = [self.graph.signal_y[beat] for beat in irregular_beats]

            # self.graph.irregular_beats_plot.setData(x_coords, y_coords)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
