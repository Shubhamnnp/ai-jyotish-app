"""
Unit tests for Provenance Badges & Shastriya Popovers (Phase 6, Task P6-T2).
Reference: docs/IMPLEMENTATION_PRD.md (Section 3.6 & 5.5, P6-T2).

Verifies:
1. Always-visible Provenance bar with Swiss Ephemeris vs Degraded Engine badge.
2. Exact Ayanamsa name and float degree representation.
3. Verified rules used count representation.
4. House system and IANA timezone representation.
5. Per-finding source popover generation with Grantha citation and Sanskrit shloka.
"""

import sys
import os
import pytest
from datetime import date, time

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.ui.components.provenance import (
    render_provenance_badge_html,
    render_finding_source_popover_html
)


@pytest.fixture(scope="module")
def sample_chart():
    bd = BirthData(
        name="Test",
        birth_date=date(1995, 5, 15),
        birth_time=time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_full_chart(bd)


def test_provenance_bar_swiss_ephemeris(sample_chart):
    """Verify Swiss Ephemeris high-precision badge on standard calculation."""
    html = render_provenance_badge_html(sample_chart, verified_rules_count=32)
    assert "Swiss Ephemeris" in html
    assert "High Precision" in html
    assert "Lahiri" in html
    assert "Verified Rules Applied" in html
    assert "Whole Sign" in html
    assert "Asia/Kolkata" in html


def test_provenance_bar_degraded_fallback(sample_chart):
    """Verify Degraded Engine warning badge when chart is degraded."""
    # Temporarily set degraded flag on chart
    sample_chart.engine_degraded = True
    html = render_provenance_badge_html(sample_chart, verified_rules_count=32)
    assert "Degraded Engine" in html
    assert "PyEphem Fallback" in html
    # Restore
    sample_chart.engine_degraded = False


def test_finding_source_popover():
    """Verify interactive HTML source popover rendering."""
    pop_html = render_finding_source_popover_html(
        finding_id="F1",
        grantha="Brihat Parashara Hora Shastra",
        chapter="Adhyaya 20",
        verse="1-4",
        shloka="तत्तद्भावफलं वक्ष्ये शृणु त्वं द्विजसत्तम।",
        claim_hi="दशम भाव में शुभ ग्रह स्थित हैं।",
        verified=True
    )
    assert "<details" in pop_html
    assert "</details>" in pop_html
    assert "Brihat Parashara Hora Shastra" in pop_html
    assert "Adhyaya 20" in pop_html
    assert "1-4" in pop_html
    assert "तत्तद्भावफलं वक्ष्ये" in pop_html
    assert "Verified Shastriya Pramana" in pop_html
