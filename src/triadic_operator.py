"""
Triadic Phase–Memory Operator

Implements U1, U2, U3 channels for:
- phase deviation (fast),
- drift / timing slip (medium),
- accumulated memory / hysteresis (slow).

Equations (2)–(4) in:
Krüger & Feeney (2026), Section 4
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class TriadicState:
    """
    Container for triadic operator output.
    """
    U1: np.ndarray  # Phase deviation
    U2: np.ndarray  # Drift rate
    U3: np.ndarray  # Accumulated memory
    t: np.ndarray   # Time vector

    def __repr__(self):
        return (
            f"TriadicState(n={len(self.t)}, "
            f"U1_range=[{self.U1.min():.3f}, {self.U1.max():.3f}], "
            f"U2_range=[{self.U2.min():.3f}, {self.U2.max():.3f}], "
            f"U3_range=[{self.U3.min():.3f}, {self.U3.max():.3f}])"
        )


def compute_U1(
    theta: np.ndarray,
    theta_ref: np.ndarray,
    wrap: bool = True
) -> np.ndarray:
    """
    Compute U1: instantaneous phase deviation.

    U1(t) = Δθ(t) = wrap(θ(t) − θ_ref(t))   (Eq. 2)
    """
    if theta.shape != theta_ref.shape:
        raise ValueError("theta and theta_ref must have the same shape")

    delta = theta - theta_ref

    if wrap:
        delta = ((delta + np.pi) % (2 * np.pi)) - np.pi

    return delta


def compute_U2(
    theta: np.ndarray,
    theta_ref: np.ndarray,
    dt: float
) -> np.ndarray:
    """
    Compute U2: drift rate / timing slip.

    U2(t) = dθ/dt − dθ_ref/dt   (Eq. 3)
    """
    omega = np.gradient(theta, dt)
    omega_ref = np.gradient(theta_ref, dt)

    return omega - omega_ref


def compute_U3(
    U1: np.ndarray,
    t: np.ndarray,
    w: Optional[np.ndarray] = None,
    t0_idx: int = 0
) -> np.ndarray:
    """
    Compute U3: accumulated memory / hysteresis state.

    U3(t) = ∫[t0→t] w(τ) · U1(τ) dτ   (Eq. 4)

    Notes
    -----
    - Integration is causal.
    - Memory accumulation starts at index t0_idx.
    - No decay or reset is applied unless implemented upstream.
    """
    if w is None:
        w = np.ones_like(U1)

    if U1.shape != w.shape:
        raise ValueError("U1 and w must have the same shape")

    if not 0 <= t0_idx < len(U1):
        raise ValueError(f"t0_idx {t0_idx} out of bounds [0, {len(U1)-1}]")

    U3 = np.zeros_like(U1)

    for i in range(max(t0_idx + 1, 1), len(U1)):
        dt = t[i] - t[i - 1]
        if dt <= 0:
            raise ValueError(f"Non-monotonic time at index {i}: dt = {dt}")
        U3[i] = U3[i - 1] + 0.5 * dt * (
            w[i] * U1[i] + w[i - 1] * U1[i - 1]
        )

    return U3


def compute_triadic_state(
    theta: np.ndarray,
    theta_ref: np.ndarray,
    t: np.ndarray,
    w: Optional[np.ndarray] = None,
    wrap_U1: bool = True,
    t0_idx: int = 0
) -> TriadicState:
    """
    Compute full triadic state (U1, U2, U3).

    This function is deterministic and stateless.
    """
    if len(t) < 2:
        raise ValueError("Time vector must contain at least two samples")

    dt = float(np.mean(np.diff(t)))

    U1 = compute_U1(theta, theta_ref, wrap=wrap_U1)
    U2 = compute_U2(theta, theta_ref, dt=dt)
    U3 = compute_U3(U1, t, w=w, t0_idx=t0_idx)

    return TriadicState(U1=U1, U2=U2, U3=U3, t=t)


def apply_gating_function(
    amplitude: np.ndarray,
    snr_threshold: float = 2.0,
    hysteresis: float = 0.5
) -> np.ndarray:
    """
    Optional amplitude-based gating function w(t).

    This implements a simple, deterministic quality gate.
    It is not required by the core operator.
    """
    median_amp = np.median(amplitude)
    norm_amp = amplitude / (median_amp + 1e-12)

    w = np.zeros_like(amplitude)
    state = False

    upper = snr_threshold + hysteresis
    lower = snr_threshold - hysteresis

    for i, a in enumerate(norm_amp):
        if state and a < lower:
            state = False
        elif not state and a > upper:
            state = True

        w[i] = 1.0 if state else 0.0

    return w


if __name__ == "__main__":
    # Self-test with synthetic phase trajectories
    t = np.linspace(0, 10, 1000)

    omega_ref = 2 * np.pi * 1.5
    theta_ref = omega_ref * t

    drift = 0.1 * t
    deviation = 0.3 * np.sin(2 * np.pi * 0.2 * t)
    theta = theta_ref + drift + deviation

    state = compute_triadic_state(theta, theta_ref, t)

    print("Triadic operator test")
    print(f"U1 mean/std: {np.mean(state.U1):.3f} / {np.std(state.U1):.3f}")
    print(f"U2 mean (drift): {np.mean(state.U2):.3f}")
    print(f"U3 final value: {state.U3[-1]:.3f}")
    print(state)
