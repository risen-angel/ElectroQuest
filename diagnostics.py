
# ==========================================
# SIGNALAB FAULT DIAGNOSIS ENGINE
# ==========================================

def diagnose(
    expected_amplitude,
    observed_amplitude,
    expected_frequency,
    observed_frequency,
    expected_cutoff,
    observed_cutoff=None,
    ground_connected=True,
    output_node_correct=True,
    generator_correct=True,
    selected_fault="Unknown"
):

    candidates = []

    def add_candidate(name, score, explanation, checks):

        candidates.append({
            "fault": name,
            "score": score,
            "explanation": explanation,
            "checks": checks
        })

    expected_amplitude = max(
        expected_amplitude, 1e-9
    )

    expected_frequency = max(
        expected_frequency, 1e-9
    )

    amplitude_ratio = (
        observed_amplitude / expected_amplitude
    )

    frequency_error = (
        abs(observed_frequency - expected_frequency)
        / expected_frequency
    )

    # --------------------------------------
    # CONNECTION CHECKS
    # --------------------------------------

    if not ground_connected:

        add_candidate(
            "Missing ground connection",
            100,
            "The measurement does not have a verified common reference.",
            [
                "Check the function generator ground.",
                "Check the oscilloscope ground reference.",
                "Verify the circuit ground node."
            ]
        )

    if not output_node_correct:

        add_candidate(
            "Incorrect output measurement point",
            100,
            "The output is not being measured across the capacitor.",
            [
                "Locate the resistor-capacitor junction.",
                "Measure output across the capacitor.",
                "Verify the probe reference connection."
            ]
        )

    if not generator_correct:

        add_candidate(
            "Incorrect function generator settings",
            100,
            "The generator configuration has not been verified.",
            [
                "Check frequency.",
                "Check amplitude and peak/RMS convention.",
                "Verify DC offset.",
                "Check output termination settings."
            ]
        )

    # --------------------------------------
    # AMPLITUDE ANALYSIS
    # --------------------------------------

    if amplitude_ratio < 0.2:

        add_candidate(
            "Possible shorted capacitor",
            75,
            "The output is significantly lower than predicted. A shorted capacitor can pull the output towards ground.",
            [
                "Disconnect circuit power.",
                "Inspect capacitor connections.",
                "Check capacitor condition using an appropriate meter."
            ]
        )

        add_candidate(
            "Possible open series connection",
            70,
            "An interrupted signal path can cause the output to collapse.",
            [
                "Inspect resistor leads.",
                "Check resistor continuity with power disconnected.",
                "Verify breadboard connections."
            ]
        )

        add_candidate(
            "Incorrect component value",
            50,
            "An incorrect RC value can cause excessive attenuation at the test frequency.",
            [
                "Measure resistance.",
                "Verify capacitor marking.",
                "Recalculate the cutoff frequency."
            ]
        )

    elif amplitude_ratio > 1.3:

        add_candidate(
            "Incorrect output measurement point",
            75,
            "The measured output is higher than the predicted filtered output.",
            [
                "Check the oscilloscope probe location.",
                "Verify that output is measured across the capacitor.",
                "Inspect circuit topology."
            ]
        )

        add_candidate(
            "Incorrect component values",
            60,
            "The actual RC values may differ from the configured values.",
            [
                "Measure resistor value.",
                "Verify capacitor value.",
                "Recalculate cutoff frequency."
            ]
        )

    # --------------------------------------
    # FREQUENCY ANALYSIS
    # --------------------------------------

    if frequency_error > 0.05:

        add_candidate(
            "Incorrect frequency measurement or generator setting",
            85,
            "The observed output frequency differs from the expected input frequency.",
            [
                "Verify function generator frequency.",
                "Inspect oscilloscope time/div.",
                "Measure multiple waveform cycles."
            ]
        )

    # --------------------------------------
    # CUTOFF ANALYSIS
    # --------------------------------------

    if observed_cutoff is not None:

        if expected_cutoff > 0:

            cutoff_error = (
                abs(observed_cutoff - expected_cutoff)
                / expected_cutoff
            )

            if cutoff_error > 0.15:

                add_candidate(
                    "Incorrect RC component values",
                    90,
                    "Measured cutoff frequency differs from the theoretical RC cutoff.",
                    [
                        "Measure resistor resistance.",
                        "Check capacitor value and units.",
                        "Verify the measurement method.",
                        "Calculate fc = 1/(2*pi*R*C)."
                    ]
                )

    # --------------------------------------
    # SIMULATION FAULT IDENTIFICATION
    # --------------------------------------

    if selected_fault != "Unknown":

        add_candidate(
            selected_fault,
            100,
            "This fault was deliberately introduced in the simulation.",
            [
                "Compare healthy and faulty waveforms.",
                "Review the circuit configuration.",
                "Restore the original component or connection."
            ]
        )

    # --------------------------------------
    # RANKING
    # --------------------------------------

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    if not candidates:

        return [{
            "fault": "No significant fault detected",
            "score": 0,
            "confidence_score": 0,
            "explanation": (
                "The supplied measurements do not show "
                "a significant mismatch."
            ),
            "checks": [
                "Check the phase difference.",
                "Verify oscilloscope settings.",
                "Test another input frequency."
            ]
        }]

    total = sum(
        item["score"] for item in candidates
    )

    for item in candidates:

        item["confidence_score"] = round(
            item["score"] / total * 100,
            1
        )

    return candidates
