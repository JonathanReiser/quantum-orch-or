"""
tests/test_dashboard_app.py — Unit tests for Streamlit Web Dashboard app.py.
"""

import os
import pytest

def test_app_file_exists():
    assert os.path.exists("app.py")
    content = open("app.py").read()
    assert "Q-AI Quantum Market Phase Dashboard" in content
    assert "MarketPhaseCollapseBot" in content
    assert "streamlit" in content
