import pytest
import os
import json
from dao_budget_allocator import DAOBudgetAllocator, Proposal, sample_proposals

def test_dao_proposal_creation():
    prop = Proposal("P1", "Audit", 100000, 9.0, 8.5)
    assert prop.proposal_id == "P1"
    assert prop.requested_amount == 100000.0
    assert prop.public_good_score == 9.0

def test_dao_budget_allocation():
    allocator = DAOBudgetAllocator(total_budget=500000.0)
    props = sample_proposals()
    report = allocator.allocate_budget(props)
    
    assert report["total_budget"] == 500000.0
    assert report["total_allocated"] <= 500000.0
    assert len(report["proposals"]) == len(props)
    assert 50.0 <= report["consensus_score"] <= 100.0

def test_dao_report_file_generation(tmp_path):
    json_path = os.path.join(tmp_path, "report.json")
    plot_path = os.path.join(tmp_path, "plot.png")
    
    allocator = DAOBudgetAllocator(total_budget=1000000.0)
    props = sample_proposals()
    report = allocator.allocate_budget(props)
    
    allocator.generate_report_file(report, output_json=str(json_path), output_plot=str(plot_path))
    
    assert os.path.exists(json_path)
    assert os.path.exists(plot_path)
    
    with open(json_path, "r") as f:
        data = json.load(f)
        assert data["total_budget"] == 1000000.0
