"""
Tests for Module 32: Gemology & Rudraksha Advisory (gemology_view.py & gemology.py)
Verifies DMS precision, classical shastriya shloka, and gemstone / rudraksha audit engine.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.services.gemology import default_gemology_service
from src.jyotish.ui.modules.gemology_view import (
    SHASTRIYA_GEMOLOGY_SHLOKAS,
    render_gemology_view,
)


def test_gemology_service_dms_precision():
    """Verify gemology audit computes full ansh, kala, and vikala."""
    mock_chart = MagicMock()
    mock_chart.lagna_sign_id = 1
    mock_chart.planets = {
        "Sun": MagicMock(longitude=120.456, dignity="own", is_combust=False, is_retrograde=False, house_from_lagna=5),
        "Moon": MagicMock(longitude=55.123, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=2),
        "Mars": MagicMock(longitude=295.8, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=10),
        "Mercury": MagicMock(longitude=135.0, dignity="friend", is_combust=True, is_retrograde=True, house_from_lagna=5),
        "Jupiter": MagicMock(longitude=92.3, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=4),
        "Venus": MagicMock(longitude=358.9, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=12),
        "Saturn": MagicMock(longitude=210.2, dignity="exalted", is_combust=False, is_retrograde=True, house_from_lagna=7),
        "Rahu": MagicMock(longitude=45.0, dignity="neutral", is_combust=False, is_retrograde=True, house_from_lagna=2),
        "Ketu": MagicMock(longitude=225.0, dignity="neutral", is_combust=False, is_retrograde=True, house_from_lagna=8)
    }

    audit = default_gemology_service.audit_all_planets(mock_chart)
    sun_audit = audit["planets_audit"]["Sun"]
    assert "ansh" in sun_audit
    assert "kala" in sun_audit
    assert "vikala" in sun_audit
    assert "dms_str" in sun_audit
    assert "°" in sun_audit["dms_str"]
    assert "'" in sun_audit["dms_str"]
    assert '"' in sun_audit["dms_str"]


def test_gemology_shloka_authenticity():
    """Verify authentic Sanskrit shloka from Jataka Parijata & Phaladeepika."""
    shloka = SHASTRIYA_GEMOLOGY_SHLOKAS.get("jataka_parijata_navaratna", {})
    assert "माणिक्यं" in shloka.get("shloka", "")
    assert "जातक पारिजात" in shloka.get("grantha", "")


def test_render_gemology_view_no_crash(monkeypatch):
    """Verify render_gemology_view executes cleanly without crashing."""
    import streamlit as st

    # Mock streamlit components
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "expander", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]))
    monkeypatch.setattr(st, "metric", MagicMock())
    monkeypatch.setattr(st, "dataframe", MagicMock())
    monkeypatch.setattr(st, "info", MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())
    monkeypatch.setattr(st, "warning", MagicMock())
    monkeypatch.setattr(st, "error", MagicMock())
    monkeypatch.setattr(st, "caption", MagicMock())
    monkeypatch.setattr(st, "tabs", MagicMock(side_effect=lambda tabs: [MagicMock() for _ in tabs]))
    monkeypatch.setattr(st, "container", MagicMock())

    # Mock chart object with planetary details
    mock_chart = MagicMock()
    mock_chart.lagna_sign_id = 1
    mock_chart.planets = {
        "Sun": MagicMock(longitude=120.45, dignity="own", is_combust=False, is_retrograde=False, house_from_lagna=5),
        "Moon": MagicMock(longitude=55.12, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=2),
        "Mars": MagicMock(longitude=295.8, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=10),
        "Mercury": MagicMock(longitude=135.0, dignity="friend", is_combust=True, is_retrograde=True, house_from_lagna=5),
        "Jupiter": MagicMock(longitude=92.3, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=4),
        "Venus": MagicMock(longitude=358.9, dignity="exalted", is_combust=False, is_retrograde=False, house_from_lagna=12),
        "Saturn": MagicMock(longitude=210.2, dignity="exalted", is_combust=False, is_retrograde=True, house_from_lagna=7),
        "Rahu": MagicMock(longitude=45.0, dignity="neutral", is_combust=False, is_retrograde=True, house_from_lagna=2),
        "Ketu": MagicMock(longitude=225.0, dignity="neutral", is_combust=False, is_retrograde=True, house_from_lagna=8)
    }

    # Call view renderer
    render_gemology_view(chart=mock_chart)
