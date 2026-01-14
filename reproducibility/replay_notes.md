## Deterministic Replay Notes

This repository supports deterministic replay under frozen parameters.

To reproduce results:
1. Use the locked parameter file in `calibration/`.
2. Apply identical preprocessing and reference-phase construction.
3. Do not modify weights or alert thresholds.
4. Run validation or test exactly once per protocol.

Any deviation invalidates comparability.

Optional development and documentation tools are intentionally excluded from the core requirements to preserve reproducibility.
