"""
Tests for Module 25: Medical Astrology & Disease Forecast (health_disease_view.py)
Verifies DMS precision, classical shastriya shloka, and micro planetary health diagnostics console.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.ui.modules.health_disease_view import (
    _format_dms,
    HEALTH_SHLOKA,
    GRAHA_HEALTH_ROLES,
    render_health_disease_view,
)


def test_format_dms_precision():
    """Verify conversion of float degrees to Ansh, Kala, Vikala."""
    ansh, kala, vikala, dms_str = _format_dms(15.5)
    assert ansh == 15
    assert kala == 30
    assert vikala == 0
    assert dms_str == '15° 30\' 00"'

    ansh2, kala2, vikala2, dms_str2 = _format_dms(27.9999)
    assert ansh2 == 28
    assert kala2 == 0
    assert vikala2 == 0
    assert dms_str2 == '28° 00\' 00"'

    ansh3, kala3, vikala3, dms_str3 = _format_dms(0.0)
    assert ansh3 == 0
    assert kala3 == 0
    assert vikala3 == 0
    assert dms_str3 == '0° 00\' 00"'


def test_health_shloka_authenticity():
    """Verify authentic Sanskrit shloka from BPHS and Phaladeepika."""
    assert "रोगेशे" in HEALTH_SHLOKA["shloka"]
    assert "फलदीपिका" in HEALTH_SHLOKA["source"]
    assert len(HEALTH_SHLOKA["meaning"]) > 20


def test_graha_health_roles_completeness():
    """Verify all 9 Vedic planets have medical roles and bodily organ mappings."""
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        assert p in GRAHA_HEALTH_ROLES
        organs, details = GRAHA_HEALTH_ROLES[p]
        assert len(organs) > 3
        assert len(details) > 5


def test_render_health_disease_view_no_crash(monkeypatch):
    """Verify render_health_disease_view executes cleanly without crashing."""
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
    mock_chart.ascendant = 115.0
    mock_chart.lagna_sign_id = 4
    mock_chart.lagna_sign = 4
    mock_chart.birth_data = MagicMock(name="परीक्षण जातक")

    # Call view renderer
    render_health_disease_view(chart=mock_chart)
