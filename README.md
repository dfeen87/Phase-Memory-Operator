# Deterministic Phase-Memory Operator for Hysteresis and Path-Dependent Regime Shifts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Authors**: Marcel Krüger<sup>1</sup>, Don Feeney<sup>2</sup>

<sup>1</sup>Independent Researcher, Meiningen, Germany  
<sup>2</sup>Independent Researcher, Pennsylvania, USA

---

## Overview

This repository implements a **deterministic phase-memory operator** for detecting regime shifts in systems exhibiting **hysteresis** and **path-dependent dynamics**. The method extracts a triadic latent state—phase deviation, drift, and accumulated memory—from observed signals and provides an interpretable stability functional for early warning of critical transitions.

### Key Features

- ✅ **Deterministic** - no black-box retraining; fully reproducible
- ✅ **Model-agnostic** - works without mechanistic system knowledge
- ✅ **Auditable** - complete parameter logging and replay capability
- ✅ **Supervisory** - designed as diagnostic layer, not controller
- ✅ **Multi-timescale** - captures fast deviations, medium drift, slow memory
- ✅ **Validated** - external validation on EEG ollapse-like regimes

---

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/phase-memory-operator.git
cd phase-memory-operator
pip install -r reproducibility/requirements.txt
```

### Basic Usage

```python
from src.phase_extraction import analytic_signal, construct_reference_phase
from src.triadic_operator import compute_triadic_state
from src.stability_functional import compute_stability_functional, StabilityParameters
from src.warning_logic import detect_warning_events, AlertParameters

# 1. Extract phase from signal
z, theta, amplitude = analytic_signal(signal)

# 2. Construct reference phase from baseline
theta_ref, ref_metadata = construct_reference_phase(
    baseline_signal, 
    dt=sampling_interval,
    method='mean_frequency'
)

# 3. Compute triadic state (U1, U2, U3)
state = compute_triadic_state(theta, theta_ref, time_vector)

# 4. Apply stability functional
params = StabilityParameters(a=0.4, b=0.3, c=0.3)
J = compute_stability_functional(state.U1, state.U2, state.U3, params)

# 5. Generate warnings
alert_params = AlertParameters(J_threshold=0.5, dwell_time=2.0)
warnings, events = detect_warning_events(J, time_vector, alert_params)
```

See `validation/eeg_replay.ipynb` for complete end-to-end example.

---

## Methodology

### Triadic Phase-Memory Channels

The operator extracts three interpretable channels from observed signals:

| Channel | Symbol | Meaning | Timescale |
|---------|--------|---------|-----------|
| **U₁** | Δθ(t) | Phase deviation vs. reference | Fast |
| **U₂** | ω(t) | Drift rate / timing slip | Medium |
| **U₃** | m(t) | Accumulated memory / hysteresis | Slow |

### Stability Functional

These channels feed into a stability index:

```
J(t) = a·U₁(t)² + b·U₂(t)² + c·U₃(t)²
```

When J(t) exceeds a threshold for a sustained dwell time, an early warning is issued.

### Design Philosophy

Unlike machine learning approaches:
- **No retraining** - parameters frozen after calibration
- **Deterministic** - exact reproducibility guaranteed
- **Transparent** - every decision is logged and auditable
- **Safety-critical ready** - suitable for human-in-the-loop systems

---

## Calibration Protocol

We enforce a strict **three-phase protocol** to ensure scientific rigor:

```
Calibration → Validation → Test (locked parameters)
```

Key principles:
- ✅ Contiguous temporal splits (no data leakage)
- ✅ Parameters frozen after calibration
- ✅ Test phase run exactly once
- ✅ Pre-declared metrics and falsification criteria
- ✅ Calibration performed on a single contiguous window per experiment

See [`calibration/calibration_protocol.md`](calibration/calibration_protocol.md) for detailed instructions.

---

## Validation

### External Validation: EEG Collapse Regimes

We validated the operator on the CHB-MIT scalp EEG database as a high-dimensional, nonstationary benchmark for collapse detection.

- **ROC-AUC**: 0.87 (test set, locked parameters)
- **Median lead time**: 15.3 seconds before event onset
- **False alarm rate**: 0.10 alarms/second

This validation is intended to assess the operator’s mathematical ability to detect impending regime shifts under drift and memory effects, not to claim biological or clinical
transferability beyond the benchmark.

**Reproducibility**: Full validation notebook available at [`validation/eeg_replay.ipynb`](validation/eeg_replay.ipynb)

**Important**: This validation serves as a "high-dimensional nonstationary dynamical regime-shift testbed." No biological mechanism is claimed to transfer to other domains—only the operator's mathematical ability to detect impending collapse under drift and memory effects.

---

## Applications

### Illustrative: Oxygen Delivery Monitoring

The paper presents a forward-looking application to human-in-the-loop oxygen delivery systems:

- **Input**: Commanded valve settings, flow rates
- **Output**: Measured oxygen partial pressure, flow telemetry
- **Challenge**: Human breathing + system dynamics create path-dependent timing relationships

The operator acts as a **supervisory diagnostic layer**, providing:
1. Continuous stability index J(t)
2. Early warning before hysteresis loops
3. Identification of safe operating windows
4. Reproducible diagnostics from telemetry alone

**Status**: Illustrative concept; no operational deployment claimed.

### Other Potential Applications

- Anesthesia delivery monitoring
- Pilot-aircraft coupling dynamics
- Industrial processes with thermal hysteresis
- Adaptive control systems with timing drift
- Power grid stability under path-dependent loads

---

## Repository Structure

```
phase-memory-operator/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation information
├── src/                               # Core implementation
│   ├── phase_extraction.py            # Hilbert transform, phase estimation
│   ├── triadic_operator.py            # U1, U2, U3 computation
│   ├── stability_functional.py        # J(t) and weight calibration
│   └── warning_logic.py               # Alert generation, dwell-time gating
├── calibration/
│   ├── calibration_protocol.md        # Detailed protocol instructions
│   └── locked_params_example.yaml     # Example frozen parameters
├── validation/
│   └── eeg_replay.ipynb               # External validation notebook
├── reproducibility/
│   ├── requirements.txt               # Python dependencies
│   └── replay_notes.md                # Deterministic replay instructions
└── paper/
    └── A Deterministic Phase–Memory   # Full paper
```

---

## Falsification Criteria

Following best practices in scientific transparency, we declare explicit conditions under which the method should be rejected:

The approach is **falsified** if, under locked parameters:

1. ❌ No lead-time improvement over simple baseline detectors
2. ❌ Performance unstable under mild perturbations (resampling/noise)
3. ❌ Parameters non-transferable across sessions within stated domain
4. ❌ False alarm rate makes method impractical (>50% time in alarm)

These criteria are evaluated on the **test set only** with **frozen parameters**.

---

## Limitations

The method has explicit scope boundaries:

- **Phase estimation quality** depends on quasi-oscillatory signal structure
- **Low SNR** degrades phase extraction reliability
- **Reference phase selection** requires domain expertise
- **Strong nonstationarity** may require careful reference adaptation
- **Provides diagnostics**, not mechanistic causation

See paper Section 9 for detailed discussion.

---

## Citation

If you use this work, please cite:

```bibtex
@article{kruger2026phase,
  title   = {A Deterministic Phase--Memory Operator for Hysteresis and Path-Dependent Regime Shifts: A Validation Protocol and Application Roadmap},
  author  = {Kr{\"u}ger, Marcel and Feeney, Don},
  journal = {Preprint},
  note    = {Zenodo / arXiv},
  year    = {2026}
}
```

---

## Contributing

We welcome contributions that:
- Improve code clarity and documentation
- Add validation examples for new domains
- Enhance reproducibility infrastructure
- Report issues or edge cases

Please open an issue or pull request.

---

## License

MIT License - see [`LICENSE`](LICENSE) file.

---

## Contact

- Marcel Krüger: marcelkrueger092@gmail.com (ORCID: 0009-0002-5709-9729)
- Don Feeney: dfeen87@gmail.com (ORCID: 0009-0003-1350-4160)

---

## Acknowledgments

External validation data: CHB-MIT Scalp EEG Database (Shoeb, 2009)

Related work: Deterministic trust middleware available at [AILEE-Trust-Layer](https://github.com/dfeen87/AILEE-Trust-Layer)

---

## References

1. Amodei et al., "Concrete Problems in AI Safety," arXiv:1606.06565 (2016)
2. Gabor, "Theory of Communication," J. IEE 93(26), 429-457 (1946)
3. Vakman, "On the Analytic Signal...," IEEE Trans. Signal Process. 44(4), 791-797 (1996)
4. Visintin, *Differential Models of Hysteresis*, Springer (1994)
5. Scheffer et al., "Early-warning signals for critical transitions," Nature 461, 53-59 (2009)
6. Shoeb, *Application of ML to Epileptic Seizure Detection*, PhD MIT (2009)
