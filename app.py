import textwrap
import streamlit as st
import numpy as np

from simulator import (
    generate_signal,
    calculate_cutoff,
    calculate_response,
    simulate_rc_filter,
    calculate_fft,
    calculate_signal_metrics,
)
from diagnostics import diagnose
from hardware import (
    validate_measurements,
    analyze_manual_measurements,
    load_oscilloscope_csv,
    analyze_csv,
)
from plots import (
    oscilloscope_plot,
    fft_plot,
    frequency_response_plot,
    measurement_comparison_plot,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Electroquest",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HTML HELPER
# textwrap.dedent removes common indentation so Streamlit
# doesn't interpret HTML as a Markdown code block.
# ============================================================

def render_html(content):
    st.markdown(
        textwrap.dedent(content).strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# DESIGN SYSTEM
# ============================================================

render_html("""
<style>
:root {
    --bg: #FFF9FB;
    --white: #FFFFFF;
    --pink: #D987A9;
    --pink-dark: #B9688C;
    --plum: #572B45;
    --text: #493744;
    --muted: #907D89;
    --border: #EEDDE5;
}

.stApp {
    background:
        radial-gradient(circle at 90% 10%, rgba(244,210,226,.38), transparent 30%),
        radial-gradient(circle at 5% 90%, rgba(232,219,240,.25), transparent 25%),
        var(--bg);
    color: var(--text);
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

.block-container {
    max-width: 1380px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 { color: var(--plum) !important; }
p, label { color: var(--text); }

/* Header */
.brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 15px 20px;
    background: rgba(255,255,255,.9);
    border: 1px solid var(--border);
    border-radius: 15px;
    box-shadow: 0 4px 18px rgba(92,55,75,.04);
    margin-bottom: 15px;
}
.brand-name {
    font-size: 22px;
    font-weight: 800;
    color: var(--plum);
    letter-spacing: -.7px;
}
.brand-subtitle {
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 1.7px;
    font-weight: 650;
}
.status {
    background: #E9F3EC;
    color: #558168;
    padding: 7px 12px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 750;
    white-space: nowrap;
}

/* Homepage hero */
.hero-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 40px;
    padding: 58px 38px 48px;
    min-height: 365px;
}
.hero-content { flex: 1.2; min-width: 0; }
.hero-label {
    display: inline-block;
    background: #F8E0EA;
    color: #A65379;
    padding: 8px 17px;
    border-radius: 30px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 23px;
}
.hero-title {
    font-size: clamp(36px, 4.4vw, 57px);
    line-height: 1.12;
    letter-spacing: -2px;
    font-weight: 800;
    color: var(--plum);
}
.hero-title span { color: #B85E83; }
.hero-description {
    font-size: 16px;
    line-height: 1.8;
    color: var(--muted);
    max-width: 570px;
    margin-top: 18px;
}

/* CSS oscilloscope illustration */
.scope-art {
    flex: .9;
    min-width: 270px;
    max-width: 440px;
    width: 100%;
    padding: 20px;
    position: relative;
    margin: 0 auto;
}
.scope-glow {
    background: linear-gradient(140deg, rgba(249,220,233,.85), rgba(238,222,242,.75));
    border-radius: 50%;
    width: 90%;
    height: 90%;
    position: absolute;
    right: 2%;
    top: 3%;
    z-index: 0;
}
.scope-device {
    position: relative;
    z-index: 1;
    background: linear-gradient(145deg,#FFFFFF,#F8E9F0);
    border: 2px solid #D98CAA;
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 22px 45px rgba(160,85,120,.16);
    transform: rotate(-2deg);
}
.scope-screen {
    background: #302437;
    border: 5px solid #E6A5BE;
    border-radius: 10px;
    padding: 13px;
}
.scope-screen svg { width: 100%; display: block; }
.scope-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 5px 0;
}
.scope-knob {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(145deg,#FFFFFF,#E8C4D4);
    border: 2px solid #D58AA8;
}
.scope-buttons { display: flex; gap: 7px; }
.scope-buttons span {
    display: block;
    width: 30px;
    height: 12px;
    border: 1px solid #CB829F;
    border-radius: 4px;
    background: #F9DCE8;
}

/* Workspace cards */
.workspace-heading {
    display: flex;
    align-items: center;
    gap: 25px;
    justify-content: center;
    margin: 12px 0 28px;
}
.workspace-heading span {
    height: 1px;
    background: #E9C7D6;
    flex: 1;
}
.workspace-heading p {
    font-size: 12px;
    letter-spacing: 4px;
    font-weight: 750;
    color: var(--plum);
    white-space: nowrap;
    margin: 0;
}
.lab-card {
    background: rgba(255,255,255,.92);
    border: 1px solid var(--border);
    border-radius: 19px;
    padding: 22px 18px;
    min-height: 190px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 7px 22px rgba(92,55,75,.045);
    transition: all .25s ease;
}
.lab-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 28px rgba(169,103,133,.13);
    border-color: #E7B5CA;
}
.lab-card:after {
    content: "";
    position: absolute;
    width: 150%;
    height: 45px;
    bottom: -26px;
    left: -15%;
    border-radius: 50%;
    opacity: .65;
}
.pink-card:after { background: #F7DCE7; }
.purple-card:after { background: #EAE0F2; }
.peach-card:after { background: #F9E5D9; }
.green-card:after { background: #E2EEE5; }
.card-icon {
    width: 45px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    color: white;
    font-size: 23px;
    margin-bottom: 15px;
}
.pink-card .card-icon { background: linear-gradient(135deg,#E99BB7,#CC6590); }
.purple-card .card-icon { background: linear-gradient(135deg,#C38BCB,#9462A7); }
.peach-card .card-icon { background: linear-gradient(135deg,#F0B58D,#D88D63); }
.green-card .card-icon { background: linear-gradient(135deg,#9DC8A8,#6EA47E); }
.card-title {
    font-size: 17px;
    font-weight: 800;
    color: var(--plum);
    margin-bottom: 8px;
}
.card-description {
    font-size: 12px;
    line-height: 1.6;
    color: var(--muted);
    min-height: 58px;
}
.card-arrow {
    position: absolute;
    right: 17px;
    bottom: 15px;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(237,210,223,.7);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--plum);
    font-size: 19px;
    z-index: 2;
}

/* Internal page headings and panels */
.section-label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    color: var(--pink-dark);
    margin-bottom: 7px;
}
.section-title {
    font-size: 30px;
    font-weight: 800;
    color: var(--plum);
}
.section-description {
    font-size: 14px;
    color: var(--muted);
}
.panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 15px;
}
.panel-title {
    font-size: 16px;
    font-weight: 750;
    color: var(--plum);
}
.panel-description {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.6;
}

/* Inputs and controls */
.stButton > button {
    width: 100%;
    border-radius: 11px;
    min-height: 42px;
    background: white;
    color: var(--plum);
    border: 1px solid var(--border);
    font-weight: 650;
    transition: .2s ease;
}
.stButton > button:hover {
    background: #FFF0F5;
    border-color: var(--pink);
    color: var(--pink-dark);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#CE7097,#AD527B);
    color: white;
    border: none;
}
.stButton > button[kind="primary"]:hover {
    background: #A94D75;
    color: white;
}
.stNumberInput input,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    background: white !important;
    border-radius: 10px !important;
    border-color: var(--border) !important;
}
.stFileUploader section {
    background: #FFF8FB;
    border: 1px dashed #DDA8BF;
    border-radius: 13px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
[data-testid="stMetricValue"] { color: var(--plum) !important; }
[data-testid="stExpander"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
}
hr { border-color: var(--border); }
.footer {
    text-align: center;
    margin-top: 42px;
    padding: 20px 0;
    color: #B49BA9;
    font-size: 10px;
    letter-spacing: 3px;
}

/* Smaller screens */
@media (max-width: 850px) {
    .hero-section {
        flex-direction: column;
        padding: 30px 10px;
        gap: 10px;
    }
    .scope-art { max-width: 390px; }
    .hero-title { font-size: 38px; }
    .workspace-heading p { letter-spacing: 2px; font-size: 10px; }
}
</style>
""")


# ============================================================
# SESSION STATE AND REUSABLE UI
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"


def navigate(page):
    st.session_state.page = page


def go_home():
    navigate("Home")
    st.rerun()


def brand_header():
    render_html("""
    <div class="brand-header">
        <div>
            <div class="brand-name">⚡ Electroquest</div>
            <div class="brand-subtitle">INTERACTIVE ELECTRONICS LABORATORY</div>
        </div>
        <div class="status">● SYSTEM READY</div>
    </div>
    """)


def page_header(title, description, category="LAB MODULE"):
    col1, _ = st.columns([1, 5])
    with col1:
        if st.button("← Home", key=f"home_{title}"):
            go_home()

    render_html(f"""
    <div style="padding:12px 0 20px;">
        <div class="section-label">{category}</div>
        <div class="section-title">{title}</div>
        <div class="section-description">{description}</div>
    </div>
    """)
    st.divider()


def show_diagnostic_results(results):
    if isinstance(results, dict):
        candidates = results.get("candidates", results.get("results", []))
        if candidates:
            results = candidates
        else:
            st.write(results)
            return

    if isinstance(results, list):
        if not results:
            st.info("No significant fault detected.")
            return

        for result in results:
            if not isinstance(result, dict):
                st.write(result)
                continue

            name = result.get("fault", result.get("name", "Possible fault"))
            with st.expander(name, expanded=True):
                st.write(result.get(
                    "explanation",
                    result.get("description", "No explanation available.")
                ))

                score = result.get("confidence_score")
                if score is not None:
                    st.caption(f"Diagnostic score: {float(score):.1f}%")

                checks = result.get("checks", result.get("steps", []))
                if checks:
                    st.markdown("**Suggested verification steps**")
                    for check in checks:
                        st.write(f"• {check}")
    else:
        st.write(results)


def get_csv_components(loaded):
    """Handle the tuple or dictionary format returned by the CSV loader."""
    if isinstance(loaded, tuple):
        data = loaded[0]
        sampling_rate = loaded[1] if len(loaded) > 1 else None
        irregular = loaded[2] if len(loaded) > 2 else False
    elif isinstance(loaded, dict):
        data = loaded.get("data", loaded)
        sampling_rate = loaded.get("sampling_rate")
        irregular = loaded.get("irregular", False)
    else:
        raise ValueError("Unexpected CSV loader return format.")

    required = ("time", "input", "output")
    if not all(key in data for key in required):
        raise ValueError("CSV must contain time, input and output columns.")

    if sampling_rate is None:
        sampling_rate = 1 / np.median(np.diff(data["time"]))

    return data, float(sampling_rate), bool(irregular)


def footer():
    render_html("""
    <div class="footer">
        ELECTROQUEST · EXPLORE · EXPERIMENT · UNDERSTAND
    </div>
    """)


# ============================================================
# HOME PAGE
# ============================================================

def home_page():
    render_html("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-label">THE INTERACTIVE ELECTRONICS LAB</div>
            <div class="hero-title">
                Understand circuits<br>
                <span>beyond the classroom.</span>
            </div>
            <div class="hero-description">
                Simulate circuits, experiment with virtual instruments,
                investigate faults and analyse real laboratory readings.
            </div>
        </div>

<div class="scope-art"><div class="scope-glow"></div><div class="scope-device"><div class="scope-screen"><svg viewBox="0 0 300 130" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="eq-grid" width="30" height="26" patternUnits="userSpaceOnUse"><path d="M30 0H0V26" fill="none" stroke="#95647F" stroke-width="0.7"/></pattern></defs><rect width="300" height="130" fill="url(#eq-grid)"/><path d="M0 65 C15 5,30 5,45 65 S75 125,90 65 S120 5,135 65 S165 125,180 65 S210 5,225 65 S255 125,270 65 S285 5,300 65" fill="none" stroke="#F6A9C9" stroke-width="3" stroke-linecap="round"/><path d="M0 65 C20 65,25 28,45 28 S70 65,90 65 S115 102,135 102 S160 65,180 65 S205 28,225 28 S250 65,270 65" fill="none" stroke="#72D6D0" stroke-width="2" opacity=".9"/></svg></div><div class="scope-controls"><div class="scope-buttons"><span></span><span></span><span></span><span></span></div><div class="scope-knob"></div></div></div></div>
    </div>
    """)

    # A single, unobtrusive call to action.
    _, cta, _ = st.columns([1, 1.2, 1])
    with cta:
        if st.button(
            "Choose a laboratory  →",
            type="primary",
            use_container_width=True,
            key="home_cta",
        ):
            st.session_state.show_workspace = True
            st.rerun()

    render_html("""
    <div class="workspace-heading">
        <span></span>
        <p>YOUR LABORATORY WORKSPACE</p>
        <span></span>
    </div>
    """)

    cards = [
        {
            "title": "Experiment Lab",
            "icon": "⌁",
            "description": "Explore the RC low-pass filter and understand its frequency response.",
            "style": "pink-card",
            "page": "Experiment Lab",
        },
        {
            "title": "Virtual Instruments",
            "icon": "∿",
            "description": "Generate signals, use an oscilloscope and inspect frequency components.",
            "style": "purple-card",
            "page": "Virtual Instruments",
        },
        {
            "title": "Fault Diagnosis",
            "icon": "⚒",
            "description": "Introduce circuit faults, observe their effects and learn troubleshooting.",
            "style": "peach-card",
            "page": "Fault Diagnosis",
        },
        {
            "title": "Hardware Analysis",
            "icon": "▥",
            "description": "Enter laboratory readings or upload oscilloscope CSV data.",
            "style": "green-card",
            "page": "Hardware Analysis",
        },
    ]

    cols = st.columns(4, gap="medium")
    for col, card in zip(cols, cards):
        with col:
            render_html(f"""
            <div class="lab-card {card['style']}">
                <div class="card-icon">{card['icon']}</div>
                <div class="card-title">{card['title']}</div>
                <div class="card-description">{card['description']}</div>
                <div class="card-arrow">→</div>
            </div>
            """)
            if st.button(
                f"Open {card['title']}",
                key=f"home_{card['page']}",
                use_container_width=True,
            ):
                navigate(card["page"])
                st.rerun()


# ============================================================
# EXPERIMENT LAB
# ============================================================

def experiment_lab():
    page_header(
        "Experiment Lab",
        "Explore the behaviour of an RC low-pass filter.",
        "CIRCUIT EXPLORATION",
    )

    render_html("""
    <div class="panel">
        <div class="panel-title">RC Low-Pass Filter</div>
        <div class="panel-description">
            A passive filter that allows low frequencies to pass
            while attenuating higher frequencies.
        </div>
        <br>
        <div style="font-family:monospace;font-size:17px;color:#572B45;line-height:2;">
            Vin ───── R ─────┬──── Vout<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;GND
        </div>
    </div>
    """)

    st.markdown("### Circuit parameters")
    col1, col2 = st.columns(2)

    with col1:
        R = st.number_input(
            "Resistance (kΩ)", min_value=0.1, max_value=1000.0,
            value=10.0, key="lab_R"
        )
    with col2:
        C = st.number_input(
            "Capacitance (µF)", min_value=0.001, max_value=1000.0,
            value=0.1, key="lab_C"
        )

    R_actual = R * 1000
    C_actual = C * 1e-6
    cutoff = calculate_cutoff(R_actual, C_actual)
    tau = R_actual * C_actual

    c1, c2, c3 = st.columns(3)
    c1.metric("Cutoff frequency", f"{cutoff:.2f} Hz")
    c2.metric("Time constant", f"{tau:.6f} s")
    c3.metric("Resistance", f"{R:.2f} kΩ")

    st.divider()
    st.markdown("### Frequency response")

    frequencies = np.logspace(0, 6, 500)
    _, gain_db, _ = calculate_response(
        frequencies, R_actual, C_actual
    )

    st.plotly_chart(
        frequency_response_plot(frequencies, gain_db, cutoff),
        use_container_width=True,
    )

    st.markdown("### Circuit theory")
    with st.expander("Cutoff frequency"):
        st.write(
            "At cutoff, output amplitude falls to approximately "
            "70.7% of the input amplitude."
        )
        st.latex(r"f_c = \frac{1}{2\pi RC}")

    with st.expander("Transfer function"):
        st.latex(r"H(s) = \frac{1}{1+sRC}")

    with st.expander("Magnitude and phase"):
        st.latex(r"|H(f)| = \frac{1}{\sqrt{1+(f/f_c)^2}}")
        st.latex(r"\phi = -\tan^{-1}(f/f_c)")

    st.info(
        "At cutoff frequency, gain is approximately -3 dB "
        "and phase shift is approximately -45°."
    )


# ============================================================
# VIRTUAL INSTRUMENTS
# ============================================================

def virtual_instruments():
    page_header(
        "Virtual Instruments",
        "Generate signals and observe how your circuit responds.",
        "SIGNAL LABORATORY",
    )

    st.markdown("### Function generator")
    col1, col2 = st.columns(2)

    with col1:
        waveform = st.selectbox(
            "Waveform", ["Sine", "Square", "Triangle", "Sawtooth"]
        )
        frequency = st.slider(
            "Frequency (Hz)", 100, 5000, 1000, 100
        )
        amplitude = st.slider(
            "Amplitude (V peak)", 0.1, 5.0, 2.0, 0.1
        )

    with col2:
        offset = st.slider("DC offset (V)", -2.0, 2.0, 0.0, 0.1)
        phase = st.slider("Phase (degrees)", 0, 360, 0, 5)
        R = st.number_input(
            "Resistance (kΩ)", min_value=0.1,
            value=10.0, key="instrument_R"
        )
        C = st.number_input(
            "Capacitance (µF)", min_value=0.001,
            value=0.1, key="instrument_C"
        )

    R_actual = R * 1000
    C_actual = C * 1e-6
    cutoff = calculate_cutoff(R_actual, C_actual)

    fs = 100000
    duration = 5 / frequency

    t, x = generate_signal(
        waveform=waveform,
        amplitude=amplitude,
        frequency=frequency,
        phase=phase,
        offset=offset,
        duration=duration,
        sampling_rate=fs,
    )

    y = simulate_rc_filter(x, fs, R_actual, C_actual)

    st.divider()
    st.markdown("### Oscilloscope")

    c1, c2 = st.columns(2)
    with c1:
        time_div = st.selectbox(
            "Time / division (ms)",
            [0.1, 0.2, 0.5, 1, 2, 5, 10],
            index=3,
        )
    with c2:
        volts_div = st.selectbox(
            "Volts / division",
            [0.1, 0.2, 0.5, 1, 2, 5],
            index=3,
        )

    visible_duration = min(time_div * 10 / 1000, duration)
    visible_samples = max(2, int(visible_duration * fs))

    st.plotly_chart(
        oscilloscope_plot(
            t[:visible_samples],
            x[:visible_samples],
            y[:visible_samples],
            title="Oscilloscope · CH1 Input / CH2 Output",
        ),
        use_container_width=True,
    )

    input_metrics = calculate_signal_metrics(x)
    output_metrics = calculate_signal_metrics(y)

    st.markdown("### Measurement readings")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**CH1 · Input**")
        a, b = st.columns(2)
        a.metric("Peak-to-peak", f"{input_metrics['peak_to_peak']:.3f} V")
        b.metric("RMS", f"{input_metrics['rms']:.3f} V")

    with c2:
        st.markdown("**CH2 · Output**")
        a, b = st.columns(2)
        a.metric("Peak-to-peak", f"{output_metrics['peak_to_peak']:.3f} V")
        b.metric("RMS", f"{output_metrics['rms']:.3f} V")

    ratio = (
        output_metrics["peak"] / input_metrics["peak"]
        if input_metrics["peak"] > 0 else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Cutoff frequency", f"{cutoff:.2f} Hz")
    c2.metric("Input frequency", f"{frequency} Hz")
    c3.metric("Output / Input ratio", f"{ratio:.3f}")

    st.divider()
    st.markdown("### FFT analyser")

    f_in, fft_in = calculate_fft(x, fs)
    f_out, fft_out = calculate_fft(y, fs)

    st.plotly_chart(
        fft_plot(f_in, fft_in, fft_out),
        use_container_width=True,
    )
    st.caption(
        "FFT resolution depends on recording duration and sampling rate."
    )


# ============================================================
# FAULT DIAGNOSIS
# ============================================================

def fault_diagnosis():
    page_header(
        "Fault Diagnosis",
        "Investigate circuit faults and learn how to verify them.",
        "TROUBLESHOOTING LAB",
    )

    render_html("""
    <div class="panel">
        <div class="panel-title">Diagnostic workspace</div>
        <div class="panel-description">
            Introduce a fault, observe the output waveform and
            investigate possible causes.
        </div>
    </div>
    """)

    fault_options = [
        "Healthy",
        "Wrong Resistor Value",
        "Wrong Capacitor Value",
        "Open Resistor",
        "Open Capacitor",
        "Shorted Capacitor",
        "Missing Ground",
        "Wrong Output Node",
        "Incorrect Function Generator Settings",
    ]

    selected_fault = st.selectbox("Circuit condition", fault_options)

    c1, c2 = st.columns(2)
    with c1:
        R = st.number_input(
            "Resistance (kΩ)", min_value=0.1,
            value=10.0, key="fault_R"
        )
    with c2:
        C = st.number_input(
            "Capacitance (µF)", min_value=0.001,
            value=0.1, key="fault_C"
        )

    c1, c2 = st.columns(2)
    with c1:
        frequency = st.number_input(
            "Input frequency (Hz)", min_value=1.0,
            value=1000.0, key="fault_frequency"
        )
    with c2:
        amplitude = st.number_input(
            "Input amplitude (V peak)", min_value=0.1,
            value=2.0, key="fault_amplitude"
        )

    if st.button(
        "Run fault simulation",
        type="primary",
        use_container_width=True,
    ):
        R_actual = R * 1000
        C_actual = C * 1e-6
        fs = 100000

        if selected_fault == "Incorrect Function Generator Settings":
            t, x = generate_signal(
                waveform="Square",
                amplitude=amplitude * 0.5,
                frequency=frequency * 2,
                duration=5 / frequency,
                sampling_rate=fs,
            )
            y = simulate_rc_filter(x, fs, R_actual, C_actual)
        else:
            t, x = generate_signal(
                waveform="Sine",
                amplitude=amplitude,
                frequency=frequency,
                duration=5 / frequency,
                sampling_rate=fs,
            )
            y = simulate_rc_filter(
                x, fs, R_actual, C_actual, fault=selected_fault
            )

        if selected_fault == "Missing Ground":
            y = np.zeros_like(x)
        elif selected_fault == "Wrong Output Node":
            y = x.copy()

        st.markdown("### Observed circuit response")
        st.plotly_chart(
            oscilloscope_plot(
                t, x, y,
                title=f"Fault simulation · {selected_fault}",
            ),
            use_container_width=True,
        )

        input_metrics = calculate_signal_metrics(x)
        output_metrics = calculate_signal_metrics(y)

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Input peak-to-peak",
            f"{input_metrics['peak_to_peak']:.3f} V",
        )
        c2.metric(
            "Output peak-to-peak",
            f"{output_metrics['peak_to_peak']:.3f} V",
        )
        c3.metric("Output RMS", f"{output_metrics['rms']:.3f} V")

        cutoff = calculate_cutoff(R_actual, C_actual)
        results = diagnose(
            expected_amplitude=input_metrics["peak"],
            observed_amplitude=output_metrics["peak"],
            expected_frequency=frequency,
            observed_frequency=frequency,
            expected_cutoff=cutoff,
            selected_fault=selected_fault,
        )

        st.markdown("### Diagnostic assessment")
        if selected_fault == "Healthy":
            st.success("Healthy circuit condition selected.")
        else:
            st.warning(f"Injected condition: {selected_fault}")

        show_diagnostic_results(results)

        st.info(
            "This is a simplified fault model. A waveform alone cannot "
            "always distinguish a loose connection from component failure. "
            "Verify suspected faults with continuity and multimeter checks."
        )


# ============================================================
# HARDWARE ANALYSIS
# ============================================================

def hardware_analysis():
    page_header(
        "Hardware Analysis",
        "Compare actual laboratory readings with theoretical results.",
        "REAL-WORLD MEASUREMENTS",
    )

    mode = st.radio(
        "Analysis method",
        ["Manual Measurements", "Upload Oscilloscope CSV"],
        horizontal=True,
    )
    st.divider()

    if mode == "Manual Measurements":
        st.markdown("### Circuit configuration")
        c1, c2 = st.columns(2)

        with c1:
            R = st.number_input(
                "Resistance (kΩ)", min_value=0.1,
                value=10.0, key="hardware_R"
            )
        with c2:
            C = st.number_input(
                "Capacitance (µF)", min_value=0.001,
                value=0.1, key="hardware_C"
            )

        st.markdown("### Input and output readings")
        c1, c2 = st.columns(2)

        with c1:
            input_amplitude = st.number_input(
                "Input amplitude (V peak)", min_value=0.0, value=2.0
            )
            input_frequency = st.number_input(
                "Input frequency (Hz)", min_value=1.0, value=100.0
            )

        with c2:
            output_amplitude = st.number_input(
                "Observed output amplitude (V peak)",
                min_value=0.0, value=1.69
            )
            output_frequency = st.number_input(
                "Observed output frequency (Hz)",
                min_value=1.0, value=100.0
            )

        st.markdown("### Connection verification")
        c1, c2, c3 = st.columns(3)

        with c1:
            ground_connected = st.checkbox("Ground verified", value=True)
        with c2:
            output_node_correct = st.checkbox("Output node verified", value=True)
        with c3:
            generator_correct = st.checkbox("Generator verified", value=True)

        if st.button(
            "Analyse hardware readings",
            type="primary",
            use_container_width=True,
        ):
            errors = validate_measurements(
                input_amplitude,
                output_amplitude,
                input_frequency,
                output_frequency,
            )

            if errors:
                for error in errors:
                    st.error(error)
            else:
                R_actual = R * 1000
                C_actual = C * 1e-6
                cutoff = calculate_cutoff(R_actual, C_actual)

                result = analyze_manual_measurements(
                    input_amplitude,
                    output_amplitude,
                    input_frequency,
                    output_frequency,
                )

                expected_gain = 1 / np.sqrt(
                    1 + (input_frequency / cutoff) ** 2
                )
                expected_output = input_amplitude * expected_gain

                st.divider()
                st.markdown("### Measurement results")

                c1, c2, c3 = st.columns(3)
                c1.metric("Expected output", f"{expected_output:.3f} V")
                c2.metric("Observed output", f"{output_amplitude:.3f} V")
                c3.metric("Observed gain", f"{result['gain']:.3f}")

                st.plotly_chart(
                    measurement_comparison_plot(
                        expected={"Output Amplitude": expected_output},
                        observed={"Output Amplitude": output_amplitude},
                    ),
                    use_container_width=True,
                )

                st.markdown("### Diagnostic suggestions")
                diagnosis_results = diagnose(
                    expected_amplitude=expected_output,
                    observed_amplitude=output_amplitude,
                    expected_frequency=input_frequency,
                    observed_frequency=output_frequency,
                    expected_cutoff=cutoff,
                    ground_connected=ground_connected,
                    output_node_correct=output_node_correct,
                    generator_correct=generator_correct,
                )
                show_diagnostic_results(diagnosis_results)

                st.caption(
                    "Diagnostic rankings are heuristic suggestions, "
                    "not confirmed probabilities."
                )

    else:
        st.markdown("### Oscilloscope data import")

        render_html("""
        <div class="panel">
            <div class="panel-title">Upload measurement file</div>
            <div class="panel-description">
                Upload a CSV exported from your oscilloscope.
                Required columns: time, input and output.
            </div>
        </div>
        """)

        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=["csv"],
        )

        if uploaded_file is not None:
            try:
                loaded = load_oscilloscope_csv(uploaded_file)
                data, sampling_rate, irregular = get_csv_components(loaded)
                analysis = analyze_csv(data)

                st.success("Measurement file loaded successfully.")

                if irregular:
                    st.warning(
                        "Sampling intervals are irregular. FFT results "
                        "based on the median sampling rate may be inaccurate."
                    )

                st.markdown("### Acquired waveform")
                st.plotly_chart(
                    oscilloscope_plot(
                        data["time"],
                        data["input"],
                        data["output"],
                        title="Hardware waveform · CH1 / CH2",
                    ),
                    use_container_width=True,
                )

                st.markdown("### Measurement summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Input peak", f"{analysis['input_peak']:.3f} V")
                c2.metric("Output peak", f"{analysis['output_peak']:.3f} V")
                c3.metric("Measured gain", f"{analysis['gain']:.3f}")

                if "gain_db" in analysis:
                    st.metric(
                        "Measured gain (dB)",
                        f"{analysis['gain_db']:.2f} dB",
                    )

                st.divider()
                st.markdown("### Frequency spectrum")

                f_in, fft_in = calculate_fft(data["input"], sampling_rate)
                f_out, fft_out = calculate_fft(data["output"], sampling_rate)

                st.plotly_chart(
                    fft_plot(f_in, fft_in, fft_out),
                    use_container_width=True,
                )

                st.caption(
                    "FFT resolution depends on recording duration "
                    "and sampling interval."
                )

            except Exception as error:
                st.error(f"Unable to analyse uploaded file: {error}")


# ============================================================
# APPLICATION ROUTER
# ============================================================

brand_header()

page = st.session_state.page

if page == "Home":
    home_page()
elif page == "Experiment Lab":
    experiment_lab()
elif page == "Virtual Instruments":
    virtual_instruments()
elif page == "Fault Diagnosis":
    fault_diagnosis()
elif page == "Hardware Analysis":
    hardware_analysis()
else:
    st.session_state.page = "Home"
    st.rerun()

footer()
