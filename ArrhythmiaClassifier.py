import numpy as np
import neurokit2 as nk
# from biosppy.signals import ecg
from enum import Enum

from PyQt5.QtCore import QThread, pyqtSignal


class ArrhythmiaClass(Enum):
    A_FIB = 101
    TACHYCARDIA = 106
    BRADYCARDIA = 200
    NORMAL = 0


class ArrhythmiaClassifier:
    @staticmethod
    def detect_irregular_beats(signal, sampling_rate=360):
        _, ecg_info = nk.ecg_process(signal, sampling_rate=sampling_rate)

        # r_peaks = ecg.ecg(signal=signal, sampling_rate=sampling_rate)[2]
        r_peaks = np.array(ecg_info["ECG_R_Peaks"])
        p_peaks = np.array(ecg_info["ECG_P_Peaks"]) if "ECG_P_Peaks" in ecg_info else np.array([])

        # Extract RR intervals
        rr_intervals = np.array(ecg_info["ECG_fixpeaks_rr"])  # RR intervals in seconds
        # rr_intervals = np.diff(r_peaks) / sampling_rate  # RR intervals in seconds
        median_rr = np.median(rr_intervals)  # Median RR for outlier detection

        afib_beats = []  # List to store beats detected as AFib

        for i in range(len(r_peaks) - 1):
            # P waves before the r peak
            prev_p_waves = p_peaks[(p_peaks < r_peaks[i]) & (p_peaks > r_peaks[i - 1])] if i > 0 else []

            no_p_wave = len(prev_p_waves) == 0
            multiple_p_waves = len(prev_p_waves) > 1
            rr_outlier = abs(rr_intervals[i] - median_rr) > 0.3  # Threshold for RR irregularity

            if no_p_wave or multiple_p_waves or rr_outlier:
                afib_beats.append(r_peaks[i])
            # if rr_outlier:
            #     afib_beats.append(r_peaks[i])

        heart_rates = 60 / rr_intervals
        heart_rate = np.mean(heart_rates)

        if np.mean(heart_rate) < 50:
            return ArrhythmiaClass.BRADYCARDIA, heart_rate
        if np.mean(heart_rate) > 120:
            return ArrhythmiaClass.TACHYCARDIA, heart_rate
        if len(afib_beats) > 0:
            return ArrhythmiaClass.A_FIB, afib_beats, heart_rate

        return ArrhythmiaClass.NORMAL, heart_rate


# class DetectionThread(QThread):
#     detection_completed = pyqtSignal(ArrhythmiaClass, list, dict)
#
#     def __init__(self, parent=None, signal=None, start_idx=0, end_idx=0, sampling_rate=360):
#         super().__init__(parent)
#
#         print(f"start_idx: {start_idx}, end_idx: {end_idx}")
#
#         self.signal = signal[start_idx:end_idx].copy()
#         self.sampling_rate = sampling_rate
#
#     def run(self):
#         classification, irregular_beats, heart_rate = ArrhythmiaClassifier.detect_irregular_beats(
#             self.signal, self.sampling_rate
#         )
#         self.detection_completed.emit(classification, irregular_beats, heart_rate)

