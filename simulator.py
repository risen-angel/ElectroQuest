
import numpy as np
from scipy import signal


# ==========================================
# SIGNAL GENERATOR
# ==========================================

def generate_signal(
    waveform="Sine",
    amplitude=2.0,
    frequency=1000.0,
    phase=0.0,
    offset=0.0,
    duration=0.02,
    sampling_rate=100000
):

    if frequency <= 0 or sampling_rate <= 0:
        raise ValueError("Frequency and sampling rate must be positive.")

    if frequency >= sampling_rate / 2:
        raise ValueError("Frequency must be below Nyquist frequency.")

    if duration <= 0:
        raise ValueError("Duration must be positive.")

    t = np.arange(
        0,
        duration,
        1 / sampling_rate
    )

    angle = (
        2 * np.pi * frequency * t
        + np.deg2rad(phase)
    )

    if waveform == "Sine":
        x = amplitude * np.sin(angle)

    elif waveform == "Square":
        x = amplitude * signal.square(angle)

    elif waveform == "Triangle":
        x = amplitude * signal.sawtooth(
            angle,
            width=0.5
        )

    elif waveform == "Sawtooth":
        x = amplitude * signal.sawtooth(angle)

    else:
        raise ValueError("Unsupported waveform.")

    return t, x + offset


# ==========================================
# RC CIRCUIT CALCULATIONS
# ==========================================

def calculate_cutoff(R, C):

    if R <= 0 or C <= 0:
        raise ValueError("R and C must be positive.")

    return 1 / (2 * np.pi * R * C)


def calculate_response(frequencies, R, C):

    fc = calculate_cutoff(R, C)

    ratio = frequencies / fc

    magnitude = 1 / np.sqrt(
        1 + ratio**2
    )

    phase = -np.arctan(ratio)

    gain_db = 20 * np.log10(
        np.maximum(magnitude, 1e-12)
    )

    return magnitude, gain_db, np.degrees(phase)


# ==========================================
# RC FILTER SIMULATION
# ==========================================

def simulate_rc_filter(
    x,
    sampling_rate,
    R,
    C,
    fault="Healthy"
):

    if R <= 0 or C <= 0:
        raise ValueError("R and C must be positive.")

    if sampling_rate <= 0:
        raise ValueError("Sampling rate must be positive.")

    if fault == "Open Resistor":
        return np.zeros_like(x)

    if fault == "Open Capacitor":
        return x.copy()

    if fault == "Shorted Capacitor":
        return np.zeros_like(x)

    if fault == "Missing Ground":
        return np.zeros_like(x)

    if fault == "Wrong Output Node":
        return x.copy()

    if fault == "Wrong Resistor Value":
        R *= 5

    elif fault == "Wrong Capacitor Value":
        C *= 5

    RC = R * C

    numerator = [1]
    denominator = [RC, 1]

    b, a = signal.bilinear(
        numerator,
        denominator,
        fs=sampling_rate
    )

    zi = signal.lfilter_zi(b, a) * x[0]

    y, _ = signal.lfilter(
        b,
        a,
        x,
        zi=zi
    )

    return y


# ==========================================
# FFT ANALYSIS
# ==========================================

def calculate_fft(x, sampling_rate):

    x = np.asarray(x, dtype=float)

    N = len(x)

    if N < 4:
        return np.array([]), np.array([])

    if not np.all(np.isfinite(x)):
        return np.array([]), np.array([])

    centered = x - np.mean(x)

    window = np.hanning(N)

    transformed = np.fft.rfft(
        centered * window
    )

    frequencies = np.fft.rfftfreq(
        N,
        d=1 / sampling_rate
    )

    amplitudes = (
        np.abs(transformed)
        * 2 / np.sum(window)
    )

    amplitudes[0] /= 2

    if N % 2 == 0:
        amplitudes[-1] /= 2

    return frequencies, amplitudes


# ==========================================
# SIGNAL MEASUREMENTS
# ==========================================

def calculate_signal_metrics(x):

    x = np.asarray(x, dtype=float)

    x = x[np.isfinite(x)]

    if len(x) == 0:
        return {
            "peak": 0.0,
            "peak_to_peak": 0.0,
            "rms": 0.0,
            "mean": 0.0
        }

    centered = x - np.mean(x)

    return {
        "peak": float(np.max(np.abs(centered))),
        "peak_to_peak": float(np.ptp(x)),
        "rms": float(np.sqrt(np.mean(centered**2))),
        "mean": float(np.mean(x))
    }
