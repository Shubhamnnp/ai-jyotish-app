"""
Tests for Module 28: Personality, Vices, Destiny & Karmic Ledger (karma_view.py)
Verifies DMS precision, classical shastriya shloka, and micro planetary karmic diagnostics console.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.ui.modules.karma_view import (
    _format_dms,
    KARMA_SHLOKA,
    GRAHA_KARMA_MAPPINGS,
    render_karma_view,
)


def test_format_dms_precision():
    """Verify conversion of float degrees to Ansh, Kala, Vikala."""
    ansh, kala, vikala, dms_str = _format_dms(18.25)
    assert ansh == 18
    assert kala == 15
    assert vikala == 0
    assert dms_str == '18° 15\' 00"'

    ansh2, kala2, vikala2, dms_str2 = _format_dms(29.999)
    assert ansh2 == 29
    assert kala2 == 59
    assert vikala2 == 56
    assert dms_str2 == '29° 59\' 56"'


def test_karma_shloka_authenticity():
    """Verify authentic Sanskrit shloka from Phaladeepika and Brihat Jataka."""
    assert "कर्मानुरूपं" in KARMA_SHLOKA["shloka"]
    assert "फलदीपिका" in KARMA_SHLOKA["source"]
    assert len(KARMA_SHLOKA["meaning"]) > 20


def test_graha_karma_mappings_completeness():
    """Verify all 9 Vedic planets have karmic roles and prarabdha indications."""
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        assert p in GRAHA_KARMA_MAPPINGS
        area, karma_trait, remedy = GRAHA_KARMA_MAPPINGS[p]
        assert len(area) > 2
        assert len(karma_trait) > 5
        assert len(remedy) > 5


def test_render_karma_view_no_crash(monkeypatch):
    """Verify render_karma_view executes cleanly without crashing."""
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
    monkeypatch.setattr(st, "progress", MagicMock())
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
    render_karma_view(chart=mock_chart)
