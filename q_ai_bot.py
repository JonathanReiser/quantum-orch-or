"""Compatibility shim; use :mod:`q_ai_governance.q_ai_bot`."""
from q_ai_governance.q_ai_bot import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.q_ai_bot", run_name="__main__")
