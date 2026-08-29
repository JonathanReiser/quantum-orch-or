"""
tests/test_q_ai_giving_portal.py — Unit tests for Base L2 Q-Giving Philanthropy Portal.
"""

import pytest
from q_ai_governance.q_ai_giving_portal import QGivingPortal

def test_q_ai_giving_portal_approval():
    portal = QGivingPortal()
    res = portal.audit_giving_grant("Red Cross Disaster Relief", 50000, donor_votes_yes=900, donor_votes_no=100)
    assert res["nonprofit_name"] == "Red Cross Disaster Relief"
    assert res["quantum_impact_metrics"]["quantum_impact_score"] >= 0.80
    assert res["base_l2_execution"] is True
    assert len(res["qiskit_impact_hash"]) == 64

def test_q_ai_giving_portal_rejection():
    portal = QGivingPortal()
    res = portal.audit_giving_grant("Opaque Overhead Charity", 10000, donor_votes_yes=300, donor_votes_no=700)
    assert res["quantum_impact_metrics"]["quantum_impact_score"] < 0.80
    assert res["base_l2_execution"] is False
