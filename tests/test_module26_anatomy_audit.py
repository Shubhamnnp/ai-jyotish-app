"""
Tests for Module 26: Body Anatomy & Physical Traits (body_anatomy_view.py)
Verifies DMS precision, classical shastriya shloka, and micro planetary anatomy diagnostics console.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.ui.modules.body_anatomy_view import (
    _format_dms,
    BODY_ANATOMY_SHLOKA,
    GRAHA_KALAPURUSHA_LIMBS,
    render_body_anatomy_view,
)


def test_format_dms_precision():
    """Verify conversion of float degrees to Ansh, Kala, Vikala."""
    ansh, kala, vikala, dms_str = _format_dms(12.75)
    assert ansh == 12
    assert kala == 45
    assert vikala == 0
    assert dms_str == '12° 45\' 00"'

    ansh2, kala2, vikala2, dms_str2 = _format_dms(29.9999)
    assert ansh2 == 30
    assert kala2 == 0
    assert vikala2 == 0
    assert dms_str2 == '30° 00\' 00"'


def test_body_anatomy_shloka_authenticity():
    """Verify authentic Sanskrit shloka from Brihat Samhita & BPHS."""
    assert "शीर्षं" in BODY_ANATOMY_SHLOKA["shloka"]
    assert "बृहत्संहिता" in BODY_ANATOMY_SHLOKA["source"]
    assert len(BODY_ANATOMY_SHLOKA["meaning"]) > 20


def test_graha_kalapurusha_limbs_completeness():
    """Verify all 9 Vedic planets have Kalapurusha organ mappings."""
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        assert p in GRAHA_KALAPURUSHA_LIMBS
        limb, details = GRAHA_KALAPURUSHA_LIMBS[p]
        assert len(limb) > 2
        assert len(details) > 5


def test_render_body_anatomy_view_no_crash(monkeypatch):
    """Verify render_body_anatomy_view executes cleanly without crashing."""
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
    render_body_anatomy_view(chart=mock_chart)
