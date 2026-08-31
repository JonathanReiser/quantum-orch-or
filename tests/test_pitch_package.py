"""
tests/test_pitch_package.py — Unit tests for Pitch Deck & Grant Proposal exporter.
"""

import os
import pytest
from generate_pitch_package import export_pitch_package

def test_pitch_documents_exist():
    assert os.path.exists("WEB3_QUANTUM_AI_PROTOCOL_PITCH.md")
    assert os.path.exists("uniswap_grant_proposal.md")

    pitch_content = open("WEB3_QUANTUM_AI_PROTOCOL_PITCH.md").read()
    assert "On-Chain Quantum AI Governance" in pitch_content
    assert "Q_AIGovernanceHook.sol" in pitch_content
    # The pitch deck still contains the retracted "835,000 Snapshot DAO votes"
    # figure, so it must carry the retraction banner. Asserting the banner —
    # rather than the marketing string, as this test used to — means the test
    # fails if the correction is ever dropped. See CORRECTIONS.md.
    assert "RETRACTED CLAIMS" in pitch_content
    assert "CORRECTIONS.md" in pitch_content

    grant_content = open("uniswap_grant_proposal.md").read()
    assert "Uniswap Foundation Grant Application" in grant_content
    assert "$100,000 USD" in grant_content

def test_export_pitch_package():
    res = export_pitch_package()
    assert res is True
