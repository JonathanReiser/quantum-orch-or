"""Canonicalise floating-point results before they are serialised to JSON.

Why this exists
---------------
``benchmark_snapshot_real.py`` and ``benchmark_contestedness.py`` are pinned in
the results ledger by the sha256 of their output. The ledger regenerates them in
CI and compares bytes, which is the right check for "did this number change" --
but a raw float64 dump is not reproducible across platforms. The same code, the
same committed dataset and the same seed give different low-order bits on
different BLAS backends, because reduction order differs.

Measured on 2026-09-13 by regenerating both benchmarks on three platforms
(local arm64 macOS, ``macos-latest``, ``ubuntu-latest``) and diffing field by
field, 640 floats in total:

===========================  ==========  ==========
quantity                     worst rel   worst abs
===========================  ==========  ==========
classical benchmark           9.494e-14   3.411e-13
contestedness benchmark       1.261e-16   5.551e-17
===========================  ==========  ==========

The 9.494e-14 outlier is ``results.ridge_prevote_features.r2``. R^2 there is
~0.0129, a small difference of two much larger sums, so cancellation amplifies
its *relative* error even though the absolute error is only 1.2e-15. Everything
else sits at a few ULP.

The precision
-------------
``SIGNIFICANT_DIGITS = 6``, chosen against two independent constraints.

*Above the noise.* Rounding to 6 significant digits quantises with a relative
step of at least 1e-6. That is ~1e7 times the 9.494e-14 noise floor. A value
only changes its rounded form if it sits within the noise of a rounding
boundary, with probability ~eps/step ~ 1e-7 per value, so ~6e-5 across all 640.
Rounding is therefore not a *proof* of byte-identity, only a very strong
guarantee -- and the cross-platform CI job is what actually verifies it. Do not
raise this value without redoing that arithmetic: at 9 digits the per-run risk
is a few percent, which would make the ledger flaky rather than reproducible.

*Below every published claim.* The finest number any document asserts is four
significant digits (``10.44`` pp MAE); the rest are three (``0.660``,
``-0.125``, ``0.416``) or two (``0.0010``). Six significant digits keeps two
digits more than the most precise published claim, so every documented value
formats identically before and after canonicalisation. ``tests/
test_canonical_json.py`` pins that.

This is deliberately *not* a tolerance. The artifact on disk is exact and the
ledger's byte comparison stays exact; what changes is that the artifact no
longer records digits the computation cannot reproduce.
"""

from __future__ import annotations

import math

SIGNIFICANT_DIGITS = 6

# Worst relative disagreement observed across the three platforms probed.
# Kept here so the margin argument above can be re-checked in a test.
MEASURED_NOISE_FLOOR_REL = 9.494e-14


def round_significant(value: float, digits: int = SIGNIFICANT_DIGITS) -> float:
    """Round to `digits` significant digits, scale-free.

    Significant digits rather than decimal places because these outputs span
    1e-3 (p-values) to 1e2 (percentage-point predictions); a fixed number of
    decimals would over-round one end and under-round the other.
    """
    if value == 0.0:
        return 0.0  # collapses -0.0, which json would otherwise write as "-0.0"
    if not math.isfinite(value):
        return value  # NaN/inf are not reproducible anyway; left for the caller to catch
    exponent = math.floor(math.log10(abs(value)))
    return round(value, digits - 1 - exponent) + 0.0


def canonicalise(obj, digits: int = SIGNIFICANT_DIGITS):
    """Recursively round every float in a JSON-shaped structure.

    Ints and bools are returned untouched -- counts and flags are exact and
    must not be perturbed. Mappings preserve insertion order.
    """
    if isinstance(obj, bool) or isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return round_significant(obj, digits)
    if isinstance(obj, dict):
        return {k: canonicalise(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [canonicalise(v, digits) for v in obj]
    # numpy scalars expose .item(); anything else passes through unchanged
    item = getattr(obj, "item", None)
    if callable(item):
        converted = item()
        if isinstance(converted, float):
            return round_significant(converted, digits)
        if isinstance(converted, (int, bool)):
            return converted
    return obj
