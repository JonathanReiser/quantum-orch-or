"""tests/test_dashboard_app.py — the root app.py compatibility shim.

The cleanup turned root ``app.py`` into a shim re-exporting
``q_ai_governance.app``. The previous test read the shim's source looking for the
dashboard's page title, so it failed the moment the body moved — it detected a
file move, not a defect.

These tests check what actually matters: the legacy path resolves, it exposes the
same objects as the canonical module, and the canonical module still configures
the dashboard. Importing is done in a subprocess (see conftest) because these
modules run application logic at import time.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHIM_PATH = ROOT / "app.py"
SHIM = "app"
CANONICAL = "q_ai_governance.app"
KEY_OBJECT = "MarketPhaseCollapseBot"
PAGE_TITLE = "Q-AI Quantum Market Phase Dashboard"


@pytest.fixture(scope="session")
def probe(shim_probe):
    return shim_probe(SHIM, CANONICAL, KEY_OBJECT)


# --- source-level checks: no import, no side effects -------------------------


def test_legacy_import_path_still_exists():
    assert SHIM_PATH.is_file(), "root app.py is the documented legacy entry point"


def test_shim_is_a_thin_reexport_rather_than_a_copy():
    """Guards the cleanup's intent. If the dashboard body — or just its title —
    is ever pasted back into the shim, including to satisfy a source-scanning
    test, this fails."""
    source = SHIM_PATH.read_text()
    assert CANONICAL in source
    assert "import *" in source
    assert "set_page_config" not in source, "shim should not contain the dashboard body"
    assert PAGE_TITLE not in source, (
        "the page title belongs to the canonical module; putting it in the shim "
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
    """Identity, not just presence — a shim that redefined its own copies would
    satisfy a name check while diverging in behaviour."""
    assert not probe["not_identical"], (
        f"re-exported but not the same object: {probe['not_identical']}")


def test_shim_reexports_the_market_bot(probe):
    assert probe["key_object_present"], f"{KEY_OBJECT} missing from the shim"
    assert probe["key_object_identical"], f"{KEY_OBJECT} is not the canonical object"


def test_canonical_module_still_configures_the_dashboard(probe):
    """Asserts the module actually calls set_page_config with the title, rather
    than that the string appears somewhere in a file."""
    assert PAGE_TITLE in probe["page_config_titles"], probe["page_config_titles"]


def test_canonical_module_renders_a_title(probe):
    assert probe["titles"], "dashboard rendered no st.title"
    assert any("Market Phase" in t for t in probe["titles"]), probe["titles"]


def test_dashboard_side_effects_stay_out_of_the_repository(probe):
    """app.py writes market_signals_report.json on import. It must land in the
    probe's temporary directory, never in the checkout."""
    assert "market_signals_report.json" in probe["files_written_to_cwd"], (
        "expected the dashboard's artifact in the sandbox; if this stops being "
        "written the isolation check below is no longer meaningful")
    assert not (ROOT / "market_signals_report.json").exists(), (
        "dashboard artifact leaked into the repository root")
