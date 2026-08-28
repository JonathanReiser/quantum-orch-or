import pytest
import os
import json
from benchmark_real_dao_data import RealDAOBenchmarkRunner, REAL_DAO_HISTORICAL_DATA

def test_real_dao_benchmark_execution():
    runner = RealDAOBenchmarkRunner()
    summary = runner.run_benchmark()
    
    assert summary["proposals_count"] == len(REAL_DAO_HISTORICAL_DATA)
    assert 0.0 <= summary["q_ai_mae"] <= 1.0
    assert 0.0 <= summary["q_ai_r2_score"] <= 1.0
    assert len(summary["proposals"]) == len(REAL_DAO_HISTORICAL_DATA)

def test_real_dao_benchmark_plot_and_json(tmp_path):
    json_path = os.path.join(tmp_path, "benchmark.json")
    plot_path = os.path.join(tmp_path, "benchmark.png")
    
    runner = RealDAOBenchmarkRunner()
    summary = runner.run_benchmark()
    
    runner.generate_benchmark_plot(summary, output_plot=str(plot_path))
    with open(str(json_path), "w") as f:
        json.dump(summary, f, indent=2)
        
    assert os.path.exists(json_path)
    assert os.path.exists(plot_path)
