"""
Tests for Module 30: Classical Predictive Analysis (shastriya_faladesh_view.py)
Verifies DMS precision, classical shastriya shloka, and 50-dimension evidence table.
"""
from unittest.mock import MagicMock
import pytest
from src.jyotish.ui.shastriya_faladesh_view import (
    _format_dms,
    SHASTRIYA_FALADESH_SHLOKA,
    render_shastriya_faladesh_view,
)


def test_format_dms_precision():
    """Verify conversion of float degrees to Ansh, Kala, Vikala."""
    ansh, kala, vikala, dms_str = _format_dms(14.375)
    assert ansh == 14
    assert kala == 22
    assert vikala == 30
    assert dms_str == '14° 22\' 30"'

    ansh2, kala2, vikala2, dms_str2 = _format_dms(45.5)  # 45.5 % 30 = 15.5
    assert ansh2 == 15
    assert kala2 == 30
    assert vikala2 == 0
    assert dms_str2 == '15° 30\' 00"'


def test_shastriya_faladesh_shloka_authenticity():
    """Verify authentic Sanskrit shloka from BPHS and Phaladeepika."""
    assert "यद् यद्" in SHASTRIYA_FALADESH_SHLOKA["shloka"]
    assert "बृहत्पाराशर" in SHASTRIYA_FALADESH_SHLOKA["source"]
    assert len(SHASTRIYA_FALADESH_SHLOKA["meaning"]) > 20


def test_render_shastriya_faladesh_view_no_crash(monkeypatch):
    """Verify render_shastriya_faladesh_view executes cleanly without crashing."""
    import streamlit as st

    # Mock streamlit components
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "expander", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]))
    monkeypatch.setattr(st, "dataframe", MagicMock())
    monkeypatch.setattr(st, "selectbox", MagicMock(return_value="1. आजीविका व कर्म"))
    monkeypatch.setattr(st, "radio", MagicMock(return_value="दैनिक जीवन एवं प्राथमिक जिज्ञासाएं (General Querent FAQs)"))
    monkeypatch.setattr(st, "text_input", MagicMock(return_value=""))
    monkeypatch.setattr(st, "info", MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())
    monkeypatch.setattr(st, "warning", MagicMock())
    monkeypatch.setattr(st, "tabs", MagicMock(side_effect=lambda tabs: [MagicMock() for _ in tabs]))

    # Mock chart object with planetary details
    mock_chart = MagicMock()
    mock_chart.planets = {
        "Sun": MagicMock(longitude=120.45, sign_name="Leo", sign_id=5, sign_degree=0.45, house_from_lagna=1, house_from_moon=10, is_retrograde=False, is_combust=False, dignity="own", nakshatra_name="मघा", nakshatra_pada=1, nakshatra_lord="Ketu"),
        "Moon": MagicMock(longitude=55.12, sign_name="Taurus", sign_id=2, sign_degree=25.12, house_from_lagna=10, house_from_moon=1, is_retrograde=False, is_combust=False, dignity="exalted", nakshatra_name="मृगशिरा", nakshatra_pada=2, nakshatra_lord="Mars"),
        "Mars": MagicMock(longitude=295.8, sign_name="Capricorn", sign_id=10, sign_degree=25.8, house_from_lagna=6, house_from_moon=9, is_retrograde=False, is_combust=False, dignity="exalted", nakshatra_name="धनिष्ठा", nakshatra_pada=1, nakshatra_lord="Mars"),
        "Mercury": MagicMock(longitude=135.0, sign_name="Leo", sign_id=5, sign_degree=15.0, house_from_lagna=1, house_from_moon=10, is_retrograde=True, is_combust=True, dignity="friend", nakshatra_name="पूर्वाफाल्गुनी", nakshatra_pada=1, nakshatra_lord="Venus"),
        "Jupiter": MagicMock(longitude=92.3, sign_name="Cancer", sign_id=4, sign_degree=2.3, house_from_lagna=12, house_from_moon=3, is_retrograde=False, is_combust=False, dignity="exalted", nakshatra_name="पुनर्वसु", nakshatra_pada=4, nakshatra_lord="Jupiter"),
        "Venus": MagicMock(longitude=358.9, sign_name="Pisces", sign_id=12, sign_degree=28.9, house_from_lagna=8, house_from_moon=11, is_retrograde=False, is_combust=False, dignity="exalted", nakshatra_name="रेवती", nakshatra_pada=4, nakshatra_lord="Mercury"),
        "Saturn": MagicMock(longitude=210.2, sign_name="Libra", sign_id=7, sign_degree=0.2, house_from_lagna=3, house_from_moon=6, is_retrograde=True, is_combust=False, dignity="exalted", nakshatra_name="विशाखा", nakshatra_pada=1, nakshatra_lord="Jupiter"),
        "Rahu": MagicMock(longitude=45.0, sign_name="Taurus", sign_id=2, sign_degree=15.0, house_from_lagna=10, house_from_moon=1, is_retrograde=True, is_combust=False, dignity="neutral", nakshatra_name="रोहिणी", nakshatra_pada=2, nakshatra_lord="Moon"),
        "Ketu": MagicMock(longitude=225.0, sign_name="Scorpio", sign_id=8, sign_degree=15.0, house_from_lagna=4, house_from_moon=7, is_retrograde=True, is_combust=False, dignity="neutral", nakshatra_name="अनुराधा", nakshatra_pada=4, nakshatra_lord="Saturn")
    }
    mock_chart.lagna_sign_name = "Leo"
    mock_chart.lagna_sign_id = 5
    mock_chart.lagna_degree = 120.45
    mock_chart.houses = []
    mock_chart.shadbala = None

    # Call view renderer
    render_shastriya_faladesh_view(chart=mock_chart)
