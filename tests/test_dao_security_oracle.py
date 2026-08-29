"""
tests/test_dao_security_oracle.py — Unit tests for B2B DAO Security Oracle.
"""

import pytest
from q_ai_governance.dao_security_oracle import DAOSecurityOracle

def test_dao_security_oracle_approval():
    oracle = DAOSecurityOracle(dao_name="Uniswap DAO")
    cert = oracle.audit_proposal(
        proposal_id="UNI-PROP-42",
        yes_votes=550000,
        no_votes=450000,
        category="Public Goods"
    )
    assert cert["dao_name"] == "Uniswap DAO"
    assert cert["proposal_id"] == "UNI-PROP-42"
    assert cert["quantum_audit_metrics"]["quantum_consensus_score"] >= 0.80
    assert cert["smart_contract_execution"] is True
    assert len(cert["qiskit_proof_hash"]) == 64

def test_dao_security_oracle_rejection():
    oracle = DAOSecurityOracle(dao_name="Whale DAO")
    cert = oracle.audit_proposal(
        proposal_id="WHALE-PROP-01",
        yes_votes=100000,
        no_votes=900000,
        category="Selfish Extraction"
    )
    assert cert["quantum_audit_metrics"]["quantum_consensus_score"] < 0.80
    assert cert["smart_contract_execution"] is False
