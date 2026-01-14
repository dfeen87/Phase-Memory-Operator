# A Deterministic Phase–Memory Operator for Hysteresis and Path-Dependent Regime Shifts: A Validation Protocol and Application Roadmap

**Marcel Krüger¹ and Don Feeney²**

¹ Independent Researcher, Meiningen, Germany  
Email: marcelkrueger092@gmail.com  
ORCID: 0009-0002-5709-9729

² Independent Researcher, Pennsylvania, USA  
Email: dfeen87@gmail.com  
ORCID: 0009-0003-1350-4160

January 14, 2026

---

## Abstract

Hysteresis and path-dependent regime shifts occur across biological, engineering, and human-in-the-loop systems, where classical optimization and control strategies can fail under timing drift and geometric misalignment. We present a deterministic phase–memory operator that extracts a triadic latent state—phase deviation, drift, and accumulated memory—from observed signals and yields an interpretable stability functional for early warning of transition regimes. The proposed operator is model-agnostic, requires no retraining, and is designed to operate as a supervisory diagnostic layer rather than a controller. We outline a reproducible calibration and evaluation protocol and summarize an external validation on EEG time series demonstrating strong predictive performance for collapse-like dynamics under fixed-parameter replay. Finally, we provide an application roadmap for deploying the method to other hysteretic systems (including oxygen-delivery monitoring as a representative human-in-the-loop loop), emphasizing falsification criteria and limitations to ensure transparent scientific assessment.

---

## 1. Introduction

Hysteresis and path dependence are ubiquitous in complex systems, including physiological regulation, coupled human–machine loops, and engineering processes subject to drift and accumulated state history [4–6]. Classical learning-based methods can be effective, but they may lack deterministic replay, auditability, and stability guarantees in safety-critical contexts. This work proposes a deterministic, runtime-computable operator that acts as a diagnostic/supervisory layer for regime-shift detection, rather than a controller.

### Contributions

- A deterministic phase–memory operator producing a triadic latent state (U₁, U₂, U₃) from observed time series.
- A stability functional and thresholding logic for early warning under drift and hysteresis.
- A reviewer-auditable calibration/validation protocol emphasizing leakage control, frozen parameters after calibration, and falsification criteria.
- An external validation summary on EEG collapse-like regimes with full reproducibility via a public notebook and deterministic replay.
- An application roadmap for hysteretic human-in-the-loop systems, including an illustrative oxygen-delivery monitoring example.

---

## 2. Problem Setting: Hysteresis, Drift, and Path Dependence

Let x(t) be an observed signal (scalar or multichannel). Many systems exhibit: (i) phase-like structure, (ii) slow drift in effective timing or geometry, (iii) memory effects where identical instantaneous states map to different outcomes depending on history. We treat these as a triad of observables extracted from x(t) (or a derived feature s(t)).

**Signal-to-feature mapping.** A deterministic preprocessing map P yields s(t) = P[x(t)]; P is frozen after calibration and logged for replay.

---

## 3. Phase Extraction and Observables

We define an analytic signal via the Hilbert transform [2, 3]:

```
z(t) = s(t) + i H[s(t)], θ(t) = arg z(t)
```

where H[·] denotes the Hilbert transform and θ(t) is the instantaneous phase. A reference phase θ_ref(t) is defined either from a baseline segment, a nominal model, or an adaptive low-variance estimator (explicitly specified and frozen after calibration).

**Practical note.** If s(t) is not narrowband/oscillatory, phase estimation may be ill-posed; we treat this as an explicit limitation (Section 9).

---

## 4. Triadic Phase–Memory Operator

We define three channels:

```
U₁(t) := Δθ(t) = wrap(θ(t) − θ_ref(t))
U₂(t) := ω(t) = d/dt θ(t) − d/dt θ_ref(t)
U₃(t) := m(t) = ∫[t₀ to t] w(τ) U₁(τ) dτ
```

with a bounded wrapping operator wrap(·) and an optional weighting/gating function w(τ) (e.g., confidence, SNR, artifact mask). The role of U₃ is to encode accumulated deviation—a minimal memory sufficient to represent hysteretic separation between forward/backward trajectories.

### 4.1 Interpretation (reviewer-friendly)

- **U₁**: instantaneous misalignment (fast)
- **U₂**: drift rate / timing slip (medium)
- **U₃**: accumulated memory / hysteresis state (slow)

**Table 1: Triadic phase–memory channels (conceptual definition and timescale)**

| Channel | Symbol | Meaning | Typical timescale |
|---------|--------|---------|-------------------|
| U₁ | Δθ | phase deviation vs. reference | fast |
| U₂ | ω | drift rate / timing slip | medium |
| U₃ | m | accumulated memory / hysteresis | slow |

---

## 5. Stability Functional and Early-Warning Logic

We define an interpretable stability functional:

```
J(t) = a U₁(t)² + b U₂(t)² + c U₃(t)², a, b, c ≥ 0
```

with weights (a, b, c) determined by calibration (Section 6). A regime-shift warning is triggered when J(t) exceeds a threshold J_c for a sustained dwell time ΔT:

```
Warn(t) = 1 ⟺ J(τ) ≥ J_c ∀τ ∈ [t − ΔT, t]
```

**Scope note (important).** The operator does not generate control actions; it produces a deterministic diagnostic score intended to complement existing controllers or monitoring stacks.

---

## 6. Calibration and Validation Protocol

To ensure reviewer-auditable claims, we enforce:

- deterministic preprocessing and full replay (logged parameters, fixed seeds where applicable),
- parameter freezing after calibration (no dataset-specific retuning in test),
- strict temporal splits (leakage control),
- pre-declared metrics and falsification criteria [7, 8].

### 6.1 Data splits and leakage control

We recommend contiguous temporal splits:

- **Calibration window**: estimate θ_ref(t), weights (a, b, c), and choose (J_c, ΔT).
- **Validation window**: select among fixed candidate configurations (no peeking at test).
- **Test window**: locked parameters; report final metrics once.

All split indices are recorded to guarantee replay.

### 6.2 Metrics

We recommend: lead time, ROC-AUC, PR-AUC (class imbalance), false-alarm rate per unit time, and perturbation stability (resampling/noise) [9]. Where applicable, include calibration curves and event-based scoring rules.

**Table 2: Recommended evaluation metrics for regime-shift prediction**

| Metric | Definition / purpose |
|--------|---------------------|
| Lead time | Median time between first warning and event onset |
| ROC-AUC | Threshold-independent discrimination |
| PR-AUC | Robust under class imbalance |
| False alarm rate | Warnings per unit time in non-event windows |
| Stability | Sensitivity to resampling / noise injections |

**Table 3: Calibration settings and locked parameters for reviewer-auditable evaluation**

All items listed as "Locked" must remain unchanged during the test phase.

| Item | Specification (must be explicit) | Status | Where logged |
|------|----------------------------------|--------|--------------|
| Data split indices | Exact train/val/test (or calibration/val/test) boundaries; contiguous temporal splits; no peeking into test windows. | Locked | Split file / config |
| Signal preprocessing P | Filter type/order, band limits, resampling rate, normalization, artifact masks; deterministic pipeline definition. | Locked | Pipeline config + hash |
| Feature definition s(t) | Exact mapping s(t) = P[x(t)]; channel selection; aggregation rules for multichannel signals. | Locked | Config + code version |
| Phase estimator | Analytic signal definition; Hilbert transform method; phase unwrap/wrap convention; numerical differentiation method for θ̇(t). | Locked | Code + parameter dump |
| Reference phase θ_ref(t) | Baseline window selection rules or nominal reference construction; update policy (if any) must be pre-declared. | Locked | Reference spec + indices |
| Weighting/gating w(t) | Definition (e.g., SNR gate, artifact mask, confidence weighting); thresholds and hysteresis logic (if used). | Locked | Mask logs + config |
| Operator definitions | Eqs. for U₁, U₂, U₃ including wrap operator wrap(·) and integration limits (t₀); numeric integrator choice. | Locked | Operator spec + code hash |
| Stability weights (a, b, c) | Calibration procedure; objective used for choosing (a, b, c); resulting values frozen for test. | Locked | Calibration report |
| Alert parameters (J_c, ΔT) | Threshold J_c, dwell time ΔT, warning policy; any smoothing/hysteresis pre-declared. | Locked | Alert policy config |
| Baselines | Declared baseline detectors (e.g. amplitude threshold, AR drift, spectral features) and their locked params. | Locked | Baseline config |
| Metrics | Pre-declared metrics: lead time, ROC-AUC, PR-AUC, false alarms/hour, perturbation stability; scoring rules. | Locked | Evaluation script |
| Random seeds (if any) | Seeds for any stochastic components (bootstraps, perturbation tests); otherwise "N/A". | Locked | Seed log |
| Reproducibility artifacts | Repository commit, environment (Python version), dependency lockfile, deterministic replay logs. | Locked | Replay bundle |

---

## 7. External Validation Summary: EEG Collapse Regimes

We summarize an external validation on EEG time series (e.g., CHB–MIT scalp EEG database), where the operator yields strong predictive performance for seizure-like collapse regimes. Full reproducibility is provided via a transparent notebook and fixed-parameter replay.

**Resources.** Notebook / validation link: [https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb](https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb)

**Interpretation boundary.** This validation is used strictly as a high-dimensional nonstationary dynamical regime-shift testbed. No biological mechanism is transferred to engineering applications; only the operator's regime-shift sensitivity under drift and memory is relevant.

---

## 8. Application Roadmap

This section translates the method into a deployment plan (signal requirements, phase reference selection, safety constraints, logging) for hysteretic systems.

```
Input u(t)          O2 Loop         Output y(t)       Preprocessing      Phase
(Setpoint)      → (Hardware)    →  (Telemetry)   →   s(t) = P[y(t)] → θ(t), θ_ref(t)
                                                                              ↓
                                                                        Triadic Op.
                                                                       (U₁, U₂, U₃)
                                                                              ↓
                                                                       Stability J(t)
                                                                              ↓
                                                                         Dwell ΔT
                                                                              ↓
                                                                    ALARM + Audit Log
                                                                              
                                                          Supervisory Diagnostic
```

### 8.1 Roadmap steps

1. **Signal qualification**: ensure s(t) supports phase extraction; define artifact masks and w(t).
2. **Reference definition**: construct θ_ref(t) from stable segments or nominal operating envelopes.
3. **Calibration**: fit (a, b, c) and (J_c, ΔT) on calibration window only; freeze parameters.
4. **Shadow deployment**: compute J(t) in parallel to existing monitoring; log all decisions.
5. **A/B evaluation**: compare against baseline detectors (thresholds, AR models, spectral drift) under locked parameters.
6. **Operationalization**: define alert policies, escalation routes, and audit schema.

### 8.2 Illustrative human-in-the-loop oxygen-delivery monitoring (non-operational)

**Scope and interpretation.** The following oxygen-delivery example is illustrative and forward-looking. No claim of experimental validation or operational deployment in NASA or spaceflight systems is made. The purpose is to demonstrate how the proposed phase–memory operator can be applied as a supervisory diagnostic layer to systems exhibiting hysteresis and path-dependent timing effects.

**System abstraction.** Consider a loop characterized by commanded input u(t) (e.g., valve setting / flow command) and measured output y(t) (e.g., partial oxygen pressure, flow rate, or proxy variables). Human-in-the-loop operation and cyclic breathing patterns can induce path dependence and drift in the effective timing relationship between u(t) and y(t).

**Role of the operator.** The operator is employed strictly as a supervisory diagnostic: it does not replace controllers, modify actuation laws, or introduce new physical dynamics. It provides an early-warning stability index J(t) that detects phase drift and memory-driven divergence (hysteresis separation) before macroscopic failure modes occur.

**Operational outputs.** Application yields: (i) a continuous stability index J(t), (ii) identification of admissible operating windows, (iii) early-warning signals preceding hysteresis loops, and (iv) reproducible diagnostics based solely on measured time series.

**Table 4: Conventional diagnostics vs. phase–memory supervision (conceptual)**

| Aspect | Conventional diagnostics | Phase–memory supervision |
|--------|-------------------------|--------------------------|
| Hysteresis handling | limited | explicit (via U₃) |
| Drift sensitivity | high | reduced (via U₂) |
| Early warning | variable | explicit (J(t) with dwell) |
| Hardware changes | often required | none required |

```
Observed Signal     Analytic Signal      Triadic State      Stability Score    Warning + Audit
x(t) / s(t)     →   z(t) & Phase θ(t) → (U₁, U₂, U₃)   →   J(t)           →  (No control action)
                                                  ↑                              
                                    Frozen parameters after calibration
                                    Deterministic replay
                                    Artifact masks w(t)
                                    Dwell-time gating
                                    Stable alert policy
                                    
                         Deterministic Diagnostic Pipeline
```

---

## 9. Falsification Criteria and Limitations

### Falsification criteria

The approach is considered falsified (within the stated scope) if, under locked parameters:

- it yields no lead-time improvement over declared baselines across pre-registered test splits,
- performance is unstable under mild perturbations (resampling/noise) beyond stated tolerances,
- thresholds and weights are not transferable across sessions/subjects within the stated uncertainty envelope.

### Limitations

Phase estimation can fail under low SNR or in non-oscillatory regimes. Strong nonstationarity may require careful reference-phase selection; failure to specify θ_ref(t) is treated as a methodological error. The operator provides diagnostics, not mechanistic causation.

---

## 10. Conclusion

We presented a deterministic phase–memory operator for diagnosing hysteresis and path-dependent regime shifts. The method is designed for auditability, deterministic replay, and transparent falsification, and can complement existing controllers and monitoring systems.

---

## Appendix A: Implementation and Deterministic Replay

We recommend logging: (i) preprocessing map P and all filter parameters, (ii) reference selection procedure for θ_ref(t), (iii) (a, b, c), J_c, ΔT, (iv) split indices, and (v) artifact masks and gating w(t). Deterministic replay is achieved by freezing all above elements and replaying the same decision logic on the same inputs.

**Software availability (optional, separate from the operator).** A reference implementation of a deterministic trust middleware (MIT license) providing deterministic replay and audit logging is available at: [https://github.com/dfeen87/Phase-Memory-Operator](https://github.com/dfeen87/Phase-Memory-Operator). This software is independent and is cited here only as an example of auditable governance tooling. Unlike learning-based safety approaches that modify objectives or training procedures, the present work focuses on deterministic runtime governance and replay, complementing prior discussions of AI safety concerns [1].

---

## Appendix B: External Validation Appendix: EEG Collapse Regimes

This appendix summarizes an external validation of the proposed phase–memory operator on EEG time series exhibiting collapse-like dynamics. The purpose is not parameter optimization, but an out-of-sample robustness check using fixed operator settings and deterministic replay.

### B.1 Dataset and scope

The validation was performed on publicly available EEG recordings (e.g., CHB–MIT scalp EEG database) [10]. No dataset-specific tuning or retraining was performed after initial calibration.

### B.2 Methodology

The operator was applied as a supervisory diagnostic layer:

- phase extraction from EEG-derived signals,
- fixed triadic phase–memory computation (U₁, U₂, U₃) using Eqs. (2)–(4),
- stability functional evaluation via Eq. (5) with frozen parameters,
- event prediction via Eq. (6) (threshold crossing + minimum dwell time).

All preprocessing, thresholds, and evaluation steps were logged to enable deterministic replay and independent verification.

### B.3 Reproducibility resources

**Notebook:** [https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb](https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb)

---

## References

[1] D. Amodei, C. Olah, J. Steinhardt, P. Christiano, J. Schulman, and D. Mané, "Concrete Problems in AI Safety," arXiv:1606.06565 (2016).

[2] D. Gabor, "Theory of Communication," Journal of the Institution of Electrical Engineers – Part III: Radio and Communication Engineering 93(26), 429–457 (1946).

[3] D. E. Vakman, "On the Analytic Signal, the Teager–Kaiser Energy Algorithm, and Other Methods for Defining Amplitude and Frequency," IEEE Transactions on Signal Processing 44(4), 791–797 (1996).

[4] A. Visintin, Differential Models of Hysteresis. Springer, Berlin (1994).

[5] M. Brokate and J. Sprekels, Hysteresis and Phase Transitions. Springer, New York (1996).

[6] C. Kuehn, "A mathematical framework for critical transitions: bifurcations, fast–slow systems and stochastic dynamics," Physica D 240(12), 1020–1035 (2011).

[7] M. Scheffer, J. Basu, M. Brock, V. Brooks, S. Carpenter et al., "Early-warning signals for critical transitions," Nature 461, 53–59 (2009).

[8] V. Dakos, S. R. Carpenter, W. A. Brock, A. M. Ellison, V. Guttal et al., "Methods for Detecting Early Warnings of Critical Transitions in Time Series Illustrated Using Simulated Ecological Data," PLoS ONE 7(7), e41010 (2012).

[9] T. Saito and M. Rehmsmeier, "The Precision–Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets," PLoS ONE 10(3), e0118432 (2015).

[10] A. Shoeb, Application of Machine Learning to Epileptic Seizure Onset Detection and Treatment. PhD thesis, Massachusetts Institute of Technology (2009). (Associated with the CHB–MIT EEG database.)
