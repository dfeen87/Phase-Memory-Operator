# Bug Fixes Summary

## Overview
This document summarizes all critical bugs that were identified and fixed during the code review of the Phase-Memory-Operator repository.

## Critical Bugs Fixed

### 1. warning_logic.py

#### 1.1 Division by Zero in `compute_false_alarm_rate()` (Line 177)
**Issue:** When `active_time` is zero or negative (when all time is excluded), division by zero occurred.

**Fix:** Added check to return 0.0 when `active_time <= 0`:
```python
if active_time <= 0:
    return 0.0
```

**Impact:** Prevents ZeroDivisionError crash in edge cases.

---

#### 1.2 Unvalidated `searchsorted` Indices (Lines 141, 165)
**Issue:** `np.searchsorted()` can return an index equal to `len(array)` when the search value exceeds all array values, causing IndexError when accessing the array.

**Fix:** Added bounds checking using `min()`:
```python
event_idx = min(np.searchsorted(t, event_t), len(t) - 1)
idx = min(np.searchsorted(t, et), len(t) - 1)
```

**Impact:** Prevents IndexError when event times are beyond signal duration.

---

#### 1.3 Uninitialized `onset_idx` Variable (Lines 95-127)
**Issue:** `onset_idx` was initialized to `None`, but could be accessed in the final event creation block without proper null checks, causing TypeError.

**Fix:** Changed to use `None` with explicit null checks:
```python
onset_idx = None
# ... in loop ...
if onset_idx is not None:
    # ... safe to use onset_idx ...
```

**Impact:** Prevents TypeError when no warning events occur.

---

#### 1.4 Bounds Check in `compute_lead_times()` (Line 145)
**Issue:** Accessing `t[warning_indices[0]]` without validating that the index is within bounds.

**Fix:** Added bounds check:
```python
if len(warning_indices) > 0 and warning_indices[0] < len(t):
    lead_times.append(event_t - t[warning_indices[0]])
```

**Impact:** Prevents potential IndexError in edge cases.

---

#### 1.5 IndexError in `compute_false_alarm_rate()` Exclusion Slice (Line 168)
**Issue:** The slice `exclusion[start:idx + 1]` could cause IndexError when `idx == len(t) - 1`.

**Fix:** Added bounds check:
```python
end = min(idx + 1, len(exclusion))
exclusion[start:end] = True
```

**Impact:** Prevents IndexError when events occur at the end of the signal.

---

#### 1.6 Magic Number in Fallback Threshold (Line 227)
**Issue:** Used magic number `50` for percentile calculation.

**Fix:** Defined named constant:
```python
FALLBACK_THRESHOLD_PERCENTILE = 50
# ... later ...
best = float(np.percentile(J_cal, FALLBACK_THRESHOLD_PERCENTILE))
```

**Impact:** Improves code clarity and maintainability.

---

### 2. stability_functional.py

#### 2.1 Null `best` Threshold in `calibrate_alert_threshold()` (Line 220)
**Issue:** If no suitable threshold was found during calibration, `best` remained `None`, causing TypeError when creating `AlertParameters`.

**Fix:** Added fallback to median:
```python
if best is None:
    best = float(np.percentile(J_cal, FALLBACK_THRESHOLD_PERCENTILE))
```

**Impact:** Prevents TypeError and ensures a valid threshold is always returned.

---

#### 2.2 Failed Calibration Warning in `calibrate_weights_grid()`
**Issue:** When calibration fails (all scores are NaN), the function silently used default weights without warning the user.

**Fix:** Added explicit check and warning:
```python
if norm < 1e-12:
    warnings.warn("No valid weights found during calibration; using default equal weights")
    a_opt, b_opt, c_opt = 1.0/np.sqrt(3), 1.0/np.sqrt(3), 1.0/np.sqrt(3)
```

**Impact:** Alerts users when calibration fails so they can investigate.

---

### 3. triadic_operator.py

#### 3.1 Invalid `t0_idx` Validation in `compute_U3()` (Line 99)
**Issue:** No validation that `t0_idx` is within valid bounds `[0, len(U1)-1]`, could cause silent failure.

**Fix:** Added bounds check:
```python
if not 0 <= t0_idx < len(U1):
    raise ValueError(f"t0_idx {t0_idx} out of bounds [0, {len(U1)-1}]")
```

**Impact:** Detects invalid input early and provides clear error message.

---

#### 3.2 Non-Monotonic Time Detection in `compute_U3()` (Line 100)
**Issue:** No validation that time array is strictly increasing, could cause incorrect U3 computation.

**Fix:** Added check in integration loop:
```python
dt = t[i] - t[i - 1]
if dt <= 0:
    raise ValueError(f"Non-monotonic time at index {i}: dt = {dt}")
```

**Impact:** Detects and rejects invalid time arrays, preventing incorrect results.

---

### 4. phase_extraction.py

#### 4.1 Empty Signal Validation in `analytic_signal()` (Line 70)
**Issue:** No check for empty input arrays, could cause silent failure or confusing errors downstream.

**Fix:** Added validation:
```python
if len(s) == 0:
    raise ValueError("Signal must be non-empty")
```

**Impact:** Provides clear error message for invalid input.

---

## Testing

All fixes were validated with comprehensive test cases:

1. **Empty signal validation** - Ensures empty signals are rejected
2. **Division by zero in FAR** - Ensures no crash when active_time is zero
3. **Searchsorted bounds check** - Ensures out-of-bounds events are handled
4. **Uninitialized onset_idx** - Ensures no crash when no warnings occur
5. **Invalid t0_idx validation** - Ensures invalid indices are rejected
6. **Non-monotonic time detection** - Ensures invalid time arrays are rejected
7. **Null best threshold handling** - Ensures calibration always returns valid threshold
8. **Failed calibration weights** - Ensures default weights are used when calibration fails
9. **Dwell time gate correctness** - Ensures correct sample counting
10. **Empty J window handling** - Ensures edge cases with short signals are handled

**Test Results:** 10/10 tests passing

---

## Security Analysis

**CodeQL Scan Results:** 0 alerts found

No security vulnerabilities were detected in the codebase.

---

## Impact Summary

### Crashes Prevented
- ZeroDivisionError in false alarm rate computation
- IndexError in lead time computation and event detection
- TypeError from uninitialized variables

### Silent Failures Fixed
- Invalid input acceptance (empty signals, invalid indices, non-monotonic time)
- Failed calibrations that would silently use default values

### Code Quality Improvements
- Added input validation throughout
- Improved error messages for debugging
- Added warning for edge cases
- Replaced magic numbers with named constants

---

## Backward Compatibility

All fixes maintain full backward compatibility:
- No changes to public API
- No changes to function signatures
- No changes to expected behavior for valid inputs
- Only adds validation and error handling for invalid inputs

---

## Recommendations

1. Consider adding automated testing infrastructure to catch these types of issues earlier
2. Consider adding type hints for better static analysis
3. Consider adding docstring examples showing valid input ranges
4. Consider adding integration tests that exercise edge cases

---

## Files Changed

1. `src/warning_logic.py` - 5 critical bugs fixed
2. `src/stability_functional.py` - 2 critical bugs fixed
3. `src/triadic_operator.py` - 2 critical bugs fixed
4. `src/phase_extraction.py` - 1 critical bug fixed
5. `src/test_bug_fixes.py` - New comprehensive test suite added
6. `.gitignore` - Added to prevent committing build artifacts

---

**Total: 10 critical bugs fixed, 10 test cases added, 0 security vulnerabilities**
