"""Compatibility shim; use :mod:`q_ai_governance.snapshot_live_oracle`."""
from q_ai_governance.snapshot_live_oracle import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.snapshot_live_oracle", run_name="__main__")
