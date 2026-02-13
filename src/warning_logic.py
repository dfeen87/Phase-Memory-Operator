"""
Warning Logic and Alert Policy

Implements dwell-time gating and alert generation:

Warn(t) = 1 ⇔ J(τ) ≥ J_c ∀ τ ∈ [t − ΔT, t]   (Eq. 6)

Reference:
Krüger & Feeney (2026), Section 5
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AlertParameters:
    """
    Container for alert policy parameters.

    Notes
    -----
    Parameters must be frozen after calibration
    to ensure locked evaluation.
    """
    J_threshold: float
    dwell_time: float
    frozen: bool = False

    def freeze(self):
        object.__setattr__(self, "frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "frozen", False) and name != "frozen":
            raise AttributeError(
                f"Cannot modify '{name}': alert parameters are frozen."
            )
        super().__setattr__(name, value)

    def to_dict(self) -> dict:
        return {
            "J_threshold": float(self.J_threshold),
            "dwell_time": float(self.dwell_time),
            "frozen": bool(self.frozen),
        }


@dataclass
class WarningEvent:
    """
    Record of a single warning event.
    """
    onset_time: float
    onset_index: int
    J_max: float
    duration: float
    active: bool


def apply_dwell_time_gate(
    J: np.ndarray,
    t: np.ndarray,
    alert_params: AlertParameters
) -> np.ndarray:
    """
    Apply dwell-time gating to J(t).

    Returns a binary warning signal.
    """
    dt = float(np.mean(np.diff(t)))
    dwell_samples = max(1, int(np.round(alert_params.dwell_time / dt)))

    warn = np.zeros(len(J), dtype=bool)

    for i in range(dwell_samples, len(J)):
        # Check exactly dwell_samples + 1 consecutive samples (current sample + previous dwell_samples)
        if np.all(J[i - dwell_samples:i + 1] >= alert_params.J_threshold):
            warn[i] = True

    return warn


def detect_warning_events(
    J: np.ndarray,
    t: np.ndarray,
    alert_params: AlertParameters
) -> Tuple[np.ndarray, List[WarningEvent]]:
    """
    Detect discrete warning events (onset-based).
    """
    warn = apply_dwell_time_gate(J, t, alert_params)

    events: List[WarningEvent] = []
    in_event = False
    onset_idx = 0

    for i, w in enumerate(warn):
        if w and not in_event:
            onset_idx = i
            in_event = True

        elif not w and in_event:
            J_window = J[onset_idx:i]
            events.append(
                WarningEvent(
                    onset_time=t[onset_idx],
                    onset_index=onset_idx,
                    J_max=float(np.max(J_window)) if len(J_window) > 0 else 0.0,
                    duration=float(t[i - 1] - t[onset_idx]),
                    active=False,
                )
            )
            in_event = False

    if in_event and onset_idx < len(J):
        J_window = J[onset_idx:]
        events.append(
            WarningEvent(
                onset_time=t[onset_idx],
                onset_index=onset_idx,
                J_max=float(np.max(J_window)) if len(J_window) > 0 else 0.0,
                duration=float(t[-1] - t[onset_idx]),
                active=True,
            )
        )

    return warn, events


def compute_lead_times(
    warn: np.ndarray,
    t: np.ndarray,
    event_times: np.ndarray
) -> List[float]:
    """
    Compute lead time for each ground-truth event.
    """
    lead_times = []

    for event_t in event_times:
        event_idx = min(np.searchsorted(t, event_t), len(t) - 1)
        warning_indices = np.where(warn[:event_idx])[0]

        if len(warning_indices) > 0 and warning_indices[0] < len(t):
            lead_times.append(event_t - t[warning_indices[0]])
        else:
            lead_times.append(np.nan)

    return lead_times


def compute_false_alarm_rate(
    warn: np.ndarray,
    t: np.ndarray,
    event_times: np.ndarray,
    exclusion_window: float
) -> float:
    """
    Compute false alarm rate (event-based, per unit time).
    """
    dt = float(np.mean(np.diff(t)))
    exclusion = np.zeros(len(t), dtype=bool)

    for et in event_times:
        idx = min(np.searchsorted(t, et), len(t) - 1)
        start = max(0, idx - int(exclusion_window / dt))
        exclusion[start:idx + 1] = True

    # Count warning *onsets* outside exclusion windows
    onsets = np.where(np.diff(warn.astype(int)) == 1)[0] + 1
    false_onsets = [i for i in onsets if i < len(exclusion) and not exclusion[i]]

    total_time = t[-1] - t[0]
    excluded_time = np.sum(exclusion) * dt
    active_time = max(total_time - excluded_time, dt)

    # Prevent division by zero
    if active_time <= 0:
        return 0.0

    return len(false_onsets) / active_time


def calibrate_alert_threshold(
    J_cal: np.ndarray,
    t_cal: np.ndarray,
    labels_cal: np.ndarray,
    dwell_time: float,
    target_far: float,
    tolerance: float = 0.05
) -> Tuple[AlertParameters, dict]:
    """
    OPTIONAL calibration of J_threshold on calibration window only.

    Selects J_c to approximately match target false alarm rate.
    """
    event_indices = np.where(np.diff(labels_cal.astype(int)) > 0)[0]
    event_times = t_cal[event_indices] if len(event_indices) else np.array([])

    J_candidates = np.linspace(
        np.percentile(J_cal, 10),
        np.percentile(J_cal, 95),
        50,
    )

    best = None
    best_far = np.inf

    for Jc in J_candidates:
        params = AlertParameters(J_threshold=Jc, dwell_time=dwell_time)
        warn, _ = detect_warning_events(J_cal, t_cal, params)

        far = compute_false_alarm_rate(
            warn, t_cal, event_times, exclusion_window=dwell_time
        )

        if abs(far - target_far) < abs(best_far - target_far):
            best_far = far
            best = Jc

        if abs(far - target_far) <= tolerance:
            break

    # Fallback to median if no suitable threshold found
    if best is None:
        best = float(np.percentile(J_cal, 50))

    alert_params = AlertParameters(J_threshold=float(best), dwell_time=dwell_time)

    warn, _ = detect_warning_events(J_cal, t_cal, alert_params)
    lead_times = compute_lead_times(warn, t_cal, event_times)

    metadata = {
        "target_far": float(target_far),
        "achieved_far": float(best_far),
        "median_lead_time": float(np.nanmedian(lead_times)) if len(lead_times) else np.nan,
        "n_events": int(len(event_times)),
    }

    return alert_params, metadata
