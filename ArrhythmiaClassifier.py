import numpy as np
import neurokit2 as nk
from enum import Enum


class ArrhythmiaClass(Enum):
    A_FIB = 101
    TACHYCARDIA = 106
    BRADYCARDIA = 200
    NORMAL = 0


class ArrhythmiaClassifier:
    @staticmethod
    def detect_irregular_beats(ecg, start_idx, end_idx, sampling_rate=360):
        _, ecg_info = nk.ecg_process(ecg[start_idx:end_idx], sampling_rate=sampling_rate)

        r_peaks = np.array(ecg_info["ECG_R_Peaks"])
        p_peaks = np.array(ecg_info["ECG_P_Peaks"]) if "ECG_P_Peaks" in ecg_info else np.array([])

        # Extract RR intervals
        rr_intervals = np.array(ecg_info["ECG_fixpeaks_rr"])  # RR intervals in seconds
        median_rr = np.median(rr_intervals)  # Median RR for outlier detection

        afib_beats = []  # List to store beats detected as AFib

        for i in range(len(r_peaks) - 1):
            # Find P-waves before this R-peak
            prev_p_waves = p_peaks[(p_peaks < r_peaks[i]) & (p_peaks > r_peaks[i - 1])] if i > 0 else []

            # Conditions for AFib beat detection
            no_p_wave = len(prev_p_waves) == 0
            multiple_p_waves = len(prev_p_waves) > 1
            rr_outlier = abs(rr_intervals[i] - median_rr) > 0.3  # Threshold for RR irregularity

            if no_p_wave or multiple_p_waves or rr_outlier:
                afib_beats.append(r_peaks[i])  # Mark this beat as AFib

        if len(afib_beats) > 0:
            return ArrhythmiaClass.A_FIB, afib_beats, ecg_info

        heart_rate = 60 / rr_intervals
        if np.mean(heart_rate) < 50:
            return ArrhythmiaClass.BRADYCARDIA, ecg_info
        if np.mean(heart_rate) > 120:
            return ArrhythmiaClass.TACHYCARDIA, ecg_info

        return ArrhythmiaClass.NORMAL, ecg_info
