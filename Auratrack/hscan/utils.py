import numpy as np
from scipy.signal import find_peaks

def calculate_vitals(ir_data, red_data, sample_rate=100):
    """
    Takes arrays of raw IR and Red values and returns estimated HR and SpO2.
    """
    ir_array = np.array(ir_data)
    red_array = np.array(red_data)
    
    # 1. Heart Rate Calculation using Scipy Peak Detection
    # distance specifies the minimum samples between peaks (e.g., max 150 BPM)
    peaks, _ = find_peaks(ir_array, distance=sample_rate/2.5) 
    
    if len(peaks) > 1:
        # Calculate average distance between peaks in seconds
        avg_peak_interval = np.mean(np.diff(peaks)) / sample_rate
        bpm = 60.0 / avg_peak_interval
    else:
        bpm = 0.0 # Not enough data to find a pulse

    # 2. SpO2 Calculation (Simplified empirical ratio method)
    # SpO2 relies on the ratio of AC (fluctuating) to DC (static) signals
    ir_ac = np.std(ir_array)
    ir_dc = np.mean(ir_array)
    red_ac = np.std(red_array)
    red_dc = np.mean(red_array)

    if ir_dc > 0 and red_dc > 0:
        # R is the ratio of ratios
        R = (red_ac / red_dc) / (ir_ac / ir_dc)
        # Standard empirical formula for SpO2 calculation
        spo2 = 104.0 - 1.17 * R 
        # Cap realistic values
        spo2 = min(100.0, max(0.0, spo2))
    else:
        spo2 = 0.0

    return round(bpm, 1), round(spo2, 1)