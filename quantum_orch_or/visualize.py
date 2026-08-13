import matplotlib.pyplot as plt
import numpy as np
from .physics import HBAR

def plot_simulation_results(results, num_qubits, save_path=None):
    """
    Plots the results of the Orch-OR simulation.
    
    Creates a 3-panel figure:
    1. Qubit State Probabilities (P(|1>) for each tubulin)
    2. System Coherence Weight (measure of entanglement/coherence)
    3. Accumulated Action vs. Penrose Threshold (HBAR)
    """
    time = np.array(results["time"])
    coherence = np.array(results["coherence"])
    energy = np.array(results["energy"])
    action = np.array(results["action"])
    collapses = np.array(results["collapses"])
    probs = np.array(results["probabilities"]) # shape: (steps, num_qubits)
    
    # Setup styling (dark mode friendly / professional styling)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Determine times of collapse events
    collapse_times = time[collapses] if len(collapses) > 0 else []
    
    # ----------------------------------------------------
    # Panel 1: Qubit Probabilities (Excitation States of Tubulins)
    # ----------------------------------------------------
    ax = axes[0]
    for q in range(num_qubits):
        ax.plot(time, probs[:, q], label=f"Tubulin {q+1}", alpha=0.8, linewidth=2)
    
    # Highlight collapse events with vertical lines
    for t_col in collapse_times:
        ax.axvline(x=t_col, color='crimson', linestyle='--', linewidth=1.5, alpha=0.9,
                   label="Objective Reduction (OR)" if t_col == collapse_times[0] else "")
        
    ax.set_ylabel("Probability of state $|1\\rangle$ (Beta)", fontsize=11)
    ax.set_title("Tubulin Dimers Conformation Evolution", fontsize=13, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", frameon=True, shadow=True)
    
    # ----------------------------------------------------
    # Panel 2: Quantum Coherence / Entanglement Weight
    # ----------------------------------------------------
    ax = axes[1]
    ax.plot(time, coherence, color="darkviolet", linewidth=2.5, label="Coherence Weight ($W_c$)")
    
    for t_col in collapse_times:
        ax.axvline(x=t_col, color='crimson', linestyle='--', linewidth=1.5, alpha=0.9)
        
    ax.set_ylabel("Coherence Weight", fontsize=11)
    ax.set_title("Quantum Coherence Weight (Mass Coherence Scale)", fontsize=13, fontweight='bold')
    # Theoretical limits: product state is num_qubits, fully coherent state is num_qubits^2
    ax.set_ylim(0, max(num_qubits**2 + 1, np.max(coherence) * 1.2))
    ax.legend(loc="upper right", frameon=True, shadow=True)
    
    # ----------------------------------------------------
    # Panel 3: Accumulated Action vs Penrose Threshold
    # ----------------------------------------------------
    ax = axes[2]
    # Scale action and HBAR to eV·s for readable labels
    ev_scale = 1.602176634e-19
    action_ev = action / ev_scale
    hbar_ev = HBAR / ev_scale
    
    ax.plot(time, action_ev, color="royalblue", linewidth=2.5, label=r"Accumulated Action $\int E_G dt$")
    ax.axhline(y=hbar_ev, color="darkorange", linestyle="-.", linewidth=2, 
               label="Penrose Threshold $\\hbar$")
    
    for t_col in collapse_times:
        ax.axvline(x=t_col, color='crimson', linestyle='--', linewidth=1.5, alpha=0.9)
        
    ax.set_xlabel("Time (seconds)", fontsize=12)
    ax.set_ylabel("Action ($eV \\cdot s$)", fontsize=11)
    ax.set_title("Penrose Threshold Evolution (Objective Reduction Meter)", fontsize=13, fontweight='bold')
    ax.legend(loc="upper left", frameon=True, shadow=True)
    
    # Adjust layout and show/save
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Results plot saved to {save_path}")
    else:
        plt.show()
    plt.close()
