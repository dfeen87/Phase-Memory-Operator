"""
Phase Extraction Module

Implements analytic signal construction and instantaneous phase estimation
via Hilbert transform (Eq. 1 in the paper).

Used for construction of:
- θ(t): instantaneous phase
- ω(t): instantaneous frequency (drift channel precursor)
- Δθ(t): wrapped phase deviation for U1

Reference:
Krüger & Feeney (2026), Section 3 and Section 9 (Limitations)
"""

import numpy as np
from scipy.signal import hilbert
from typing import Tuple
import warnings


def wrap_phase(theta: np.ndarray, period: float = 2 * np.pi) -> np.ndarray:
    """
    Wrap phase to [-π, π] or custom period.

    Used for U1(t) = Δθ(t) computation (Eq. 2).

    Parameters
    ----------
    theta : np.ndarray
        Unwrapped phase
    period : float, default=2π
        Wrapping period

    Returns
    -------
    np.ndarray
        Wrapped phase in [-period/2, period/2]
    """
    return ((theta + period / 2) % period) - period / 2


def analytic_signal(s: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Construct analytic signal via Hilbert transform.

    z(t) = s(t) + i·H[s(t)]
    θ(t) = arg(z(t))

    Parameters
    ----------
    s : np.ndarray
        Real-valued input signal (must be 1D)

    Returns
    -------
    z : np.ndarray (complex)
        Analytic signal
    theta : np.ndarray
        Instantaneous phase (unwrapped)
    amplitude : np.ndarray
        Instantaneous amplitude

    Notes
    -----
    Phase estimation quality depends on oscillatory content.
    Non-oscillatory or low-SNR signals may yield meaningless phase.
    See paper Section 9 (Limitations).
    """
    if s.ndim != 1:
        raise ValueError("Signal must be one-dimensional")

    if len(s) == 0:
        raise ValueError("Signal must be non-empty")

    if np.any(np.isnan(s)) or np.any(np.isinf(s)):
        raise ValueError("Signal contains NaN or Inf values")

    z = hilbert(s)
    theta = np.unwrap(np.angle(z))
    amplitude = np.abs(z)

    return z, theta, amplitude


def instantaneous_frequency(theta: np.ndarray, dt: float = 1.0) -> np.ndarray:
    """
    Compute instantaneous frequency ω(t) = dθ/dt.

    Parameters
    ----------
    theta : np.ndarray
        Unwrapped instantaneous phase
    dt : float, default=1.0
        Sampling interval

    Returns
    -------
    np.ndarray
        Instantaneous frequency (same length as theta)
    """
    return np.gradient(theta, dt)


def construct_reference_phase(
    s_baseline: np.ndarray,
    dt: float = 1.0,
    method: str = "mean_frequency"
) -> Tuple[np.ndarray, dict]:
    """
    Construct reference phase θ_ref(t) from a baseline segment.

    Parameters
    ----------
    s_baseline : np.ndarray
        Baseline signal segment (stable operating condition)
    dt : float, default=1.0
        Sampling interval
    method : str, default='mean_frequency'
        Reference construction method:
        - 'mean_frequency': constant ω_ref from baseline
        - 'direct': use θ_baseline directly

    Returns
    -------
    theta_ref : np.ndarray
        Reference phase trajectory (baseline window only)
    metadata : dict
        Construction metadata for deterministic replay

    Notes
    -----
    θ_ref is constructed only over the baseline window.
    Extension or alignment outside this window must be handled by the caller.
    """
    _, theta_baseline, _ = analytic_signal(s_baseline)

    metadata = {
        "method": method,
        "baseline_length": len(s_baseline),
        "dt": dt
    }

    if method == "mean_frequency":
        omega_baseline = instantaneous_frequency(theta_baseline, dt)
        omega_ref = float(np.mean(omega_baseline))

        t = np.arange(len(s_baseline)) * dt
        theta_ref = omega_ref * t + theta_baseline[0]

        metadata["omega_ref"] = omega_ref

    elif method == "direct":
        theta_ref = theta_baseline

    else:
        raise ValueError(f"Unknown reference phase method: {method}")

    return theta_ref, metadata


def validate_phase_quality(
    amplitude: np.ndarray,
    snr_threshold: float = 3.0
) -> Tuple[bool, str]:
    """
    Heuristic check for phase estimation quality.

    Parameters
    ----------
    amplitude : np.ndarray
        Instantaneous amplitude from analytic signal
    snr_threshold : float, default=3.0
        Minimum acceptable amplitude SNR estimate

    Returns
    -------
    is_valid : bool
        Whether phase estimation is likely reliable
    message : str
        Diagnostic message

    Notes
    -----
    This check is advisory only and does not halt execution.
    """
    mean_amp = np.mean(amplitude)
    std_amp = np.std(amplitude)

    if mean_amp < 1e-6:
        return False, "Amplitude too low – possible DC or flat signal"

    snr_estimate = mean_amp / (std_amp + 1e-12)

    if snr_estimate < snr_threshold:
        warnings.warn(
            f"Low phase SNR estimate ({snr_estimate:.2f} < {snr_threshold}). "
            "Phase estimation may be unreliable (see paper Section 9). "
            "This warning is non-fatal."
        )
        return False, f"SNR estimate {snr_estimate:.2f} below threshold"

    return True, f"Phase quality acceptable (SNR ≈ {snr_estimate:.2f})"


def phase_summary(theta: np.ndarray, omega: np.ndarray) -> dict:
    """
    Return summary statistics for logging and deterministic replay.
    """
    return {
        "theta_min": float(np.min(theta)),
        "theta_max": float(np.max(theta)),
        "omega_mean": float(np.mean(omega)),
        "omega_std": float(np.std(omega))
    }


if __name__ == "__main__":
    # Simple self-test with synthetic oscillatory signal
    t = np.linspace(0, 10, 1000)
    dt = t[1] - t[0]

    s = np.sin(2 * np.pi * 1.5 * t)

    z, theta, amp = analytic_signal(s)
    omega = instantaneous_frequency(theta, dt)

    valid, msg = validate_phase_quality(amp)

    print("Phase extraction test")
    print(f"Mean frequency: {np.mean(omega)/(2*np.pi):.3f} Hz (expected ~1.5)")
    print(f"Quality check: {msg}")
    print("Summary:", phase_summary(theta, omega))
