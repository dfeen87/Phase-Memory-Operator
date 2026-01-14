"""
Stability Functional

Implements:
J(t) = a·U1(t)^2 + b·U2(t)^2 + c·U3(t)^2  (Eq. 5)

This module also provides OPTIONAL calibration utilities for selecting (a, b, c)
on a calibration window only, consistent with the paper's protocol.

Reference:
Krüger & Feeney (2026), Section 5 and Section 6 (parameter freezing / replay)
"""

import numpy as np
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class StabilityParameters:
    """
    Container for stability functional parameters.

    Notes
    -----
    - Weights (a, b, c) must be non-negative.
    - Freeze after calibration to enforce locked-parameter evaluation.
    """
    a: float
    b: float
    c: float
    frozen: bool = False

    def __post_init__(self):
        if self.a < 0 or self.b < 0 or self.c < 0:
            raise ValueError("Weights must be non-negative")

    def freeze(self) -> None:
        """Lock parameters (cannot be modified after this)."""
        object.__setattr__(self, "frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "frozen", False) and name != "frozen":
            raise AttributeError(
                f"Cannot modify '{name}': parameters are frozen. "
                "See paper Section 6 (locked test evaluation)."
            )
        super().__setattr__(name, value)

    def to_dict(self) -> dict:
        return {"a": float(self.a), "b": float(self.b), "c": float(self.c), "frozen": bool(self.frozen)}


def compute_stability_functional(
    U1: np.ndarray,
    U2: np.ndarray,
    U3: np.ndarray,
    params: StabilityParameters
) -> np.ndarray:
    """
    Compute stability functional J(t) (Eq. 5).

    J(t) = a·U1^2 + b·U2^2 + c·U3^2
    """
    return params.a * (U1 ** 2) + params.b * (U2 ** 2) + params.c * (U3 ** 2)


def normalize_channels(
    U1: np.ndarray,
    U2: np.ndarray,
    U3: np.ndarray,
    eps: float = 1e-12
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """
    Normalize channels by standard deviation for calibration convenience.

    Returns normalized channels plus the normalization statistics for replay logging.
    """
    stats = {
        "U1_std": float(np.std(U1) + eps),
        "U2_std": float(np.std(U2) + eps),
        "U3_std": float(np.std(U3) + eps),
        "eps": float(eps),
    }

    return U1 / stats["U1_std"], U2 / stats["U2_std"], U3 / stats["U3_std"], stats


def _roc_auc_safe(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    ROC-AUC with optional sklearn dependency.
    Returns np.nan if unavailable or ill-posed (e.g., single-class labels).
    """
    try:
        from sklearn.metrics import roc_auc_score
        # roc_auc_score fails if only one class present
        if len(np.unique(y_true)) < 2:
            return float("nan")
        return float(roc_auc_score(y_true, y_score))
    except Exception:
        return float("nan")


def _pr_auc_safe(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    PR-AUC with optional sklearn dependency.
    Returns np.nan if unavailable or ill-posed.
    """
    try:
        from sklearn.metrics import precision_recall_curve, auc
        if len(np.unique(y_true)) < 2:
            return float("nan")
        precision, recall, _ = precision_recall_curve(y_true, y_score)
        return float(auc(recall, precision))
    except Exception:
        return float("nan")


def evaluate_discriminative_power(J: np.ndarray, labels: np.ndarray) -> dict:
    """
    Evaluate discriminative metrics (optional sklearn).

    Returns ROC-AUC and PR-AUC when available.
    """
    roc_auc = _roc_auc_safe(labels, J)
    pr_auc = _pr_auc_safe(labels, J)

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "J_mean": float(np.mean(J)),
        "J_std": float(np.std(J)),
        "J_min": float(np.min(J)),
        "J_max": float(np.max(J)),
    }


def calibrate_weights_grid(
    U1_cal: np.ndarray,
    U2_cal: np.ndarray,
    U3_cal: np.ndarray,
    labels_cal: np.ndarray,
    objective: str = "roc_auc",
    normalize: bool = True,
    grid: Optional[np.ndarray] = None
) -> Tuple[StabilityParameters, dict]:
    """
    OPTIONAL: Calibrate (a, b, c) on the calibration window only.

    This function uses a deterministic grid search over non-negative weights,
    then normalizes (a, b, c) to unit L2 norm for interpretability.

    Parameters
    ----------
    objective : {'roc_auc','pr_auc'}
        Metric to maximize (requires sklearn; returns best-effort if missing).
    normalize : bool
        If True, standardize U1/U2/U3 by their calibration std-devs before searching.
    grid : np.ndarray, optional
        Candidate weights to search (e.g., np.linspace(0, 2, 21)).
        If None, uses a small default grid.

    Returns
    -------
    params : StabilityParameters
        Best weights found (NOT frozen; caller should freeze after selecting thresholds).
    metadata : dict
        Calibration metadata for deterministic replay logging.

    Notes
    -----
    For reviewer-auditable evaluation:
    - run only on the calibration window
    - lock params after calibration
    - do not retune on validation/test
    """
    if grid is None:
        # Small, deterministic grid: fast and transparent
        grid = np.linspace(0.0, 2.0, 21)

    if normalize:
        U1n, U2n, U3n, norm_stats = normalize_channels(U1_cal, U2_cal, U3_cal)
    else:
        U1n, U2n, U3n = U1_cal, U2_cal, U3_cal
        norm_stats = None

    def score_fn(J: np.ndarray) -> float:
        if objective == "roc_auc":
            return _roc_auc_safe(labels_cal, J)
        elif objective == "pr_auc":
            return _pr_auc_safe(labels_cal, J)
        else:
            raise ValueError(f"Unknown objective: {objective}")

    best_score = -np.inf
    best_weights = (1.0, 1.0, 1.0)

    # Deterministic brute-force grid search
    for a in grid:
        for b in grid:
            for c in grid:
                if a == 0 and b == 0 and c == 0:
                    continue
                J = a * (U1n ** 2) + b * (U2n ** 2) + c * (U3n ** 2)
                s = score_fn(J)

                # If sklearn unavailable, s may be nan; keep default weights.
                if np.isnan(s):
                    continue

                if s > best_score:
                    best_score = s
                    best_weights = (float(a), float(b), float(c))

    a_opt, b_opt, c_opt = best_weights

    # Normalize to unit L2 norm (interpretability; scale absorbed by threshold Jc)
    norm = float(np.sqrt(a_opt**2 + b_opt**2 + c_opt**2) + 1e-12)
    a_opt, b_opt, c_opt = a_opt / norm, b_opt / norm, c_opt / norm

    params = StabilityParameters(a=a_opt, b=b_opt, c=c_opt)

    metadata = {
        "objective": objective,
        "normalized": bool(normalize),
        "norm_stats": norm_stats,
        "grid_min": float(np.min(grid)),
        "grid_max": float(np.max(grid)),
        "grid_n": int(len(grid)),
        "best_score": float(best_score) if best_score != -np.inf else float("nan"),
        "n_calibration_samples": int(len(U1_cal)),
        "class_balance": float(np.mean(labels_cal)) if len(labels_cal) else float("nan"),
        "note": "Calibration performed via deterministic grid search; lock parameters after calibration.",
    }

    return params, metadata


if __name__ == "__main__":
    # Minimal self-test (synthetic)
    np.random.seed(42)

    n = 1000
    regime_shift_idx = 700

    U1 = 0.1 * np.random.randn(n)
    U1[regime_shift_idx:] += 0.5 * np.linspace(0, 1, n - regime_shift_idx)

    U2 = 0.05 * np.random.randn(n)
    U2[regime_shift_idx:] += 0.2 * np.linspace(0, 1, n - regime_shift_idx)

    U3 = np.cumsum(U1) * 0.01

    labels = np.zeros(n)
    labels[regime_shift_idx - 50:] = 1

    print("Calibrating stability functional weights (deterministic grid)...")
    params, meta = calibrate_weights_grid(U1, U2, U3, labels, objective="roc_auc", normalize=True)

    print("Weights:", params.to_dict())
    print("Calibration metadata:", {k: meta[k] for k in ["objective", "best_score", "grid_n", "normalized"]})

    J = compute_stability_functional(U1, U2, U3, params)
    metrics = evaluate_discriminative_power(J, labels)
    print("Metrics:", metrics)

    print("Freezing parameters...")
    params.freeze()
    try:
        params.a = 0.5
    except AttributeError as e:
        print("Freeze check OK:", e)
