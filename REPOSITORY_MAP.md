# Repository map

This repository preserves historical paths so published links and imports keep
working. New code must use the canonical locations below.

## Canonical source

| Path | Purpose | Status |
| --- | --- | --- |
| `q_ai_governance/` | Governance experiments and the published Python package | Maintained |
| `quantum_orch_or/` | Quantum/open-system research simulations and somatic bridge | Maintained research code |
| `contracts/` | Solidity commitments and governance prototypes | Experimental; audit before deployment |
| `tests/` | Automated tests for both Python packages and compatibility paths | Maintained |
| `data/` | Versioned inputs and result manifests | Preserve with provenance |
| `tools/ledger/` | Reproducibility ledger and checks | Maintained |

## Evidence and interpretation

| Path | Purpose |
| --- | --- |
| `CORRECTIONS.md` | Authoritative correction of unsupported historical claims |
| `VERIFICATION_THEATER.md` | Failure-mode analysis |
| `CONTESTEDNESS.md`, `EWL_EQUILIBRIUM.md` | Current focused research notes |
| Other root `.md`, `.pdf`, and `.tex` files | Historical publications retained so citations do not break; correction notices govern where claims conflict |

## Compatibility policy

Several root-level Python modules duplicate modules in `q_ai_governance/`.
Their paths are retained as thin compatibility shims. New imports must use the
package path, for example:

```python
from q_ai_governance.quantum_agent import QuantumOrchORAgent
```

Do not add new root-level Python modules. A compatibility path may be removed
only in a documented major release after downstream users have had a migration
window.

## Somatic research pipeline

The new files belong here:

```text
quantum_orch_or/somatic_bridge.py       wearable window -> motion-qualified RMSSD -> gamma
quantum_orch_or/cognitive_lindblad.py   gamma -> one-qubit density-matrix trajectory
contracts/SomaticValidation.sol         append-only salted commitments
tests/test_somatic_bridge.py
tests/test_cognitive_lindblad.py
```

The quantum-cognitive layer is a mathematical analogy. It is not evidence that
cognition is quantum and it is not a medical device.

