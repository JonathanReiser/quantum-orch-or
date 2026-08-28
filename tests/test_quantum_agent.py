import pytest
import numpy as np
from quantum_agent import QuantumPrisonerDilemmaEnv, QuantumOrchORAgent

def test_quantum_environment():
    env = QuantumPrisonerDilemmaEnv(opponent_strategy="always_cooperate")
    obs = env.reset()
    assert len(obs) == 2
    
    # Action 0 (Cooperate) against Cooperate -> Payoff 3.0
    next_obs, reward, done, info = env.step(0)
    assert reward == 3.0
    assert info["agent_action"] == 0
    assert info["opponent_action"] == 0
    
    # Action 1 (Defect) against Cooperate -> Payoff 5.0
    next_obs, reward, done, info = env.step(1)
    assert reward == 5.0
    assert info["agent_action"] == 1

def test_quantum_agent_deliberation():
    agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)
    obs = np.array([0.0, 0.0], dtype=np.float32)
    
    action_idx, steps, coherence, log_prob, rotations = agent.deliberate_and_act(obs, max_steps=20)
    
    assert 0 <= action_idx < (2 ** 2)
    assert 1 <= steps <= 20
    assert coherence > 0.0
    assert isinstance(log_prob, float)
    assert len(rotations) == 4

def test_quantum_agent_policy_update():
    agent = QuantumOrchORAgent(num_qubits=2, state_dim=2, learning_rate=0.1)
    obs = np.array([1.0, 0.0], dtype=np.float32)
    
    initial_weights = agent.weights.copy()
    action_idx, steps, coherence, log_prob, rotations = agent.deliberate_and_act(obs, max_steps=10)
    
    agent.update_policy(reward=5.0, state_obs=obs, log_prob=log_prob, rotations=rotations)
    
    assert not np.array_equal(initial_weights, agent.weights)
