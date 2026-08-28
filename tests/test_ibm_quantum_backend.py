import pytest
from ibm_quantum_backend import IBMQuantumBackendConnector

def test_ibm_quantum_connector_fallback():
    connector = IBMQuantumBackendConnector(api_token=None)
    res = connector.execute_quantum_deliberation(theta=0.5, phi=0.8, shots=100)
    
    assert res["using_real_hardware"] == False
    assert "AerSimulator" in res["backend_used"]
    assert res["shots"] == 100
    assert "00" in res["state_probabilities"]
    assert sum(res["state_probabilities"].values()) == pytest.approx(1.0, abs=0.01)
