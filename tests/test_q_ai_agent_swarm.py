"""
tests/test_q_ai_agent_swarm.py — Unit tests for Enterprise Multi-Agent AI Swarm Engine.
"""

import pytest
from q_ai_governance.q_ai_agent_swarm import QAIAgentSwarm

def test_q_ai_agent_swarm_consensus():
    swarm = QAIAgentSwarm()
    res = swarm.evaluate_swarm_consensus("Supply Chain Routing", num_agents=5, agent_approval_probabilities=[0.85, 0.90, 0.88, 0.92, 0.80])
    assert res["task_name"] == "Supply Chain Routing"
    assert res["quantum_swarm_metrics"]["ghz_entangled_consensus_score"] >= 0.80
    assert res["autonomous_execution"] is True
    assert len(res["qiskit_swarm_hash"]) == 64

def test_q_ai_agent_swarm_gridlock():
    swarm = QAIAgentSwarm()
    res = swarm.evaluate_swarm_consensus("Conflicting Task", num_agents=3, agent_approval_probabilities=[0.30, 0.25, 0.40])
    assert res["quantum_swarm_metrics"]["ghz_entangled_consensus_score"] < 0.80
    assert res["autonomous_execution"] is False
