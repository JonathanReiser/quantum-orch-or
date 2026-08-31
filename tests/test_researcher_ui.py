from pathlib import Path


def test_researcher_console_is_local_and_validates_records():
    root = Path(__file__).resolve().parents[1]
    html = (root / "researcher.html").read_text(encoding="utf-8")
    javascript = (root / "researcher.js").read_text(encoding="utf-8")

    assert "Nothing is uploaded" in html
    assert 'id="record-files"' in html
    assert "Accepted sessions" in html
    assert "Rejected records" in html
    assert "Duplicates" in html
    assert "Descriptive arm comparison" in html
    assert "Export combined event CSV" in html
    assert "SHA-256 integrity mismatch" in javascript
    assert "ResearchCore.validateRecord" in javascript
    assert "knownIds.has" in javascript
    assert "ResearchCore.summarize" in javascript


def test_experiment_and_participant_pages_link_to_console():
    root = Path(__file__).resolve().parents[1]
    index = (root / "index.html").read_text(encoding="utf-8")
    study = (root / "study.html").read_text(encoding="utf-8")

    assert 'href="researcher.html"' in index
    assert 'href="researcher.html"' in study
