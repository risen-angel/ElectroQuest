
import csv
import io
import numpy as np


# ==========================================
# VALIDATE MANUAL MEASUREMENTS
# ==========================================

def validate_measurements(
    input_amplitude,
    output_amplitude,
    input_frequency,
    output_frequency
):

    errors = []

    if input_amplitude <= 0:
        errors.append("Input amplitude must be positive.")

    if output_amplitude < 0:
        errors.append("Output amplitude cannot be negative.")

    if input_frequency <= 0:
        errors.append("Input frequency must be positive.")

    if output_frequency < 0:
        errors.append("Output frequency cannot be negative.")

    return errors


# ==========================================
# ANALYZE MANUAL MEASUREMENTS
# ==========================================

def analyze_manual_measurements(
    input_amplitude,
    output_amplitude,
    input_frequency,
    output_frequency
):

    if input_amplitude <= 0:
        raise ValueError("Input amplitude must be positive.")

    gain = output_amplitude / input_amplitude

    gain_db = (
        20 * np.log10(gain)
        if gain > 0 else float("-inf")
    )

    frequency_error = (
        abs(output_frequency - input_frequency)
        / input_frequency
    ) * 100

    return {
        "gain": float(gain),
        "gain_db": float(gain_db),
        "frequency_error": float(frequency_error)
    }


# ==========================================
# LOAD OSCILLOSCOPE CSV
# ==========================================

def load_oscilloscope_csv(uploaded_file):

    content = uploaded_file.getvalue()

    try:
        decoded = content.decode("utf-8-sig")

    except UnicodeDecodeError:
        raise ValueError("CSV must use UTF-8 encoding.")

    reader = csv.DictReader(
        io.StringIO(decoded)
    )

    if not reader.fieldnames:
        raise ValueError("CSV file is empty.")

    headers = {
        name.strip().lower(): name
        for name in reader.fieldnames
        if name
    }

    required = {"time", "input", "output"}

    missing = required - set(headers)

    if missing:
        raise ValueError(
            "Missing columns: " + ", ".join(missing)
        )

    time_values = []
    input_values = []
    output_values = []

    for row_number, row in enumerate(reader, start=2):

        try:

            time_values.append(
                float(row[headers["time"]])
            )

            input_values.append(
                float(row[headers["input"]])
            )

            output_values.append(
                float(row[headers["output"]])
            )

        except (ValueError, TypeError):

            raise ValueError(
                f"Invalid measurement at row {row_number}."
            )

    t = np.asarray(time_values, dtype=float)
    x = np.asarray(input_values, dtype=float)
    y = np.asarray(output_values, dtype=float)

    if len(t) < 10:
        raise ValueError("At least 10 samples are required.")

    if not (
        np.all(np.isfinite(t))
        and np.all(np.isfinite(x))
        and np.all(np.isfinite(y))
    ):
        raise ValueError("Invalid numerical measurements.")

    differences = np.diff(t)

    if np.any(differences <= 0):
        raise ValueError(
            "Time values must be strictly increasing."
        )

    median_interval = np.median(differences)

    sampling_rate = 1 / median_interval

    irregular = (
        np.max(np.abs(differences - median_interval))
        / median_interval
    ) > 0.02

    data = {
        "time": t,
        "input": x,
        "output": y
    }

    return data, sampling_rate, irregular


# ==========================================
# ANALYZE CSV WAVEFORMS
# ==========================================

def analyze_csv(data):

    input_signal = data["input"]
    output_signal = data["output"]

    input_peak = np.ptp(input_signal) / 2
    output_peak = np.ptp(output_signal) / 2

    gain = (
        output_peak / input_peak
        if input_peak > 0 else 0
    )

    gain_db = (
        20 * np.log10(gain)
        if gain > 0 else float("-inf")
    )

    return {
        "input_peak": float(input_peak),
        "output_peak": float(output_peak),
        "gain": float(gain),
        "gain_db": float(gain_db)
    }
