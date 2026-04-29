# A Deterministic Phase–Memory Operator for Hysteresis and Path-Dependent Regime Shifts: A Validation Protocol and Application Roadmap

*Archives of Advanced Engineering Science*
DOI: 10.47852/bonviewAAESXXXXXXXX

**Marcel Krüger¹\***, **Don Feeney²**

¹ Independent Researcher, Germany — marcelkrueger092@gmail.com — ORCID: 0009-0002-5709-9729

² Independent Researcher, Pennsylvania, USA — dfeen87@gmail.com — ORCID: 0009-0003-1350-4160

\* Corresponding author: Marcel Krüger, Independent Researcher, Germany. Email: marcelkrueger092@gmail.com

---

## Abstract

Hysteresis and path-dependent regime shifts occur across biological and engineering systems, including human-in-the-loop settings, where classical optimization and control strategies can fail under timing drift and geometric misalignment. We present a deterministic phase–memory operator that extracts a triadic latent state—phase deviation, drift, and accumulated memory—from observed signals and yields an interpretable stability functional for early warning of transition regimes. The proposed operator is model-agnostic, requires no retraining, and is designed to operate as a supervisory diagnostic layer rather than a controller. We outline a reproducible calibration and evaluation protocol and summarize an external validation on EEG time series demonstrating predictive performance for collapse-like dynamics under fixed-parameter replay. Finally, we provide an application roadmap for extending the method to other hysteretic systems, including oxygen-delivery monitoring as a representative human-in-the-loop example, emphasizing falsification criteria and limitations to ensure transparent scientific assessment.

**Keywords:** phase–memory operator; hysteresis; path dependence; early warning; deterministic replay; supervisory diagnostics

---

## 1 Introduction

Hysteresis and path-dependent regime shifts arise in a wide range of complex systems, including physiological regulation, coupled human–machine loops, and engineering processes affected by drift, delay, and accumulated state history [4–6]. In such settings, identical instantaneous measurements may correspond to different effective system states depending on the preceding trajectory, which limits the usefulness of purely memoryless thresholding or static classification rules.

Classical learning-based approaches can be effective for event detection and forecasting, but in safety-critical contexts they may be difficult to audit and replay exactly, and may remain sensitive to retraining or dataset-specific adaptation. Motivated by these constraints, the present work introduces a deterministic, runtime-evaluable phase–memory operator intended to function as a diagnostic/supervisory layer for regime-shift detection rather than as a control law. The aim is not to replace existing controllers or decision systems, but to provide an interpretable stability index that can be computed from observed signals under fixed and reviewable parameter settings.

**Contributions.** The main contributions of this work are as follows:

- A deterministic phase–memory operator that produces a triadic latent state (U₁, U₂, U₃) from observed time series.
- A stability functional and thresholding logic for early warning under drift, delay, and hysteretic separation.
- A reviewer-auditable calibration and validation protocol emphasizing temporal leakage control, frozen parameters after calibration, and explicit falsification criteria.
- An external validation summary on EEG collapse-like regimes, used here strictly as a high-dimensional nonstationary regime-shift testbed, together with full reproducibility via a public notebook and deterministic replay.
- An engineering application roadmap for hysteretic human-in-the-loop settings, including an illustrative oxygen-delivery monitoring example.

---

## 2 Problem Setting: Hysteresis, Drift, and Path Dependence

Let x(t) denote an observed signal, either scalar or multichannel. We consider systems in which measured dynamics may exhibit three practically relevant features:

1. phase-like structure or oscillatory organization,
2. slow drift in effective timing, geometry, or operating point,
3. memory effects such that similar instantaneous observations correspond to different outcomes depending on prior trajectory.

These three aspects motivate the introduction of a triadic observable representation extracted either directly from x(t) or from a derived feature signal s(t).

**Signal-to-feature mapping.** We define a deterministic preprocessing map 𝒫 such that

> s(t) = 𝒫[x(t)] &emsp; (1)

The map 𝒫 may include filtering, channel selection, normalization, artifact masking, or other explicitly declared preprocessing operations. For reproducibility, 𝒫 is fixed after calibration and logged for deterministic replay.

---

## 3 Phase Extraction and Observables

To extract a phase-like observable, we define an analytic signal using the Hilbert transform [2, 3]:

> z(t) = s(t) + i 𝓗[s(t)], &emsp; θ(t) = arg z(t) &emsp; (2)

where 𝓗[·] denotes the Hilbert transform and θ(t) is the instantaneous phase associated with the preprocessed signal s(t). A reference phase θ_ref(t) is then specified from one of the following sources: a baseline segment, a nominal reference model, or an adaptive low-variance estimator. The chosen construction must be declared explicitly and kept fixed after calibration.

**Practical note.** Phase extraction by Hilbert-based analytic continuation is most meaningful when s(t) has sufficiently oscillatory or narrowband structure. If this condition is not met, instantaneous phase may become ill-posed or strongly representation-dependent. In the present framework, such cases are treated not as hidden model failure but as an explicit admissibility limitation; see Section 10.

---

## 4 Triadic Phase–Memory Operator

We introduce a triadic observable representation intended to capture instantaneous misalignment, drift, and finite accumulated memory under path-dependent evolution. The three channels are defined as

> U₁(t) := Δθ(t) = wrap(θ(t) − θ_ref(t)) &emsp; (3)
>
> U₂(t) := Δω(t) = θ̇(t) − θ̇_ref(t) &emsp; (4)
>
> U₃(t) := m(t) = ∫_{t−Tₘ}^{t} w(τ) Δθ(τ) dτ, &emsp; Tₘ > 0 &emsp; (5)

where wrap(·) denotes a bounded phase-wrapping operator, θ̇(t) is the instantaneous phase velocity, w(τ) ∈ [0, 1] is an optional confidence or gating function (e.g. artifact mask or SNR-based weight), and Tₘ is a finite memory horizon fixed during calibration.

The interpretation is as follows. U₁ captures instantaneous phase mismatch relative to the chosen reference; U₂ captures timing drift or relative phase-velocity slip; and U₃ accumulates recent directional deviation over a finite horizon. The finite-memory construction avoids uncontrolled long-time accumulation and is sufficient to encode hysteretic separation between forward and backward trajectories within the stated scope.

**Discrete implementation.** For sampled signals tₙ = nΔt, a replay-compatible implementation is

> U₁[n] := wrap(θ[n] − θ_ref[n]) &emsp; (6)
>
> U₂[n] := (θ[n] − θ[n−1]) / Δt − (θ_ref[n] − θ_ref[n−1]) / Δt &emsp; (7)
>
> U₃[n] := Δt · Σ_{k=n−Mₘ+1}^{n} w[k] U₁[k] &emsp; (8)

where Mₘ = ⌊Tₘ/Δt⌋ is the locked memory-window length. In practice, additional smoothing of U₂ may be used, provided that the filter and its parameters are declared and frozen after calibration.

### 4.1 Interpretation

- **U₁:** instantaneous phase misalignment (fast channel)
- **U₂:** relative drift rate / timing slip (intermediate channel)
- **U₃:** finite accumulated memory / hysteresis state (slow channel)

**Table 1: Triadic phase–memory channels and their conceptual roles.**

| Channel | Symbol | Meaning | Typical timescale |
|---------|--------|---------|-------------------|
| U₁ | Δθ | phase deviation vs. reference | fast |
| U₂ | Δω | relative phase-velocity mismatch / drift | intermediate |
| U₃ | m | finite accumulated deviation / hysteresis memory | slow |

---

## 5 Stability Functional and Early-Warning Logic

To combine the three channels into a single interpretable diagnostic score, we define the stability functional

> J(t) = a (U₁(t) / σ_θ)² + b (U₂(t) / σ_ω)² + c (U₃(t) / σ_m)², &emsp; a, b, c ≥ 0 &emsp; (9)

where σ_θ, σ_ω, and σ_m are fixed scale parameters estimated on the calibration window, and (a, b, c) are nonnegative weights chosen during calibration and then frozen for validation and test.

This normalization makes the three channels commensurable and reduces sensitivity to arbitrary differences in scale or physical units across the phase, drift, and memory components.

A regime-shift warning is issued when the score remains above a critical level J_c for a sustained dwell interval ΔT:

> Warn(t) = 1 ⟺ J(τ) ≥ J_c ∀ τ ∈ [t − ΔT, t] &emsp; (10)

**Discrete warning logic.** In sampled form, with M_d = ⌊ΔT/Δt⌋, the warning rule becomes

> Warn[n] = 1 ⟺ J[k] ≥ J_c ∀ k ∈ {n − M_d + 1, …, n} &emsp; (11)

This formulation is deterministic, replayable, and compatible with locked-parameter evaluation.

**Scope note.** The operator does not generate control actions and does not replace an existing controller. It produces a deterministic supervisory diagnostic score intended to complement existing monitoring or control stacks.

---

## 6 Calibration and Validation Protocol

To support reviewer-auditable claims, the following protocol is enforced:

- deterministic preprocessing and full replay (logged parameters, fixed seeds where applicable),
- parameter freezing after calibration (no retuning on validation or test windows),
- strict temporal splits to prevent information leakage,
- pre-declared metrics and explicit falsification criteria [7, 8].

### 6.1 Data Splits and Leakage Control

We recommend contiguous temporal splits:

- **Calibration window:** estimate θ_ref(t), scale parameters (σ_θ, σ_ω, σ_m), weights (a, b, c), and choose (J_c, ΔT, Tₘ).
- **Validation window:** select among fixed candidate configurations without inspecting the test window.
- **Test window:** evaluate once using locked parameters and report final metrics.

All split indices, filter settings, differentiation rules, and masking/gating definitions are recorded to guarantee deterministic replay.

### 6.2 Metrics

Recommended evaluation metrics include lead time, ROC-AUC, PR-AUC (for class imbalance), false-alarm rate per unit time, and perturbation stability under resampling or noise injections [9]. Where applicable, calibration curves and event-based scoring rules should also be reported.

**Table 2: Recommended evaluation metrics for regime-shift prediction.**

| Metric | Definition / purpose |
|--------|----------------------|
| Lead time | Median time between first warning and event onset |
| ROC-AUC | Threshold-independent discrimination performance |
| PR-AUC | Performance under class imbalance |
| False alarm rate | Warning frequency per unit time in non-event windows |
| Stability | Sensitivity to resampling, masking, or additive noise perturbations |

**Table 3: Calibration settings and locked parameters for reviewer-auditable evaluation.**

| Item | Specification (must be explicit) | Status | Where logged |
|------|----------------------------------|--------|--------------|
| Data split indices | Exact calibration/validation/test boundaries; contiguous temporal splits; no peeking into test windows. | Locked | Split file / config |
| Signal preprocessing 𝒫 | Filter type/order, band limits, resampling rate, normalization, artifact masks; deterministic pipeline definition. | Locked | Pipeline config + hash |
| Feature definition s(t) | Exact mapping s(t) = 𝒫[x(t)]; channel selection; aggregation rules for multichannel signals. | Locked | Config + code version |
| Phase estimator | Analytic signal definition; Hilbert transform method; phase unwrap/wrap convention; numerical differentiation rule for θ̇(t). | Locked | Code + parameter dump |
| Reference phase θ_ref(t) | Baseline window selection rules or nominal reference construction; update policy (if any) must be pre-declared. | Locked | Reference spec + indices |
| Weighting/gating w(t) | Definition (e.g., SNR gate, artifact mask, confidence weighting); thresholds and masking logic (if used). | Locked | Mask logs + config |
| Operator definitions | Eqs. for U₁, U₂, U₃ including the wrap operator wrap(·), finite memory horizon Tₘ, and any discrete implementation choices. | Locked | Operator spec + code hash |
| Scale parameters (σ_θ, σ_ω, σ_m) | Calibration procedure and resulting normalization scales used in Eq. (9). | Locked | Calibration report |
| Stability weights (a, b, c) | Calibration procedure; objective used for choosing (a, b, c); resulting values frozen for test. | Locked | Calibration report |
| Alert parameters (J_c, ΔT) | Threshold J_c, dwell time ΔT, warning policy; any smoothing or hysteresis in alert logic pre-declared. | Locked | Alert policy config |
| Baselines | Declared baseline detectors (e.g. amplitude threshold, AR drift, spectral features) and their locked parameters. | Locked | Baseline config |
| Metrics | Pre-declared metrics: lead time, ROC-AUC, PR-AUC, false alarms/hour, perturbation stability; scoring rules. | Locked | Evaluation script |
| Random seeds (if any) | Seeds for any stochastic components (bootstraps, perturbation tests); otherwise "N/A". | Locked | Seed log |
| Reproducibility artifacts | Repository commit, execution environment, dependency lockfile, deterministic replay logs. | Locked | Replay bundle |

### 6.3 Locked-Parameter Specification

For transparent review, the following quantities must be declared and frozen after calibration:

- preprocessing map 𝒫,
- phase-reference construction θ_ref(t),
- differentiation rule for θ̇(t),
- memory horizon Tₘ,
- gating function w(t),
- scale parameters (σ_θ, σ_ω, σ_m),
- weights (a, b, c),
- threshold J_c and dwell time ΔT.

**Table 4: Locked parameters and replay requirements for deterministic evaluation.**

| Item | Requirement | Status |
|------|-------------|--------|
| Preprocessing 𝒫 | filter, normalization, masking, feature mapping explicitly declared | locked |
| Reference phase θ_ref | baseline/model/adaptive rule explicitly specified | locked |
| Drift estimator | numerical differentiation and any smoothing rule declared | locked |
| Memory horizon Tₘ | finite integration window fixed after calibration | locked |
| Gating w(t) | confidence/SNR/artifact weighting rule declared | locked |
| Scales (σ_θ, σ_ω, σ_m) | estimated only on calibration split | locked |
| Weights (a, b, c) | fitted or selected on calibration/validation only | locked |
| Thresholding (J_c, ΔT) | alert policy pre-declared before final test | locked |

---

## 7 Simulation Benchmark for a Delayed Bistable System

To complement the external EEG regime-shift testbed with an explicitly controlled engineering-style benchmark, we evaluate the phase–memory operator on a delayed bistable system with slow parameter drift. The purpose of this section is not to claim a complete physical model of a specific device, but to test whether the operator detects path-dependent regime separation under controlled hysteresis, noise, and delay.

### 7.1 Benchmark Model

We consider the scalar delayed stochastic dynamics

> ẏ(t) = −∂V(y; λ(t))/∂y − κ(y(t) − y(t − τ_d)) + σ ξ(t) &emsp; (12)

where

> V(y; λ) = ¼ y⁴ − ½ λ y² &emsp; (13)

is a quartic double-well potential, λ(t) is a slowly drifting control parameter, τ_d > 0 is a fixed delay, κ ≥ 0 is the delay-coupling strength, σ is the noise amplitude, and ξ(t) denotes a zero-mean unit white-noise process in the numerical discretization sense.

For λ > 0, the potential admits two metastable wells, and slow drift in λ(t) combined with delay and noise generates branch-dependent transitions and hysteretic switching. This makes the model suitable as a controlled benchmark for testing the operator under path dependence.

### 7.2 Observed Signal and Feature Construction

The observed signal is taken as

> x(t) = y(t) + η(t) &emsp; (14)

where η(t) is optional additive measurement noise. The preprocessing map 𝒫 yields a scalar feature signal

> s(t) = 𝒫[x(t)] &emsp; (15)

for example after detrending, band-limiting, and normalization. The exact preprocessing pipeline must be fixed and logged as described in Section 6.

### 7.3 Simulation Protocol

A representative benchmark protocol consists of:

1. selecting a calibration window in which the system remains in a nominal regime,
2. estimating θ_ref(t), (σ_θ, σ_ω, σ_m), (a, b, c), Tₘ, J_c, and ΔT from calibration/validation only,
3. applying the locked operator to test trajectories with slow drift and delayed switching,
4. comparing against declared baselines under identical splits and replay settings.

The numerical integrator, time step, random seed handling, drift schedule λ(t), delay τ_d, and perturbation amplitudes must all be explicitly reported.

### 7.4 Baseline Comparators

To evaluate whether the phase–memory construction adds value beyond memoryless diagnostics, the following baselines should be reported where applicable:

- amplitude-threshold detector on x(t) or s(t),
- drift-only detector using U₂ or a smoothed derivative proxy,
- spectral or variance-based instability detector,
- ablated operator variants using only (U₁, U₂) without the memory channel U₃.

### 7.5 Primary Benchmark Outputs

The main outputs to report are:

- lead time before branch transition or escape event,
- false-alarm rate in non-transition windows,
- ROC-AUC and PR-AUC when event labels are defined,
- perturbation stability under resampling and additive noise,
- sensitivity of results to delay τ_d, drift rate, and memory horizon Tₘ.

### 7.6 Simulation Results

In an illustrative delayed-bistable benchmark under fixed benchmark-specific parametrization, the simulated system underwent a regime transition at

> t_trans = 64.20 s

The full phase–memory operator produced a sustained pre-transition increase in the stability score J(t), whereas an ablated no-memory variant based on (U₁, U₂) alone showed a weaker and less persistent pre-transition response.

For the benchmark configuration reported here, the full operator achieved a ROC-AUC of

> ROC-AUC = 0.862

with respect to the pre-transition warning labels defined on the benchmark trajectory. The highlighted warning interval is used only to visualize early-warning behavior in this controlled synthetic setting.

These results should be interpreted as an illustrative controlled demonstration of regime-shift sensitivity in a delayed hysteretic system, not as a full robustness sweep or deployment validation. In particular, the benchmark parameters, including the drift schedule, memory weighting, and warning-window construction, were fixed for this synthetic test scenario and should not be interpreted as universal operating values.

**Table 5: Representative delayed bistable benchmark parameters to be reported explicitly.**

| Parameter | Meaning | Example role |
|-----------|---------|--------------|
| τ_d | fixed delay | path dependence / lag |
| κ | delay-coupling strength | history sensitivity |
| σ | process-noise amplitude | stochastic perturbation level |
| λ(t) | slow drift schedule | regime destabilization |
| Δt | integration step | numerical replay resolution |
| Tₘ | operator memory horizon | finite hysteresis encoding |

**Table 6: Quantitative benchmark comparison for the delayed bistable simulation.**

| Method | Lead time | False alarms | ROC-AUC | Stability |
|--------|-----------|--------------|---------|-----------|
| Amplitude threshold | [insert] | [insert] | [insert] | [insert] |
| Drift-only baseline | [insert] | [insert] | [insert] | [insert] |
| U₁ + U₂ only | [insert] | [insert] | [insert] | [insert] |
| Phase–memory operator (U₁, U₂, U₃) | [insert] | [insert] | [insert] | [insert] |

### 7.7 Interpretation Boundary

This benchmark is intended as a controlled engineering-style test of path dependence, delay sensitivity, and finite-memory supervision. It does not by itself validate a specific biomedical or aerospace deployment. Its role is to provide an intermediate methodological bridge between the abstract operator definition and the external testbed/application sections that follow.

---

## 8 External Validation Summary: EEG Collapse Regimes

We summarize a published external validation of the phase–memory operator on EEG time series exhibiting collapse-like dynamics, reported in [12]. In that study, the operator was evaluated on nonstationary neural recordings as a regime-shift detection framework under fixed-parameter replay and transparent preprocessing. Within the scope relevant here, the EEG setting serves as an external high-dimensional testbed for assessing sensitivity to drift, phase deviation, and accumulated memory effects.

**Published validation source.** The external validation study is: Krüger, M., Feeney, D., and Wende, M. T. (2026), *Information-Theoretic Modeling of Neural Coherence via Triadic Spiral-Time Dynamics: A Framework for Neurodynamic Collapse*, Medinformatics. DOI: https://doi.org/10.47852/bonviewMEDIN62029043.

**Reproducibility resources.** Notebook / validation resource: https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb.

**Interpretation boundary.** This validation is used strictly as a high-dimensional nonstationary dynamical regime-shift testbed. No biological mechanism is transferred to the engineering applications considered in the present manuscript. Only the operator's sensitivity to regime change under drift, phase misalignment, and finite-memory effects is carried over at the methodological level.

---

## 9 Application Roadmap

This section translates the method into a deployment plan, including signal requirements, phase-reference selection, safety constraints, and logging, for hysteretic systems.

```
Input u(t)          O2 Loop          Output y(t)
(Setpoint)    →   (Hardware)    →    (Telemetry)
                                          ↓
                                   Preprocessing
                                   s(t) = P[y(t)]
                                          ↓
                                       Phase
                                  θ(t), θ_ref(t)
                                          ↓
                                    Triadic Op.
                                   (U1, U2, U3)
                                          ↓
                                   Stability J(t)
                                    Dwell ΔT
                                          ↓
                               ALARM    Audit Log
                          [Supervisory Diagnostic]
```

*Figure 2: Conceptual supervisory architecture for a human-in-the-loop oxygen-delivery setting. The physical loop maps commanded input u(t) to measured output y(t), while the proposed phase–memory operator acts only as an external diagnostic layer. No control action is generated by the operator; the output is an alarm and audit trail based on the stability score J(t).*

### 9.1 Roadmap Steps

1. **Signal qualification:** ensure s(t) supports phase extraction; define artifact masks and w(t).
2. **Reference definition:** construct θ_ref(t) from stable segments or nominal operating envelopes.
3. **Calibration:** fit (a, b, c) and (J_c, ΔT) on calibration window only; freeze parameters.
4. **Shadow deployment:** compute J(t) in parallel to existing monitoring; log all decisions.
5. **A/B evaluation:** compare against baseline detectors (thresholds, AR models, spectral drift) under locked parameters.
6. **Operationalization:** define alert policies, escalation routes, and audit schema.

### 9.2 Illustrative Human-in-the-Loop Oxygen-Delivery Monitoring (Non-Operational)

**Scope and interpretation.** The following oxygen-delivery example is illustrative and forward-looking. No claim of experimental validation or operational deployment in NASA or spaceflight systems is made. The purpose is to demonstrate how the proposed phase–memory operator can be applied as a supervisory diagnostic layer to systems exhibiting hysteresis and path-dependent timing effects.

**System abstraction.** Consider a loop characterized by commanded input u(t) (e.g., valve setting or flow command) and measured output y(t) (e.g., partial oxygen pressure, flow rate, or proxy variables). Human-in-the-loop operation and cyclic breathing patterns can induce path dependence and drift in the effective timing relationship between u(t) and y(t).

**Role of the operator.** The operator is employed strictly as a supervisory diagnostic: it does not replace controllers, modify actuation laws, or introduce new physical dynamics. It provides an early-warning stability index J(t) that detects phase drift and memory-driven divergence before macroscopic failure modes occur.

**Operational outputs.** Application yields: (i) a continuous stability index J(t), (ii) identification of admissible operating windows, (iii) early-warning signals preceding hysteresis loops, and (iv) reproducible diagnostics based solely on measured time series.

**Table 7: Conventional diagnostics vs. phase–memory supervision (conceptual comparison).**

| Aspect | Conventional diagnostics | Phase–memory supervision |
|--------|--------------------------|--------------------------|
| Hysteresis handling | limited | explicit (via U₃) |
| Drift sensitivity | high | reduced (via U₂) |
| Early warning | variable | explicit (J(t) with dwell) |
| Hardware changes | often required | none required |

### 9.3 Illustrative Extension to Large Life-Support Environments (Conceptual)

The proposed phase–memory operator is not restricted to small closed-loop subsystems. In principle, it may also be considered for larger hybrid environments in which multiple subsystems interact with different response times, delays, and history-dependent effects. Examples include modular life-support architectures combining physical–chemical processes with slower biological or human-in-the-loop components.

Such environments may exhibit hysteresis, timing drift, and delayed cross-coupling that are not always well summarized by memoryless thresholding alone. Within the present framework, this motivates considering the phase–memory operator as an additional supervisory diagnostic layer rather than as a replacement for existing control architectures.

**Table 8: Conceptual comparison between conventional control diagnostics and phase–memory supervision in delayed hybrid environments.**

| Aspect | Conventional monitoring / control view | Phase–memory supervisory view |
|--------|----------------------------------------|-------------------------------|
| Primary focus | Instantaneous error or threshold crossing | Phase deviation, drift, and finite-memory effects |
| Handling of hysteresis | Often indirect or model-specific | Represented explicitly through the memory channel U₃ |
| Delay sensitivity | Can require dedicated compensation design | Diagnosed through relative drift and dwell-based warning logic |
| Global coupling | Often treated locally or hierarchically | Can be summarized through an aggregated supervisory score |
| Operational role | Control and regulation | Diagnostic supervision only |
| Hardware modification required | Application-dependent | Not required in principle for the diagnostic layer |

**Hybrid system coordination.** Large life-support environments may combine fast mechanical processes (e.g. pumps, valves, scrubbers) with slower subsystems exhibiting delayed or history-dependent behavior. In such settings, the operator may provide a compact supervisory description of temporal misalignment and drift across subsystems, without altering their underlying physical models.

**Energy and operational interpretation.** The present work does not establish improved energy efficiency or superior closed-loop control performance for such environments. Rather, the potential role of the operator is limited to early warning and supervisory monitoring under delayed, path-dependent dynamics. Any claim of operational benefit would require explicit benchmark or deployment-specific validation.

**Global stability monitoring.** For modular systems with significant propagation delays, one may define an aggregated stability score J(t) from phase, drift, and finite-memory observables. In that interpretation, an increase in J(t) indicates departure from a previously calibrated operating regime, even if individual local signals remain within nominal bounds.

**Autonomy and long-duration operation.** In settings with limited intervention or delayed recalibration, the operator may serve as a deterministic monitoring layer for detecting slow drift in timing relationships or regime structure. This should be understood as a diagnostic aid only. No claim is made here that the framework by itself provides validated autonomous compensation or control.

---

## 10 Falsification Criteria and Limitations

### 10.1 Falsification Criteria

Within the stated scope, the proposed approach is considered falsified if, under locked parameters and pre-declared evaluation rules, one or more of the following conditions hold:

- it yields no reproducible lead-time improvement over declared baselines across pre-registered test splits,
- its performance degrades materially under mild perturbations (e.g. resampling, additive noise, or moderate masking changes) beyond the stated tolerance envelope,
- the warning logic defined by (J_c, ΔT) fails to remain stable under deterministic replay,
- the calibrated thresholds, scales, or weights fail to transfer across sessions or subjects within the uncertainty envelope claimed for the application setting.

These falsification conditions are intentionally operational: they are designed to test whether the method adds predictive or supervisory value beyond simpler baselines while remaining reproducible under controlled evaluation.

### 10.2 Limitations

Several limitations must be stated explicitly.

First, phase estimation may fail under low signal-to-noise ratio or in non-oscillatory regimes. In such cases, the analytic-signal representation may become ill-posed or strongly representation-dependent, and the resulting operator output should not be interpreted as reliable.

Second, strong nonstationarity may require careful construction of the reference phase θ_ref(t). Failure to specify the reference-phase definition, update rule, or calibration window explicitly is treated here as a methodological error rather than a hidden model degree of freedom.

Third, the proposed framework provides a deterministic diagnostic and supervisory score only. It does not establish mechanistic causation, does not identify underlying physical or biological generators uniquely, and does not by itself constitute a control law.

Finally, the external EEG validation and the illustrative oxygen-delivery roadmap serve different purposes. The EEG study is used only as a nonstationary regime-shift testbed, whereas the engineering roadmap is conceptual unless supported by an explicit benchmark or deployment-specific validation.

---

## 11 Conclusion

We presented a deterministic phase–memory operator for diagnosing hysteresis and path-dependent regime shifts in delayed and history-dependent systems. The framework is designed as a supervisory diagnostic layer rather than a control law, with emphasis on deterministic replay, auditability, locked-parameter evaluation, and explicit falsification criteria.

The central methodological contribution is the construction of a triadic observable state (U₁, U₂, U₃) that separates instantaneous phase deviation, relative drift, and finite accumulated memory. From this state, an interpretable stability score J(t) is formed and used for dwell-based early-warning logic under fixed and reviewable calibration rules.

To avoid overclaiming, the present work distinguishes clearly between three layers of evidence: a formal operator definition, a controlled simulation benchmark for path-dependent dynamics, and an external EEG-based regime-shift validation used only as a nonstationary testbed. The engineering application roadmap is therefore intended as a transparent extension path, not as a claim of completed deployment validation.

Within this scope, the proposed method contributes a deterministic and reviewer-auditable alternative to purely memoryless or retraining-dependent approaches for regime-shift supervision in complex systems.

---

## Appendix A: Implementation and Deterministic Replay

We recommend logging: (i) the preprocessing map 𝒫 and all associated filter parameters, (ii) the reference-phase construction θ_ref(t), (iii) the normalization scales (σ_θ, σ_ω, σ_m), (iv) the stability weights (a, b, c), (v) the alert parameters (J_c, ΔT, Tₘ), (vi) all split indices, and (vii) artifact masks and gating definitions w(t). Deterministic replay is achieved by freezing all of the above elements and reapplying the same decision logic to the same inputs.

**Software availability (operator reference implementation).** A reference implementation of the deterministic phase–memory operator (MIT license), including deterministic replay, parameter freezing, and audit logging for reviewer verification, is available at: https://github.com/dfeen87/Phase-Memory-Operator. The repository provides reproducibility artifacts including locked-parameter examples, replay notes, and validation notebooks to support independent verification of the reported diagnostic logic. Unlike learning-based safety approaches that modify objectives or training procedures, the present work emphasizes deterministic runtime supervision and exact replay [1].

---

## Appendix B: External Validation Appendix: EEG Collapse Regimes

This appendix summarizes an external validation of the proposed phase–memory operator on EEG time series exhibiting collapse-like dynamics. The purpose is not parameter optimization, but an out-of-sample robustness check using fixed operator settings and deterministic replay.

### B.1 Dataset and Scope

The validation was performed on publicly available EEG recordings, including CHB–MIT scalp EEG data [10]. No dataset-specific retuning or retraining was performed after initial calibration.

### B.2 Methodology

The operator was applied as a supervisory diagnostic layer using:

- phase extraction from EEG-derived signals,
- fixed triadic phase–memory computation (U₁, U₂, U₃) using Eqs. (3)–(5),
- stability-functional evaluation via Eq. (9) with frozen parameters,
- event prediction via Eqs. (10) and (11), depending on the implementation setting.

All preprocessing, thresholding, and evaluation steps were logged to enable deterministic replay and independent verification.

### B.3 Reproducibility Resources

Notebook: https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb

---

## Author Contributions

**Marcel Krüger** conceived the original phase–memory / spiral-time operator, developed its mathematical formalism, defined the supervisory diagnostic interpretation, designed the overall study concept, and wrote the manuscript.

**Don Feeney** contributed to implementation strategy, core software integration, repository structure, reproducibility architecture, figure and table preparation, and critical manuscript revision.

Both authors reviewed the final manuscript and approved the submitted version.

---

## Acknowledgement

The authors thank the maintainers of the public datasets and open-source tools used in the reproducibility workflow.

## Funding Support

No external funding was received for this work.

## Ethical Statement

This study did not involve new human or animal experiments performed by the authors. Publicly available de-identified data and deterministic simulation protocols were used where applicable.

## Conflicts of Interest

The authors declare no conflicts of interest.

## Data Availability Statement

The reference implementation, replay materials, and reproducibility resources for the phase–memory operator are publicly available at: https://github.com/dfeen87/Phase-Memory-Operator.

External EEG validation resources are available at: https://github.com/nwycomp/NeuroDynamics-Collapse-Validation-/blob/main/eeg-part-four.ipynb.

---

## References

[1] D. Amodei, C. Olah, J. Steinhardt, P. Christiano, J. Schulman, and D. Mané, "Concrete Problems in AI Safety," arXiv:1606.06565 (2016).

[2] D. Gabor, "Theory of Communication," *Journal of the Institution of Electrical Engineers – Part III: Radio and Communication Engineering* 93(26), 429–457 (1946).

[3] D. E. Vakman, "On the Analytic Signal, the Teager–Kaiser Energy Algorithm, and Other Methods for Defining Amplitude and Frequency," *IEEE Transactions on Signal Processing* 44(4), 791–797 (1996).

[4] A. Visintin, *Differential Models of Hysteresis*. Springer, Berlin (1994).

[5] M. Brokate and J. Sprekels, *Hysteresis and Phase Transitions*. Springer, New York (1996).

[6] C. Kuehn, "A mathematical framework for critical transitions: bifurcations, fast–slow systems and stochastic dynamics," *Physica D* 240(12), 1020–1035 (2011).

[7] M. Scheffer, J. Basu, M. Brock, V. Brooks, S. Carpenter et al., "Early-warning signals for critical transitions," *Nature* 461, 53–59 (2009).

[8] V. Dakos, S. R. Carpenter, W. A. Brock, A. M. Ellison, V. Guttal et al., "Methods for Detecting Early Warnings of Critical Transitions in Time Series Illustrated Using Simulated Ecological Data," *PLoS ONE* 7(7), e41010 (2012).

[9] T. Saito and M. Rehmsmeier, "The Precision–Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets," *PLoS ONE* 10(3), e0118432 (2015).

[10] A. Shoeb, *Application of Machine Learning to Epileptic Seizure Onset Detection and Treatment*. PhD thesis, Massachusetts Institute of Technology (2009). (Associated with the CHB–MIT EEG database.)

[11] M. Krüger, *Octonionic Structure of Triadic Spiral Time in the Helix–Light–Vortex (HLV) Framework*, Zenodo (2025), doi:10.5281/zenodo.17683977.

[12] M. Krüger, D. Feeney, and M. T. Wende, "Information-Theoretic Modeling of Neural Coherence via Triadic Spiral-Time Dynamics: A Framework for Neurodynamic Collapse," *Medinformatics*, 2026. doi: https://doi.org/10.47852/bonviewMEDIN62029043.

[13] Choi, J., & Kim, P. (2022). Early warning for critical transitions using machine-based predictability. *AIMS Mathematics*, 7(11), 20313–20327.

[14] Tirabassi, G., & Masoller, C. (2022). Correlation lags give early warning signals of approaching bifurcations. *Chaos, Solitons & Fractals*, 155, 111720.

[15] Wagener, F. O. O., & de Zeeuw, A. (2021). Stable partial cooperation in managing systems with tipping points. *Journal of Environmental Economics and Management*, 109, 102499.

[16] Bury, T. M., Bauch, C. T., & Anand, M. (2021). Deep learning for early warning signals of tipping points. *Proceedings of the National Academy of Sciences*, 118(39), e2106140118.

[17] Banerjee, A., Pavithran, I., & Sujith, R. I. (2024). Early warnings of tipping in a nonautonomous turbulent reactive flow system: Efficacy, reliability, and warning times. *Chaos*, 34(1), 013113.

[18] Homayounfar, M., & Muneepeerakul, R. (2021). On coupled dynamics and regime shifts in coupled human–water systems. *Hydrological Sciences Journal*, 66(5), 769–776.

[19] Dylewsky, D., Lenton, T. M., Scheffer, M., Bury, T. M., Fletcher, C. G., Anand, M., & Bauch, C. T. (2023). Universal early warning signals of phase transitions in climate systems. *Journal of the Royal Society Interface*, 20(201), 20220562.

[20] Kim, E.-J., & Hollerbach, R. (2022). Non-equilibrium statistical properties, path-dependent information geometry, and entropy relations in edge-localized modes in fusion plasmas. *Physics of Plasmas*, 29(11), 112302.

[21] MacLaren, N. G., Kundu, P., & Masuda, N. (2023). Early warnings for multi-stage transitions in dynamics on networks. *Journal of the Royal Society Interface*, 20(200), 20220743.

[22] Dakos, V., Boulton, C. A., Buxton, J. E., Abrams, J. F., Arellano-Nava, B., Armstrong McKay, D. I., Bathiany, S., Blaschke, L., Boers, N., Dylewsky, D., López-Martínez, C., Parry, I., Ritchie, P., van der Bolt, B., van der Laan, L., Weinans, E., & Kéfi, S. (2024). Tipping point detection and early warnings in climate, ecological, and human systems. *Earth System Dynamics*, 15, 1117–1135.
