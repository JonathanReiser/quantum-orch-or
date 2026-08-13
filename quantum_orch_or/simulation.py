import numpy as np
from qiskit import transpile, QuantumCircuit
from qiskit_aer import AerSimulator
from .physics import (
    calculate_single_tubulin_eg,
    calculate_coherence_metric,
    scale_gravitational_energy,
    HBAR
)
from .circuit import (
    build_full_evolution_circuit,
    create_initial_state_circuit,
    append_trotter_step
)

class QuantumOrchORSimulation:
    def __init__(self, num_qubits=4, J_coupling=1.0e-3, g_tunneling=5.0e-4, dt=1.0e-3, total_steps=100, initial_state="superposition", eg_scaling=1.0):
        """
        Initializes the Orch-OR simulation.
        
        Parameters:
        - num_qubits: Number of tubulins in the chain (qubits)
        - J_coupling: Dipole-dipole coupling constant (in arbitrary or scaled physics units)
        - g_tunneling: Quantum tunneling rate (transverse field strength)
        - dt: Time step size (seconds)
        - total_steps: Total number of time steps to run
        - initial_state: The starting quantum state ('ground', 'superposition', 'ghz')
        - eg_scaling: A scaling factor applied to E_G (useful for forcing collapses in small qubit toys)
        """
        self.num_qubits = num_qubits
        self.J_coupling = J_coupling
        self.g_tunneling = g_tunneling
        self.dt = dt
        self.total_steps = total_steps
        self.initial_state_type = initial_state
        
        # Calculate base physical parameters
        self.single_eg = calculate_single_tubulin_eg() * eg_scaling
        
        # Results storage
        self.time_axis = []
        self.energies = []
        self.coherences = []
        self.accumulated_actions = []
        self.collapse_events = []  # List of step indices where collapse occurred
        self.qubit_probabilities = []  # List of dicts or arrays storing p(|1>) for each qubit
        self.active_state_names = []  # State of the system at each step
        
        self.simulator = AerSimulator()

    def run_statevector_simulation(self):
        """
        Runs the simulation using statevector tracking.
        This represents the continuous quantum evolution of the system.
        When the Penrose threshold is reached, we probabilistically collapse the state.
        """
        print(f"Starting Statevector Orch-OR Simulation...")
        print(f"Number of qubits: {self.num_qubits}")
        print(f"Base Single Dimer E_G: {self.single_eg:.4e} J")
        print(f"HBAR constant: {HBAR:.4e} J·s")
        print(f"Penrose threshold (Action limit): {HBAR:.4e}")
        
        # Initialize the system state
        # We start with the chosen initial state type
        current_state_qc = create_initial_state_circuit(self.num_qubits, self.initial_state_type)
        current_state_qc.save_statevector()
        
        # Compile and run to get the initial statevector
        t_qc = transpile(current_state_qc, self.simulator)
        result = self.simulator.run(t_qc).result()
        current_statevector = np.array(result.get_statevector(t_qc))
        
        accumulated_action = 0.0
        
        for step in range(self.total_steps):
            current_time = step * self.dt
            self.time_axis.append(current_time)
            
            # 1. Compute coherence metric and Z-expectations from the current statevector
            coherence_weight, c_matrix = calculate_coherence_metric(current_statevector, self.num_qubits)
            inst_eg = scale_gravitational_energy(self.single_eg, coherence_weight)
            
            # Store data
            self.coherences.append(coherence_weight)
            self.energies.append(inst_eg)
            
            # Calculate individual qubit excited state (|1>) probabilities
            qubit_probs = []
            for q in range(self.num_qubits):
                prob_1 = 0.0
                for idx in range(len(current_statevector)):
                    if (idx >> q) & 1:
                        prob_1 += np.abs(current_statevector[idx]) ** 2
                qubit_probs.append(prob_1)
            self.qubit_probabilities.append(qubit_probs)
            
            # 2. Accumulate action: Action = Energy * dt
            # Using simple rectangular integration
            step_action = inst_eg * self.dt
            accumulated_action += step_action
            self.accumulated_actions.append(accumulated_action)
            
            # 3. Check for Penrose collapse (Objective Reduction)
            if accumulated_action >= HBAR:
                print(f"Collapse triggered at step {step} (t = {current_time:.4f} s)!")
                self.collapse_events.append(step)
                
                # Probabilistic collapse of the statevector:
                # Sample a basis state from the statevector probabilities
                probs = np.abs(current_statevector) ** 2
                # Normalize probabilities to protect against numerical drift
                probs /= np.sum(probs)
                
                collapsed_idx = np.random.choice(len(current_statevector), p=probs)
                
                # Reset statevector to the collapsed classical state (basis state)
                new_statevector = np.zeros_like(current_statevector)
                new_statevector[collapsed_idx] = 1.0
                current_statevector = new_statevector
                
                # Format collapsed state as binary string for logging
                bin_str = format(collapsed_idx, f'0{self.num_qubits}b')
                print(f"State collapsed to classical basis state: |{bin_str}>")
                
                # Reset accumulated action
                accumulated_action = 0.0
                
            # 4. Evolve statevector by one Trotter step
            # Create a circuit starting from the current statevector and applying one Trotter step
            qc_step = QuantumCircuit(self.num_qubits)
            qc_step.initialize(current_statevector, range(self.num_qubits))
            append_trotter_step(qc_step, self.num_qubits, self.J_coupling, self.g_tunneling, self.dt)
            qc_step.save_statevector()
            
            t_qc = transpile(qc_step, self.simulator)
            result = self.simulator.run(t_qc).result()
            current_statevector = np.array(result.get_statevector(t_qc))
            
        print("Simulation complete.")
        return {
            "time": self.time_axis,
            "coherence": self.coherences,
            "energy": self.energies,
            "action": self.accumulated_actions,
            "collapses": self.collapse_events,
            "probabilities": self.qubit_probabilities
        }
        
    def generate_qiskit_hardware_circuit(self):
        """
        Generates a single, full Qiskit circuit with mid-circuit measurements and resets
        representing the pre-calculated collapse trajectory. This circuit is ready to be
        run on real quantum hardware.
        """
        # First run the statevector simulation locally to find when collapses happen
        if not self.collapse_events:
            self.run_statevector_simulation()
            
        from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
        
        qr = QuantumRegister(self.num_qubits, 'q')
        # We need a classical register for each collapse event
        circuits = []
        
        qc = QuantumCircuit(qr)
        # Prepare initial state
        init_qc = create_initial_state_circuit(self.num_qubits, self.initial_state_type)
        qc.compose(init_qc, qubits=qr, inplace=True)
        
        last_step = 0
        collapse_count = 0
        
        for step in range(self.total_steps):
            # Apply Trotter step
            append_trotter_step(qc, self.num_qubits, self.J_coupling, self.g_tunneling, self.dt)
            
            if step in self.collapse_events:
                collapse_count += 1
                cr = ClassicalRegister(self.num_qubits, f'collapse_{collapse_count}')
                qc.add_register(cr)
                qc.barrier()
                qc.measure(qr, cr)
                # Reset to classical state after collapse
                for q in range(self.num_qubits):
                    qc.reset(qr[q])
                qc.barrier()
                
        # Final measurement
        cr_final = ClassicalRegister(self.num_qubits, 'final_state')
        qc.add_register(cr_final)
        qc.measure(qr, cr_final)
        
        return qc
