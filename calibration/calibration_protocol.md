# Calibration Protocol  
**Phase-Memory Operator**

**Reference:** Krüger & Feeney (2026), Sections 5–6  
**Status:** Mandatory protocol for all reported results

---

## Purpose

This document specifies the **mandatory calibration, validation, and test protocol** for the Phase-Memory Operator.

Its purpose is to prevent data leakage, overfitting, and post-hoc tuning, and to ensure **deterministic, auditable evaluation**.

All results reported in the paper and this repository adhere to this protocol.

---

## Overview

The protocol consists of **three strictly ordered phases**:

1. **Calibration**
2. **Validation**
3. **Test**

Once parameters are frozen at the end of calibration, **no further tuning is permitted**.

Calibration → Validation → Test
│ │ │
parameter fit sanity check final evaluation
│
FREEZE


---

## Phase 1: Calibration

### Inputs
- Contiguous calibration window (earliest segment of data)
- Observed signal(s)
- Binary labels indicating regime-shift proximity (if available)

### Steps

1. **Phase extraction**
   - Compute analytic signal via the Hilbert transform
   - Extract instantaneous phase θ(t)
   - Apply quality checks (SNR, amplitude thresholds)

2. **Reference phase construction**
   - Construct θ_ref(t) from a stable baseline window
   - Default method: mean-frequency reference

3. **Triadic state computation**
   - U₁(t): phase deviation  
   - U₂(t): drift rate  
   - U₃(t): accumulated memory (hysteresis)

4. **Stability functional calibration**
   - Fit non-negative weights (a, b, c) in

     ```
     J(t) = a·U₁² + b·U₂² + c·U₃²
     ```

   - Objective: maximize ROC-AUC (or PR-AUC if specified)
   - Channels may be normalized for numerical stability

5. **Alert threshold calibration**
   - Fix dwell time ΔT **a priori**
   - Select J_threshold to meet a target false-alarm rate on calibration data

### Output

- Calibrated parameters:
  - Stability weights (a, b, c)
  - Alert threshold J_threshold
  - Dwell time ΔT

All parameters are then **frozen**.

---

## Parameter Freezing Rule (Critical)

After calibration:

- All parameters **must be frozen**
- Any attempt to modify parameters raises an error
- Frozen parameters are logged to disk  
  (e.g. `locked_params_example.yaml`)

No parameter updates are permitted in validation or test phases.

---

## Phase 2: Validation

### Purpose

Validation is used **only** to:

- sanity-check behavior
- confirm stability under mild perturbations
- verify that performance is not degenerate

### Rules

- Frozen parameters are used **as-is**
- No tuning, refitting, or threshold adjustment
- Validation metrics **do not replace** test metrics

Validation results may be reported descriptively but are not considered final.

---

## Phase 3: Test (Final Evaluation)

### Purpose

The test phase provides the **final, single-shot evaluation** of the method.

### Rules (Strict)

- Test data must be disjoint and temporally downstream from calibration and validation
- Parameters remain frozen
- Test phase is executed **once**
- All reported performance metrics must be pre-declared

### Typical metrics

- ROC-AUC
- PR-AUC
- False-alarm rate
- Lead-time distribution
- Detection rate

---

## Prohibited Practices

The following actions **invalidate results**:

- Tuning parameters on validation or test data
- Re-running the test phase to improve metrics
- Mixing samples across temporal splits
- Selecting thresholds post-hoc based on test outcomes
- Reporting best-of-N runs

---

## Falsification Criteria

The method is considered falsified if, under locked parameters:

- No meaningful lead-time advantage over simple baselines
- Performance collapses under mild noise or resampling
- False-alarm rate renders the method impractical
- Parameters fail to transfer across sessions within the stated domain

These criteria are evaluated **only on the test set**.

---

## Reproducibility

All calibration artifacts must be logged, including:

- parameter values
- normalization statistics
- random seeds
- software versions
- data hashes (where applicable)

Deterministic replay is demonstrated in  
`validation/eeg_replay.ipynb`.

---

## Scope Note

This protocol governs **methodological correctness**, not domain validity.

Successful detection in one domain (e.g. EEG) does not imply mechanistic transfer to other systems.

---

**End of protocol**


