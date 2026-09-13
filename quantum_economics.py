"""Compatibility shim; use :mod:`q_ai_governance.quantum_economics`."""
from q_ai_governance.quantum_economics import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.quantum_economics", run_name="__main__")
