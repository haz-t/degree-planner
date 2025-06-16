import os
import pytest

from scripts.parsers import parse_file

SAMPLE_PDF = os.path.join("_context", "2025-Fall-Course-Schedule.pdf")

@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF), reason="Sample PDF not present in repo")
def test_parse_file_returns_courses_and_totals():
    data = parse_file(SAMPLE_PDF)
    assert data["courses"], "Expected at least one course parsed"
    assert data["totals"], "Expected credit totals populated"
    # Sanity: at least one Bible bucket populated if present
    if "Bible/Sacred Texts" in data["totals"]:
        assert data["totals"]["Bible/Sacred Texts"] > 0 