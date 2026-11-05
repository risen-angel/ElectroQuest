
import plotly.graph_objects as go


# ==========================================
# OSCILLOSCOPE
# ==========================================

def oscilloscope_plot(t, input_signal, output_signal,
                      title="Oscilloscope"):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t,
        y=input_signal,
        mode="lines",
        name="CH1 - Input",
        line=dict(color="#38BDF8", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=t,
        y=output_signal,
        mode="lines",
        name="CH2 - Output",
        line=dict(color="#F59E0B", width=2)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Time (seconds)",
        yaxis_title="Voltage (V)",
        template="plotly_dark",
        height=450,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=50, r=30, t=70, b=50)
    )

    return fig

# ==========================================
# FFT ANALYZER
# ==========================================

def fft_plot(
    frequencies,
    input_fft,
    output_fft
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=input_fft,
            name="Input Spectrum",
            line=dict(color="#38BDF8")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=output_fft,
            name="Output Spectrum",
            line=dict(color="#F59E0B")
        )
    )

    fig.update_layout(
        title="Frequency Spectrum",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Amplitude (V)",
        template="plotly_dark",
        height=400
    )

    return fig


# ==========================================
# FREQUENCY RESPONSE
# ==========================================

def frequency_response_plot(
    frequencies,
    gain_db,
    cutoff_frequency
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=gain_db,
            name="Magnitude Response",
            line=dict(color="#38BDF8", width=3)
        )
    )

    fig.add_vline(
        x=cutoff_frequency,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text="Cutoff Frequency"
    )

    fig.add_hline(
        y=-3.01,
        line_dash="dot",
        line_color="#EF4444",
        annotation_text="-3 dB"
    )

    fig.update_layout(
        title="RC Low-Pass Frequency Response",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Gain (dB)",
        xaxis_type="log",
        template="plotly_dark",
        height=400
    )

    return fig


# ==========================================
# EXPECTED VS OBSERVED
# ==========================================


def measurement_comparison_plot(expected, observed):

    labels = list(expected.keys())

    expected_values = [
        float(expected[label]) for label in labels
    ]

    observed_values = [
        float(observed[label]) for label in labels
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Expected",
        x=labels,
        y=expected_values,
        marker_color="#38BDF8"
    ))

    fig.add_trace(go.Bar(
        name="Observed",
        x=labels,
        y=observed_values,
        marker_color="#F59E0B"
    ))

    fig.update_layout(
        title="Expected vs Observed Measurements",
        xaxis_title="Measurement",
        yaxis_title="Voltage (V)",
        barmode="group",
        template="plotly_dark",
        height=400
    )

    return fig

