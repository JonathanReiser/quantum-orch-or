"""
tests/test_uniswap_v4_hook.py — Unit tests for Uniswap v4 Hook & Oracle.
"""

import os
import pytest
from q_ai_governance.uniswap_v4_hook_oracle import UniswapV4HookOracle

def test_solidity_contract_exists():
    sol_path = "contracts/Q_AIGovernanceHook.sol"
    assert os.path.exists(sol_path)
    content = open(sol_path).read()
    assert "contract Q_AIGovernanceHook" in content
    assert "MIN_CONSENSUS_THRESHOLD = 8000" in content
    assert "submitQuantumConsensusProof" in content
    assert "verifyAndExecuteTreasuryAllocation" in content

def test_generate_proof_payload():
    oracle = UniswapV4HookOracle()
    payload = oracle.generate_proof_payload(proposal_id=42, consensus_score=8700)
    assert payload["params"]["proposalId"] == 42
    assert payload["params"]["consensusScore"] == 8700
    assert payload["params"]["qiskitProofHash"].startswith("0x")

def test_generate_hook_deployment_summary(tmp_path):
    out_json = str(tmp_path / "test_hook.json")
    oracle = UniswapV4HookOracle()
    payload = oracle.generate_hook_deployment_summary(output_json=out_json)
    assert os.path.exists(out_json)
    assert payload["status"] == "READY_FOR_EVM_BROADCAST"
