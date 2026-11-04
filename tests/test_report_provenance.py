"""
Unit tests for Report Generator Provenance Hardening & Classical Citations (Phase 5, Task P5-T9).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.3 & 5.4, P5-T9).

Verifies:
1. Multi-domain Evidence Pack integration into publication-grade HTML reports.
2. Every domain finding contains Grantha provenance (text + chapter + verse) and verified badge.
3. Embedded Google Devanagari and Sanskrit typography ('Noto Sans Devanagari', 'Tiro Devanagari Sanskrit').
4. Rendering of all 3 traditional regional chart styles: North Indian, South Indian, and East Indian SVGs.
5. Paged-media dynamic page numbering via CSS counter(page).
6. Comprehensive statutory, medical, and ethical safety disclaimers.
"""

import sys
import os
import pytest
from datetime import date, time

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.services.report_generator import default_report_generator
from jyotish.services.pdf_generator import default_pdf_service


@pytest.fixture(scope="module")
def benchmark_chart():
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=time(6, 33, 0),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.89,
        gender="male",
        confidence="exact"
    )
    return default_chart_calculator.calculate_full_chart(bd)


def test_html_report_generation(benchmark_chart):
    """Test full HTML master report generation with domain evidence packs."""
    html = default_report_generator.generate_html_report(benchmark_chart)
    assert isinstance(html, str)
    assert len(html) > 50000
    assert "<!DOCTYPE html>" in html
    assert "</html>" in html


def test_devanagari_fonts_embedded(benchmark_chart):
    """Test embedding of Devanagari and Sanskrit typography fonts."""
    html = default_report_generator.generate_html_report(benchmark_chart)
    assert "Noto Sans Devanagari" in html
    assert "Tiro Devanagari Sanskrit" in html
    assert "font-family:" in html


def test_regional_charts_rendered(benchmark_chart):
    """Test that all three regional chart styles (North, South, East) are rendered."""
    html = default_report_generator.generate_html_report(benchmark_chart)
    assert "उत्तर भारतीय प्रारूप (North Indian Diamond)" in html
    assert "दक्षिण भारतीय प्रारूप (South Indian Square)" in html
    assert "पूर्वी / बंगाली प्रारूप (East Indian Bengali/Odia)" in html
    # Check that SVG elements exist
    assert html.count("<svg") >= 3


def test_domain_evidence_provenance_and_badges(benchmark_chart):
    """Test that Shastriya Evidence Pack cards contain source citations and verified badges."""
    html = default_report_generator.generate_html_report(benchmark_chart)
    # Check Section header
    assert "जीवन-आयाम शास्त्रीय प्रमाण समुच्चय" in html
    # Check verification badges
    assert "✓ प्रामाणिक शास्त्रीय प्रमाण (Verified)" in html
    # Check classical grantha references
    assert "Brihat Parashara Hora Shastra" in html
    assert "ग्रन्थ स्रोत:" in html
    # Check finding IDs
    assert "F1" in html


def test_page_numbering_and_disclaimer(benchmark_chart):
    """Test CSS page numbering and ethical/statutory disclaimer."""
    html = default_report_generator.generate_html_report(benchmark_chart)
    # CSS page counter
    assert "counter(page)" in html
    # Statutory & ethical safety disclaimers
    assert "वैधानिक एवं नैतिक अस्वीकरण" in html
    assert "PCPNDT Act" in html
    assert "मृत्यु की निश्चित तिथि" in html
    assert "चिकित्सीय निदान" in html


def test_pdf_service_browser_locator():
    """Test that PDF service locates executable or handles gracefully."""
    browser_bin = default_pdf_service.find_browser_executable()
    # On Windows dev machine with Edge/Chrome, should find an executable
    if browser_bin:
        assert os.path.exists(browser_bin)
