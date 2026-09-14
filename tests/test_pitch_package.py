"""
tests/test_pitch_package.py — Unit tests for Pitch Deck & Grant Proposal exporter.
"""

import os
import pytest
from generate_pitch_package import export_pitch_package

def test_pitch_documents_exist():
    pitch_path = "archive/historical-publications/WEB3_QUANTUM_AI_PROTOCOL_PITCH.md"
    grant_path = "archive/historical-publications/uniswap_grant_proposal.md"
    assert os.path.exists(pitch_path)
    assert os.path.exists(grant_path)

    pitch_content = open(pitch_path).read()
    assert "On-Chain Quantum AI Governance" in pitch_content
    assert "Q_AIGovernanceHook.sol" in pitch_content
    # The pitch deck still contains the retracted "835,000 Snapshot DAO votes"
    # figure, so it must carry the retraction banner. Asserting the banner —
    # rather than the marketing string, as this test used to — means the test
    # fails if the correction is ever dropped. See CORRECTIONS.md.
    assert "RETRACTED CLAIMS" in pitch_content
    assert "CORRECTIONS.md" in pitch_content

    grant_content = open(grant_path).read()
    assert "Uniswap Foundation Grant Application" in grant_content
    assert "$100,000 USD" in grant_content

def test_export_pitch_package(tmp_path):
    res = export_pitch_package(output_dir=str(tmp_path))
    assert res is True
    assert (tmp_path / "WEB3_QUANTUM_AI_PROTOCOL_PITCH.md").exists()
    assert (tmp_path / "uniswap_grant_proposal.md").exists()
