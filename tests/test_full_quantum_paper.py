"""
tests/test_full_quantum_paper.py — Unit tests for RevTeX 4.2 full paper generator.
"""

import os
import pytest
from full_quantum_paper_generator import compile_full_paper

def test_full_tex_file_exists():
    tex_path = "full_quantum_governance_paper.tex"
    assert os.path.exists(tex_path)
    content = open(tex_path).read()
    assert "\\documentclass" in content
    assert "Lindblad Master Equation" in content
    assert "Penrose Gravitational Objective Reduction" in content
    assert "GHZ Entanglement Consensus Theorem" in content
    assert "835,000 Snapshot DAO" in content

def test_compile_full_paper(tmp_path):
    out_dir = str(tmp_path / "arxiv_full_build")
    tarball = compile_full_paper(tex_path="full_quantum_governance_paper.tex", output_dir=out_dir)
    assert os.path.exists(tarball)
