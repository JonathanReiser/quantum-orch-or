import pytest
import numpy as np
from governance_integration import QuantumGovernanceSimulation, GovernanceProposal

def test_governance_proposal_creation():
    sim = QuantumGovernanceSimulation(num_voters=4, entangled_consensus=False)
    prop = sim.generate_quantum_proposal(1)
    
    assert prop.proposal_id == 1
    assert "Proposal-01" in prop.title
    assert len(prop.impact_vector) == 2
    assert prop.impact_vector[0] > 0.0

def test_ghz_entangled_voting_state():
    sim = QuantumGovernanceSimulation(num_voters=3, entangled_consensus=True)
    ghz_sv = sim.create_ghz_entangled_voting_state()
    
    assert len(ghz_sv) == 8  # 2^3
    assert np.isclose(np.abs(ghz_sv[0]) ** 2, 0.5)
    assert np.isclose(np.abs(ghz_sv[7]) ** 2, 0.5)

def test_proposal_voting_run():
    sim = QuantumGovernanceSimulation(num_voters=4, entangled_consensus=True)
    prop = GovernanceProposal(1, "Test Proposal", [4.0, 2.0])
    
    votes, passed, latency, consensus = sim.run_proposal_vote(prop)
    
    assert len(votes) == 4
    assert isinstance(passed, bool)
    assert latency > 0.0
    assert 0.5 <= consensus <= 1.0

def test_full_governance_simulation():
    sim = QuantumGovernanceSimulation(num_voters=4, entangled_consensus=True)
    res = sim.run_simulation(total_proposals=3)
    
    assert res["total"] == 3
    assert 0 <= res["passed"] <= 3
    assert len(res["consensus"]) == 3
    assert len(res["latency"]) == 3
