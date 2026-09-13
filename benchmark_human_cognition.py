"""Compatibility shim; use :mod:`q_ai_governance.benchmark_human_cognition`."""
from q_ai_governance.benchmark_human_cognition import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.benchmark_human_cognition", run_name="__main__")
