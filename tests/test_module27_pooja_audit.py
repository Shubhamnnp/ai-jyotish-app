"""
Tests for Module 27: Vedic Pooja & Spiritual Sadhana (pooja_view.py)
Verifies DMS precision, classical shastriya shloka, and micro planetary spiritual diagnostics console.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.ui.modules.pooja_view import (
    _format_dms,
    POOJA_SHLOKA,
    GRAHA_DEITY_MAPPINGS,
    render_pooja_view,
)


def test_format_dms_precision():
    """Verify conversion of float degrees to Ansh, Kala, Vikala."""
    ansh, kala, vikala, dms_str = _format_dms(21.3333)
    assert ansh == 21
    assert kala == 20
    assert vikala == 0
    assert dms_str == '21° 20\' 00"'

    ansh2, kala2, vikala2, dms_str2 = _format_dms(0.5)
    assert ansh2 == 0
    assert kala2 == 30
    assert vikala2 == 0
    assert dms_str2 == '0° 30\' 00"'


def test_pooja_shloka_authenticity():
    """Verify authentic Sanskrit shloka from Jaimini Sutram & BPHS."""
    assert "कारकांशाद्" in POOJA_SHLOKA["shloka"]
    assert "जैमिनी" in POOJA_SHLOKA["source"]
    assert len(POOJA_SHLOKA["meaning"]) > 20


def test_graha_deity_mappings_completeness():
    """Verify all 9 Vedic planets have spiritual deity and mantra mappings."""
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        assert p in GRAHA_DEITY_MAPPINGS
        deity, mala, mantra = GRAHA_DEITY_MAPPINGS[p]
        assert len(deity) > 2
        assert len(mala) > 2
        assert len(mantra) > 5


def test_render_pooja_view_no_crash(monkeypatch):
    """Verify render_pooja_view executes cleanly without crashing."""
    import streamlit as st

    # Mock streamlit components
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "write", MagicMock())
    monkeypatch.setattr(st, "caption", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "expander", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]))
    monkeypatch.setattr(st, "metric", MagicMock())
    monkeypatch.setattr(st, "dataframe", MagicMock())
    monkeypatch.setattr(st, "info", MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())
    monkeypatch.setattr(st, "warning", MagicMock())
    monkeypatch.setattr(st, "error", MagicMock())
    monkeypatch.setattr(st, "code", MagicMock())
    monkeypatch.setattr(st, "tabs", MagicMock(side_effect=lambda tabs: [MagicMock() for _ in tabs]))

    # Mock chart object with planetary details
    mock_chart = MagicMock()
    mock_chart.planets = {
        "Sun": MagicMock(longitude=120.45, sign_num=5, house=1, is_retrograde=False, is_combust=False, dignity="own"),
        "Moon": MagicMock(longitude=55.12, sign_num=2, house=10, is_retrograde=False, is_combust=False, dignity="exalted"),
        "Mars": MagicMock(longitude=295.8, sign_num=10, house=6, is_retrograde=False, is_combust=False, dignity="exalted"),
        "Mercury": MagicMock(longitude=135.0, sign_num=5, house=1, is_retrograde=True, is_combust=True, dignity="friend"),
        "Jupiter": MagicMock(longitude=92.3, sign_num=4, house=12, is_retrograde=False, is_combust=False, dignity="exalted"),
        "Venus": MagicMock(longitude=358.9, sign_num=12, house=8, is_retrograde=False, is_combust=False, dignity="exalted"),
        "Saturn": MagicMock(longitude=210.2, sign_num=7, house=3, is_retrograde=True, is_combust=False, dignity="exalted"),
        "Rahu": MagicMock(longitude=45.0, sign_num=2, house=10, is_retrograde=True, is_combust=False, dignity="neutral"),
        "Ketu": MagicMock(longitude=225.0, sign_num=8, house=4, is_retrograde=True, is_combust=False, dignity="neutral")
    }
    mock_chart.ascendant = 120.0
    mock_chart.lagna_sign_id = 5
    mock_chart.lagna_sign = 5
    mock_chart.birth_data = MagicMock(name="परीक्षण जातक")

    # Call view renderer
    render_pooja_view(chart=mock_chart)
