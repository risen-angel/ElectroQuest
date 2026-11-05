
import csv
import numpy as np
from scipy.signal import bilinear, lfilter

# RC circuit
R = 10_000
C = 0.1e-6

# Signal settings
frequency = 3000
amplitude = 2
sampling_rate = 100000
duration = 0.02

# Generate input sine wave
t = np.arange(0, duration, 1 / sampling_rate)
x = amplitude * np.sin(2 * np.pi * frequency * t)

# Simulate RC low-pass filter
b, a = bilinear([1], [R*C, 1], fs=sampling_rate)
y = lfilter(b, a, x)

# Export CSV
with open("test-signal.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["time", "input", "output"])

    for time, vin, vout in zip(t, x, y):
        writer.writerow([
            f"{time:.8f}",
            f"{vin:.6f}",
            f"{vout:.6f}"
        ])

print("CSV generated successfully!")
