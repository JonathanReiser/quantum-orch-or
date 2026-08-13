# Quantum Orch-OR Simulation package
from .physics import (
    calculate_single_tubulin_eg,
    calculate_collapse_time,
    calculate_coherence_metric,
    scale_gravitational_energy,
    G_CONSTANT,
    HBAR,
    TUBULIN_MASS,
    DISPLACEMENT_DISTANCE
)
from .circuit import (
    create_initial_state_circuit,
    append_trotter_step,
    build_full_evolution_circuit
)
from .simulation import QuantumOrchORSimulation
from .visualize import plot_simulation_results
