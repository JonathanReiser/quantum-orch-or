from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np

def create_initial_state_circuit(num_qubits, state_type="ground"):
    """
    Creates a circuit that prepares the initial state of the tubulin chain.
    
    States:
    - 'ground': All qubits in |0> (representing alpha conformation)
    - 'excited': All qubits in |1> (representing beta conformation)
    - 'superposition': All qubits in a uniform superposition |+> (Hadamard on each)
    - 'ghz': A fully entangled GHZ state (representing macro-coherence)
    """
    qr = QuantumRegister(num_qubits, 'q')
    qc = QuantumCircuit(qr)
    
    if state_type == "ground":
        # Do nothing, default state is |00...0>
        pass
    elif state_type == "excited":
        for i in range(num_qubits):
            qc.x(qr[i])
    elif state_type == "superposition":
        for i in range(num_qubits):
            qc.h(qr[i])
    elif state_type == "ghz":
        qc.h(qr[0])
        for i in range(num_qubits - 1):
            qc.cx(qr[i], qr[i+1])
    else:
        raise ValueError(f"Unknown state type: {state_type}")
        
    return qc

def append_trotter_step(circuit, num_qubits, J_coupling, g_tunneling, dt):
    """
    Appends a single Trotter step of time evolution under the transverse Ising model:
    H = -J * sum(Z_i * Z_{i+1}) - g * sum(X_i)
    
    Time evolution operator for step dt: U(dt) = e^(-i * H * dt)
    This is approximated as:
    U(dt) ≈ [prod_i e^(i * g * X_i * dt)] * [prod_i e^(i * J * Z_i * Z_{i+1} * dt)]
    
    In Qiskit:
    - rx(theta) implements e^(-i * theta * X / 2). 
      To get e^(i * g * X * dt), we set theta = -2 * g * dt.
    - rzz(theta) implements e^(-i * theta * Z_1 * Z_2 / 2). 
      To get e^(i * J * Z_1 * Z_2 * dt), we set theta = -2 * J * dt.
    """
    # 1. ZZ interactions (dipole-dipole coupling between adjacent tubulins)
    # Using a 1D chain topology (nearest neighbor)
    for i in range(num_qubits - 1):
        circuit.rzz(-2.0 * J_coupling * dt, i, i + 1)
        
    # 2. X rotations (transverse field / quantum tunneling)
    for i in range(num_qubits):
        circuit.rx(-2.0 * g_tunneling * dt, i)
        
    return circuit

def build_full_evolution_circuit(num_qubits, J_coupling, g_tunneling, dt, steps, initial_state="ground"):
    """
    Builds a full Qiskit circuit that prepares the initial state and evolves it for
    the specified number of Trotter steps.
    """
    # Create the initial state circuit
    qc = create_initial_state_circuit(num_qubits, state_type=initial_state)
    
    # Append the Trotter evolution steps
    for step in range(steps):
        append_trotter_step(qc, num_qubits, J_coupling, g_tunneling, dt)
        
    return qc

def build_mid_circuit_collapse_circuit(num_qubits, J_coupling, g_tunneling, dt, steps_before_collapse, initial_state="ground"):
    """
    Builds a circuit that evolves the state and adds mid-circuit measurements and resets.
    This simulates the physical collapse of the state vector when the Penrose threshold is crossed.
    """
    qr = QuantumRegister(num_qubits, 'q')
    cr = ClassicalRegister(num_qubits, 'c_collapse')
    qc = QuantumCircuit(qr, cr)
    
    # 1. Set up initial state
    init_qc = create_initial_state_circuit(num_qubits, state_type=initial_state)
    qc.compose(init_qc, qubits=qr, inplace=True)
    
    # 2. Evolve for steps_before_collapse
    for _ in range(steps_before_collapse):
        append_trotter_step(qc, num_qubits, J_coupling, g_tunneling, dt)
        
    # 3. Collapse (measure and reset to ground state |00...0>)
    qc.barrier()
    qc.measure(qr, cr)
    for i in range(num_qubits):
        qc.reset(qr[i])
    qc.barrier()
    
    return qc
