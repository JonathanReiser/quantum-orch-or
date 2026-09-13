"""Compatibility shim; use :mod:`q_ai_governance.crypto_recommendations`."""
from q_ai_governance.crypto_recommendations import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("q_ai_governance.crypto_recommendations", run_name="__main__")
