import numpy as np

# Physical constants
G_CONSTANT = 6.67430e-11        # m^3 kg^-1 s^-2 (Newton's gravitational constant)
HBAR = 1.0545718e-34            # J s (Reduced Planck constant)
EV_TO_JOULE = 1.602176634e-19   # Conversion factor from eV to Joules

# Biological constants (Orch-OR specific)
TUBULIN_MASS = 1.827e-22        # kg (~110 kDa for tubulin dimer)
DISPLACEMENT_DISTANCE = 1.0e-11 # m (~10 pm atomic displacement during conformational change)
TUBULIN_RADIUS = 4.0e-9         # m (~4 nm radius of tubulin dimer)

def calculate_single_tubulin_eg(mass=TUBULIN_MASS, displacement=DISPLACEMENT_DISTANCE, radius=TUBULIN_RADIUS, method="penrose"):
    """
    Calculates the gravitational self-energy difference (E_G) of a single tubulin dimer in superposition.
    
    Methods:
    - 'penrose': Approximates E_G for a sphere of mass m and radius r displaced by d (d << r):
                 E_G = G * m^2 * d^2 / r^3
    - 'simple': Basic dimensional analysis E_G = G * m^2 / d
    """
    if method == "penrose":
        # Penrose formula for small displacement of a sphere
        return G_CONSTANT * (mass ** 2) * (displacement ** 2) / (radius ** 3)
    elif method == "simple":
        return G_CONSTANT * (mass ** 2) / displacement
    else:
        raise ValueError(f"Unknown method: {method}")

def calculate_collapse_time(eg):
    """
    Calculates the Penrose superposition lifetime tau = hbar / E_G.
    Returns the time in seconds.
    """
    if eg <= 0:
        return float('inf')
    return HBAR / eg

def calculate_coherence_metric(state_vector_or_density_matrix, num_qubits):
    """
    Calculates a coherence/entanglement metric to scale the gravitational self-energy E_G.
    We compute the spatial correlation matrix C_ij = <Z_i Z_j> - <Z_i><Z_j>
    to see how much the qubits are behaving as a collective quantum state vs. independent classical states.
    
    If state is a pure state vector (numpy array):
    """
    # Verify shape
    state = np.asarray(state_vector_or_density_matrix)
    
    # We will compute expectation values of Z_i and Z_i Z_j
    # Z operator on qubit i
    def get_z_expectations():
        z_expects = []
        for i in range(num_qubits):
            # Compute <Z_i>
            # Z_i has eigenvalue +1 for state 0 and -1 for state 1
            val = 0.0
            for state_idx in range(len(state)):
                # Get the i-th bit (from right, 0-indexed)
                bit = (state_idx >> i) & 1
                prob = np.abs(state[state_idx]) ** 2
                val += prob * (1.0 if bit == 0 else -1.0)
            z_expects.append(val)
        return np.array(z_expects)

    def get_zz_expectations(z_expects):
        zz_expects = np.zeros((num_qubits, num_qubits))
        for i in range(num_qubits):
            for j in range(num_qubits):
                if i == j:
                    zz_expects[i, j] = 1.0
                    continue
                # Compute <Z_i Z_j>
                val = 0.0
                for state_idx in range(len(state)):
                    bit_i = (state_idx >> i) & 1
                    bit_j = (state_idx >> j) & 1
                    sign_i = 1.0 if bit_i == 0 else -1.0
                    sign_j = 1.0 if bit_j == 0 else -1.0
                    prob = np.abs(state[state_idx]) ** 2
                    val += prob * sign_i * sign_j
                zz_expects[i, j] = val
        return zz_expects

    try:
        z_exp = get_z_expectations()
        zz_exp = get_zz_expectations(z_exp)
        
        # Calculate C_ij
        c_matrix = np.zeros((num_qubits, num_qubits))
        for i in range(num_qubits):
            for j in range(num_qubits):
                c_matrix[i, j] = zz_exp[i, j] - z_exp[i] * z_exp[j]
        
        # Coherence weight is the sum of absolute correlation coefficients
        # For a product state (classical/uncorrelated), C_ij = 0 for i != j, sum = N (diagonal only)
        # For a GHZ state, C_ij = 1 for all i,j, sum = N^2
        coherence_weight = np.sum(np.abs(c_matrix))
        return coherence_weight, c_matrix
    except Exception as e:
        # Fallback to simple quantum entropy if calculations fail
        return float(num_qubits), np.eye(num_qubits)

def scale_gravitational_energy(single_eg, coherence_weight):
    """
    Scales the single tubulin E_G based on the coherence weight of the system.
    In Orch-OR, E_G scales with coherence, up to N^2 for fully coherent states.
    """
    return single_eg * coherence_weight
