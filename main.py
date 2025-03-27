import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import pandas as pd

from ArrhythmiaClassifier import ArrhythmiaClass, ArrhythmiaClassifier
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

        # self.detection_thread = ArrhythmiaDetectionThread(self)
        # self.detection_thread.detection_completed.connect(self.handle_arrhythmia_detection)
        #
        self.arrhythmia_timer = QTimer(self)
        self.arrhythmia_timer.timeout.connect(self.trigger_arrhythmia_detection)

        window_size = 1700
        detection_interval = (window_size * 1000) // 360  # Convert to milliseconds
        self.arrhythmia_timer.start(detection_interval)

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

        # Calculate start and end indices for the current window
        end_idx = graph.current_frame
        start_idx = 0

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
            self.ecgStatus.setText("Irrregular")
            # self.ecgStatus.setStyleSheet("color: red;")
        elif classification == ArrhythmiaClass.TACHYCARDIA:
            self.ecgClassification.setText("Tachycardia")
            self.ecgStatus.setText("Irregular")
            # self.ecgStatus.setStyleSheet("color: orange;")
        elif classification == ArrhythmiaClass.BRADYCARDIA:
            self.ecgClassification.setText("Bradycardia")
            self.ecgStatus.setText("Irregular")
            # self.ecgStatus.setStyleSheet("color: orange;")
        else:
            self.ecgClassification.setText("Normal")
            self.ecgStatus.setText("Within normal range")
            # self.ecgStatus.setStyleSheet("color: green;")

        self.heartBeatsValue.setText(str(round(heart_rate)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
