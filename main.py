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

        self.ecgLayout = self.findChild(QVBoxLayout, "ecgLayout")
        self.spo2Layout = self.findChild(QVBoxLayout, "spo2Layout")
        self.respLayout = self.findChild(QVBoxLayout, "respLayout")
        self.ecgClassification = self.findChild(QLabel, "ecgClassification")
        self.heartBeatsValue = self.findChild(QLabel, "ecgValue")
        self.ecgStatus = self.findChild(QLabel, "ecgStatus")

        self.ecgGraphWidget = pg.PlotWidget(self)
        self.ecgLayout.addWidget(self.ecgGraphWidget)
        self.ecgGraph = Graph(self.ecgGraphWidget, sampling_rate=360, window_size=1500)
        self.setWindowTitle('ECG')

        self.spo2GraphWidget = pg.PlotWidget(self)
        self.spo2Layout.addWidget(self.spo2GraphWidget)
        self.spo2Graph = Graph(self.spo2GraphWidget, sampling_rate=360, window_size=1500, color='#fd0900')
        self.setWindowTitle('SPO2')

        self.respGraphWidget = pg.PlotWidget(self)
        self.respLayout.addWidget(self.respGraphWidget)
        self.respGraph = Graph(self.respGraphWidget, sampling_rate=360, window_size=1500, color='#fbf906')
        self.setWindowTitle('Respiration')
        
        self.timer_connections = []
        self.read_data()
        self.read_spo2_data()
        self.read_resp_data()

        window_size = 1500  # 2 seconds at 360 Hz
        detection_interval = (window_size * 1000) // 360  # Convert to milliseconds
        # self.arrhythmia_timer.start(detection_interval)

    def read_resp_data(self):
        df = pd.read_csv("SPO2 & RESP/resp_signal_refined.csv")
        time = df["Time (s)"].values
        resp_values = df["RESP (breaths/min)"].values
        self.respGraph.set_signal(time, resp_values)

    def read_spo2_data(self):
        df = pd.read_csv("SPO2 & RESP/spo2_signal_refined.csv")
        time = df["Time (s)"].values
        spo2_values = df["SpO2 (%)"].values
        self.spo2Graph.set_signal(time, spo2_values)

    def read_data(self):
        df = pd.read_csv("ECGs/Atrial Fibrillation.csv")
        amplitude = df["Amplitude"].values
        time = (df["Time (ms)"] / 1000).values
        self.ecg = amplitude
        self.sampling_rate = 360
        self.ecgGraph.set_signal(time, amplitude)

    def trigger_arrhythmia_detection(self):
        graph = self.ecgGraph

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
            x_coords = [self.ecgGraph.signal_x[beat] for beat in irregular_beats]
            y_coords = [self.ecgGraph.signal_y[beat] for beat in irregular_beats]

            # self.graph.irregular_beats_plot.setData(x_coords, y_coords)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
