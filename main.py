import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import pandas as pd

from ArrhythmiaClassifier import ArrhythmiaClass, ArrhythmiaClassifier
# from ArrhythmiaClassifier import DetectionThread
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

        self.graphWidget = pg.PlotWidget(self)
        self.ecgLayout.addWidget(self.graphWidget)
        self.graph = Graph(self.graphWidget, sampling_rate=360, window_size=1700)
        self.setWindowTitle('Patient Monitor')

        self.read_data()

        self.ecgLayout = self.findChild(QVBoxLayout, "ecgLayout")
        self.ecgClassification = self.findChild(QLabel, "ecgClassification")
        self.heartBeatsValue = self.findChild(QLabel, "ecgValue")
        self.ecgStatus = self.findChild(QLabel, "ecgStatus")

        self.arrhythmia_timer = QTimer(self)
        self.arrhythmia_timer.timeout.connect(self.trigger_arrhythmia_detection)

        window_size = 1700
        detection_interval = (window_size * 1000) // 360  # Convert to milliseconds
        self.arrhythmia_timer.start(detection_interval)

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

        # Calculate start and end indices for the current window
        end_idx = graph.current_frame
        start_idx = max(0, end_idx - graph.window_size)

        # if self.detection_thread and self.detection_thread.isRunning():
        #     self.detection_thread.quit()  # Request thread to stop
        #     self.detection_thread.wait()  # Wait for thread to actually stop
        #
        #     # Create a new thread
        # self.detection_thread = DetectionThread(self, self.ecg, start_idx, end_idx, 360)
        #
        # # Connect the signal
        # self.detection_thread.detection_completed.connect(self.on_detection_completed)
        #
        # # Start the new thread
        # self.detection_thread.start()

        classification, irregular_beats, heart_rate = ArrhythmiaClassifier.detect_irregular_beats(
            self.ecg[start_idx:end_idx], 360
        )
        self.on_detection_completed(classification, irregular_beats, heart_rate)

    def on_detection_completed(self, classification, irregular_beats, heart_rate):
        """
        Handle the results of arrhythmia detection
        """
        # Update UI with classification
        print(f"Classification: {classification}, heart rate: {heart_rate}")
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

        self.heartBeatsValue.setText(str(round(heart_rate)))

        # If there are irregular beats, highlight them
        if irregular_beats:
            # Convert relative indices to x-coordinates
            x_coords = [self.graph.signal_x[beat] for beat in irregular_beats]
            y_coords = [self.graph.signal_y[beat] for beat in irregular_beats]

            self.graph.irregular_beats_plot.setData(x_coords, y_coords)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
