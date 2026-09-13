import numpy as np

from quantum_orch_or.cognitive_lindblad import simulate


def test_stress_accelerates_coherence_loss():
    calm = simulate(0.05, mindfulness_at_s=None)
    stress = simulate(0.70, mindfulness_at_s=None)
    assert stress.coherence_l1[-1] < calm.coherence_l1[-1]


def test_density_matrices_remain_physical():
    result = simulate(0.70)
    assert np.allclose(np.trace(result.density_matrices, axis1=1, axis2=2), 1.0, atol=1e-7)
    for rho in result.density_matrices:
        assert np.min(np.linalg.eigvalsh(rho)) >= -1e-7
    assert np.all((result.purity >= 0.5 - 1e-7) & (result.purity <= 1.0 + 1e-7))

