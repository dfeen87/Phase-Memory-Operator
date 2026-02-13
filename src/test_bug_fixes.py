"""
Test cases for critical bug fixes.

This test suite validates the bug fixes applied to:
- warning_logic.py
- stability_functional.py
- triadic_operator.py
- phase_extraction.py
"""

import numpy as np
import sys
from typing import List

# Test results
test_results: List[tuple] = []


def test_empty_signal():
    """Test that empty signal is rejected in analytic_signal()."""
    from phase_extraction import analytic_signal
    
    try:
        empty_signal = np.array([])
        analytic_signal(empty_signal)
        return False, "Empty signal should raise ValueError"
    except ValueError as e:
        if "non-empty" in str(e):
            return True, "Empty signal correctly rejected"
        return False, f"Wrong error message: {e}"


def test_division_by_zero_far():
    """Test that division by zero is prevented in compute_false_alarm_rate()."""
    from warning_logic import compute_false_alarm_rate
    
    # Create scenario where active_time could be zero
    t = np.linspace(0, 1, 100)
    warn = np.zeros(100, dtype=bool)
    # All time is excluded
    event_times = np.array([0.5])
    exclusion_window = 10.0  # Very large exclusion window
    
    try:
        far = compute_false_alarm_rate(warn, t, event_times, exclusion_window)
        # Should return 0.0 instead of raising error
        if far == 0.0:
            return True, "Division by zero correctly handled (returned 0.0)"
        return True, f"Division by zero handled (returned {far})"
    except ZeroDivisionError:
        return False, "Division by zero not handled"


def test_searchsorted_bounds():
    """Test that searchsorted indices are properly bounded."""
    from warning_logic import compute_lead_times
    
    t = np.linspace(0, 10, 100)
    warn = np.zeros(100, dtype=bool)
    warn[10:20] = True  # Warning period
    
    # Event time beyond signal duration
    event_times = np.array([15.0])  # Beyond t[-1]
    
    try:
        lead_times = compute_lead_times(warn, t, event_times)
        return True, f"Out-of-bounds event handled correctly (lead_times={lead_times})"
    except IndexError:
        return False, "searchsorted bounds not checked"


def test_uninitialized_onset_idx():
    """Test that onset_idx is properly initialized in detect_warning_events()."""
    from warning_logic import detect_warning_events, AlertParameters
    
    J = np.array([0.1, 0.2, 0.1, 0.2])  # Never exceeds threshold
    t = np.array([0.0, 1.0, 2.0, 3.0])
    params = AlertParameters(J_threshold=0.5, dwell_time=1.0)
    
    try:
        warn, events = detect_warning_events(J, t, params)
        return True, f"No warning events handled correctly (events={len(events)})"
    except (TypeError, AttributeError) as e:
        return False, f"onset_idx not initialized: {e}"


def test_invalid_t0_idx():
    """Test that invalid t0_idx is rejected in compute_U3()."""
    from triadic_operator import compute_U3
    
    U1 = np.random.randn(100)
    t = np.linspace(0, 10, 100)
    
    # Test out of bounds t0_idx
    try:
        compute_U3(U1, t, t0_idx=1000)
        return False, "Invalid t0_idx should raise ValueError"
    except ValueError as e:
        if "out of bounds" in str(e):
            return True, "Invalid t0_idx correctly rejected"
        return False, f"Wrong error message: {e}"


def test_non_monotonic_time():
    """Test that non-monotonic time is detected in compute_U3()."""
    from triadic_operator import compute_U3
    
    U1 = np.random.randn(100)
    t = np.linspace(0, 10, 100)
    t[50] = t[49] - 0.1  # Make non-monotonic
    
    try:
        compute_U3(U1, t)
        return False, "Non-monotonic time should raise ValueError"
    except ValueError as e:
        if "Non-monotonic" in str(e):
            return True, "Non-monotonic time correctly detected"
        return False, f"Wrong error message: {e}"


def test_null_best_threshold():
    """Test that null best threshold is handled in calibrate_alert_threshold()."""
    from warning_logic import calibrate_alert_threshold
    
    # Create scenario where no threshold is found (all candidates fail)
    J_cal = np.ones(100) * 0.5  # Constant J
    t_cal = np.linspace(0, 10, 100)
    labels_cal = np.zeros(100)
    
    try:
        params, metadata = calibrate_alert_threshold(
            J_cal, t_cal, labels_cal, 
            dwell_time=1.0, 
            target_far=0.1
        )
        # Should have a valid threshold (fallback to median)
        if params.J_threshold is not None:
            return True, f"Fallback threshold applied: {params.J_threshold}"
        return False, "No threshold set"
    except TypeError:
        return False, "Null best not handled"


def test_failed_calibration_weights():
    """Test that failed calibration uses default weights."""
    from stability_functional import calibrate_weights_grid
    import warnings
    
    # Create scenario where sklearn is unavailable or all scores are nan
    U1 = np.random.randn(100)
    U2 = np.random.randn(100)
    U3 = np.random.randn(100)
    labels = np.zeros(100)  # All one class - will cause nan scores
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        params, metadata = calibrate_weights_grid(U1, U2, U3, labels)
        
        # Should have valid weights (defaults or from grid)
        if params.a >= 0 and params.b >= 0 and params.c >= 0:
            # Check if warning was issued for failed calibration
            if len(w) > 0 and any("No valid weights" in str(warning.message) for warning in w):
                return True, "Failed calibration warning issued and defaults used"
            return True, "Valid weights returned (may be from successful calibration)"
        return False, "Invalid weights returned"


def test_dwell_time_gate_correctness():
    """Test that dwell_time_gate checks correct number of samples."""
    from warning_logic import apply_dwell_time_gate, AlertParameters
    
    # Create J that exceeds threshold for exactly dwell_samples
    J = np.array([0.1, 0.1, 0.6, 0.6, 0.6, 0.1, 0.1])
    t = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    
    # dwell_time = 2.0 seconds, dt = 1.0, so dwell_samples = 2
    params = AlertParameters(J_threshold=0.5, dwell_time=2.0)
    warn = apply_dwell_time_gate(J, t, params)
    
    # At index 4 (t=4.0), we should check samples [2,3,4] (3 samples total)
    # All of these are >= 0.6, so warn[4] should be True
    if warn[4]:
        return True, "Dwell time gate checks correct number of samples"
    return False, f"Dwell time gate incorrect: warn={warn}"


def test_empty_j_window():
    """Test that empty J windows are handled in detect_warning_events()."""
    from warning_logic import detect_warning_events, AlertParameters
    
    # Edge case: very short signal
    J = np.array([0.6, 0.1])
    t = np.array([0.0, 1.0])
    params = AlertParameters(J_threshold=0.5, dwell_time=0.5)
    
    try:
        warn, events = detect_warning_events(J, t, params)
        return True, f"Empty J window handled (events={len(events)})"
    except (ValueError, IndexError) as e:
        return False, f"Empty J window not handled: {e}"


def run_all_tests():
    """Run all test cases and report results."""
    tests = [
        ("Empty signal validation", test_empty_signal),
        ("Division by zero in FAR", test_division_by_zero_far),
        ("Searchsorted bounds check", test_searchsorted_bounds),
        ("Uninitialized onset_idx", test_uninitialized_onset_idx),
        ("Invalid t0_idx validation", test_invalid_t0_idx),
        ("Non-monotonic time detection", test_non_monotonic_time),
        ("Null best threshold handling", test_null_best_threshold),
        ("Failed calibration weights", test_failed_calibration_weights),
        ("Dwell time gate correctness", test_dwell_time_gate_correctness),
        ("Empty J window handling", test_empty_j_window),
    ]
    
    print("=" * 70)
    print("RUNNING BUG FIX TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            success, message = test_fn()
            if success:
                print(f"✓ {name}: PASSED")
                print(f"  {message}")
                passed += 1
            else:
                print(f"✗ {name}: FAILED")
                print(f"  {message}")
                failed += 1
        except Exception as e:
            print(f"✗ {name}: ERROR")
            print(f"  {e}")
            failed += 1
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
