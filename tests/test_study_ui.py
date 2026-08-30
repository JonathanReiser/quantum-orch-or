from pathlib import Path


def test_participant_pilot_has_consent_debrief_and_exports():
    root = Path(__file__).resolve().parents[1]
    html = (root / "study.html").read_text(encoding="utf-8")
    javascript = (root / "study.js").read_text(encoding="utf-8")

    assert "No data is transmitted" in html
    assert "not an approved human-subjects study" in html
    assert 'id="consent-age"' in html
    assert 'id="debrief-screen"' in html
    assert "Download JSON record" in html
    assert "Download CSV events" in html
    assert 'protocol: "ewl-participant-pilot/v1"' in javascript
    assert 'backend = assignmentRandom() < 0.5' in javascript
    assert 'disclosure = assignmentRandom() < 0.5' in javascript
    assert "response_time_ms" in javascript
    assert "window.crypto.subtle.digest" in javascript


def test_main_lab_links_to_participant_pilot():
    root = Path(__file__).resolve().parents[1]
    index = (root / "index.html").read_text(encoding="utf-8")

    assert 'href="study.html"' in index
    assert "Launch anonymous participant pilot" in index
