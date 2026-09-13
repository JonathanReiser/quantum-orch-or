"""Shared fixtures for the compatibility-shim tests.

Root ``app.py`` and ``dao_app.py`` are Streamlit scripts: importing them runs
the dashboard body. For ``app.py`` that includes a simulated market scan which
draws from the global numpy RNG and writes ``market_signals_report.json`` into
the working directory. Importing them inside the pytest process would therefore
leak state into unrelated tests — RNG position, ``sys.modules`` entries,
Streamlit's script-run state — and could shift the outcome of any later test
that samples.

So every import-and-behaviour check runs in a **subprocess** with its CWD set to
a ``tmp_path``. The pytest process never imports either module, and any file the
dashboard writes lands in the temporary directory. The probe reports back as
JSON written to a file rather than stdout, because the dashboards print
liberally.

Source-level checks (the file exists, the shim is a thin re-export, the title is
not pasted in) stay in-process: they only read text and have no side effects.
"""

import json
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The probe body takes its parameters from names injected above it, so no
# string formatting touches this code and no braces need escaping.
_PROBE = """
import importlib, json, os

import streamlit as st

_recorded = {"page_config": [], "titles": []}


def _fake_set_page_config(*args, **kwargs):
    _recorded["page_config"].append(kwargs)


def _fake_title(*args, **kwargs):
    if args:
        _recorded["titles"].append(args[0])


st.set_page_config = _fake_set_page_config
st.title = _fake_title

canonical = importlib.import_module(CANONICAL)
shim = importlib.import_module(SHIM)

public = sorted(n for n in vars(canonical) if not n.startswith("_"))
result = {
    "shim_module_name": shim.__name__,
    "shim_imported": True,
    "canonical_public": public,
    "missing_from_shim": sorted(set(public) - set(vars(shim))),
    "not_identical": [n for n in public
                      if vars(shim).get(n) is not vars(canonical).get(n)],
    "key_object_present": KEY in vars(shim),
    "key_object_identical": vars(shim).get(KEY) is vars(canonical).get(KEY),
    "page_config_titles": [kw.get("page_title") for kw in _recorded["page_config"]],
    "titles": _recorded["titles"],
    "files_written_to_cwd": sorted(os.listdir(".")),
}

with open(OUT, "w") as fh:
    json.dump(result, fh)
"""


@pytest.fixture(scope="session")
def shim_probe(tmp_path_factory):
    """Import a shim and its canonical module in an isolated subprocess.

    Session-scoped and cached per module: each probe pays the dashboard's
    import cost once, and no test in this process ever imports them.
    """
    cache = {}

    def _probe(shim_name, canonical_name, key_object):
        if shim_name in cache:
            return cache[shim_name]

        workdir = tmp_path_factory.mktemp(f"probe_{shim_name}")
        out_path = workdir / "probe_result.json"
        preamble = (
            f"CANONICAL = {canonical_name!r}\n"
            f"SHIM = {shim_name!r}\n"
            f"KEY = {key_object!r}\n"
            f"OUT = {str(out_path)!r}\n"
        )
        source = preamble + _PROBE

        env = dict(os.environ)
        env["PYTHONPATH"] = REPO_ROOT + os.pathsep + env.get("PYTHONPATH", "")
        env.setdefault("MPLBACKEND", "Agg")

        completed = subprocess.run(
            [sys.executable, "-c", source],
            cwd=str(workdir), env=env, capture_output=True, text=True, timeout=300,
        )
        assert completed.returncode == 0, (
            f"probe subprocess for {shim_name} failed\n"
            f"--- stderr ---\n{completed.stderr[-3000:]}")
        assert out_path.exists(), (
            f"probe wrote no result\n--- stdout ---\n{completed.stdout[-2000:]}")

        result = json.loads(out_path.read_text())
        result["_workdir"] = str(workdir)
        cache[shim_name] = result
        return result

    return _probe
