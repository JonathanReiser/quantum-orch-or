"""Compatibility shim; use :mod:`q_ai_governance.ibm_quantum_backend`."""
from q_ai_governance.ibm_quantum_backend import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.ibm_quantum_backend", run_name="__main__")
