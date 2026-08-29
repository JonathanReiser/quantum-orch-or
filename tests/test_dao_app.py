"""
tests/test_dao_app.py — Unit tests for DAO Treasury Security Portal dao_app.py.
"""

import os
import pytest

def test_dao_app_file_exists():
    assert os.path.exists("dao_app.py")
    content = open("dao_app.py").read()
    assert "Q-AI B2B DAO Treasury Security Audit Portal" in content
    assert "DAOSecurityOracle" in content
    assert "streamlit" in content
