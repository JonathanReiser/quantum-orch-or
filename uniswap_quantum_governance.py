"""Compatibility shim; use :mod:`q_ai_governance.uniswap_quantum_governance`."""
from q_ai_governance.uniswap_quantum_governance import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.uniswap_quantum_governance", run_name="__main__")
