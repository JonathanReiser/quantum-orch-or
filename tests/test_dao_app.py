"""tests/test_dao_app.py — the root dao_app.py compatibility shim.

See tests/test_dashboard_app.py for why the previous source-scanning assertion
was replaced and why importing happens in a subprocess.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHIM_PATH = ROOT / "dao_app.py"
SHIM = "dao_app"
CANONICAL = "q_ai_governance.dao_app"
KEY_OBJECT = "DAOSecurityOracle"
DASHBOARD_TITLE = "Q-AI B2B DAO Treasury Security Audit Portal"


@pytest.fixture(scope="session")
def probe(shim_probe):
    return shim_probe(SHIM, CANONICAL, KEY_OBJECT)


# --- source-level checks: no import, no side effects -------------------------


def test_legacy_import_path_still_exists():
    assert SHIM_PATH.is_file(), "root dao_app.py is the documented legacy entry point"


def test_shim_is_a_thin_reexport_rather_than_a_copy():
    source = SHIM_PATH.read_text()
    assert CANONICAL in source
    assert "import *" in source
    assert "set_page_config" not in source, "shim should not contain the dashboard body"
    assert DASHBOARD_TITLE not in source, (
        "the portal title belongs to the canonical module; putting it in the shim "
        "would satisfy a source-scanning test without the shim doing anything")
    assert len(source.splitlines()) <= 5


# --- behaviour checks: run in an isolated subprocess -------------------------


def test_shim_imports_successfully(probe):
    assert probe["shim_imported"] is True
    assert probe["shim_module_name"] == SHIM


def test_shim_reexports_every_public_name_of_the_canonical_module(probe):
    assert probe["canonical_public"], (
        "canonical module exposes no public names; the check would be vacuous")
    assert not probe["missing_from_shim"], (
        f"shim does not re-export: {probe['missing_from_shim']}")


def test_reexported_objects_are_the_canonical_ones(probe):
    assert not probe["not_identical"], (
        f"re-exported but not the same object: {probe['not_identical']}")


def test_shim_reexports_the_security_oracle(probe):
    assert probe["key_object_present"], f"{KEY_OBJECT} missing from the shim"
    assert probe["key_object_identical"], f"{KEY_OBJECT} is not the canonical object"


def test_canonical_module_renders_the_audit_portal_title(probe):
    """Asserts the module actually calls st.title with the portal title."""
    assert DASHBOARD_TITLE in " ".join(probe["titles"]), probe["titles"]
