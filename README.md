# ⚡ Electroquest
### An Interactive Electronics Laboratory

Electroquest is a web-based electronics lab assistant designed to bridge the gap between circuit theory and practical experimentation. It helps students simulate circuits, explore signals, diagnose faults and analyse real laboratory measurements.

## Features

### 1. Experiment Lab
- Explore the working principles of an RC low-pass filter.
- Configure resistance and capacitance values to observe their effect on circuit behaviour.
- Calculate cutoff frequency and analyse gain and phase response.
- Visualise the frequency response to understand how different frequencies are attenuated.

### 2. Virtual Instruments
- Generate sine, square, triangle and sawtooth waveforms.
- Adjust signal frequency, amplitude, phase and DC offset.
- Observe input and output signals through a virtual oscilloscope.
- Analyse signal characteristics using time-domain plots and FFT.

### 3. Fault Diagnosis
- Simulate common circuit faults, including incorrect component values, open and shorted components, and grounding or measurement errors.
- Compare expected and observed signal behaviour.
- Receive possible fault explanations and suggested troubleshooting checks.
- Understand how circuit faults affect the output waveform.

### 4. Hardware Analysis
- Enter practical laboratory measurements for comparison with theoretical values.
- Upload oscilloscope CSV data for signal analysis.
- Calculate gain and compare measured results with expected circuit behaviour.
- Visualise input and output waveforms to identify deviations.

## Scope and Limitations

Electroquest currently focuses on the RC low-pass filter as a foundation for interactive electronics experimentation. Its modular design allows additional circuits, experiments and diagnostic features to be introduced in future versions.

The circuit simulation uses a simplified signal-processing model rather than a full SPICE-based circuit solver. Fault diagnosis provides heuristic suggestions based on observed behaviour, so results should be verified through practical measurements and component testing.

**Future Scope**
- Extend support to additional analog and digital circuits.
- Introduce more advanced circuit simulation and analysis.
- Expand the fault library and improve diagnostic accuracy.
- Support more laboratory instruments and measurement formats.

## Tech Stack
- **Language:** Python
- **Framework:** Streamlit
- **Numerical Computing:** NumPy, SciPy
- **Visualisation:** Plotly

Deployed Link : https://electroquest.streamlit.app/
---

**Electroquest — Simulate. Measure. Diagnose. Understand.**
