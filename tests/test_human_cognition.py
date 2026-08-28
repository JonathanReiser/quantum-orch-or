import pytest
import numpy as np
from benchmark_human_cognition import (
    ConjunctionFallacyBenchmark,
    QuestionOrderEffectBenchmark,
    SpeedDatingOrderEffectBenchmark
)

def test_conjunction_fallacy_benchmark():
    bm = ConjunctionFallacyBenchmark()
    res = bm.evaluate_models()
    
    assert res["human_rate"] == 0.85
    assert res["classical_rate"] == 0.0
    assert res["quantum_rate"] > 0.5
    assert res["mae_quantum"] < res["mae_classical"]

def test_question_order_effect_benchmark():
    bm = QuestionOrderEffectBenchmark()
    res = bm.evaluate_models()
    
    # QQ Equality check: q_YY + q_NN = p_YY + p_NN
    assert np.isclose(res["qq_lhs"], res["qq_rhs"], atol=1e-3)
    assert res["quantum_qq_error"] < 1e-3
    assert res["r2_quantum"] > res["r2_classical"]

def test_speed_dating_order_effect_benchmark():
    bm = SpeedDatingOrderEffectBenchmark()
    res = bm.evaluate_models()
    
    assert res["quantum_shift"] > 0.0
    assert res["mae_quantum"] < res["mae_classical"]
