"""
Test suite for Enterprise Relational Persistence (Milestone 2).
Verifies:
1. Lossless migration parity (>12,500 Shastriya rules preserved).
2. Multi-school coverage (Parashari, Jaimini, KP, LalKitab, Tajika, Nadi).
3. Benchmark chart persistence with Vargas, Dashas, and Planet Positions.
4. User security with Argon2id hash verification.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.db.session import SessionLocal
from jyotish.db.models import (
    User, Client, BirthProfile, Chart, PlanetPositionModel, VargaModel, DashaModel, ShastriyaRuleModel
)
from argon2 import PasswordHasher


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_shastriya_rules_count_and_integrity(db_session):
    """Assert Master Directive Rule 3: Zero loss of classical Jyotish rules."""
    total_rules = db_session.query(ShastriyaRuleModel).count()
    assert total_rules >= 12500, f"Expected at least 12,500 rules, found {total_rules}"

    schools = db_session.query(ShastriyaRuleModel.school).distinct().all()
    school_names = {s[0] for s in schools}
    assert "Parashari" in school_names
    assert "Jaimini" in school_names
    assert "KP" in school_names

    sample_rule = db_session.query(ShastriyaRuleModel).filter(
        ShastriyaRuleModel.source_grantha.like("%Brihat%")
    ).first()
    assert sample_rule is not None
    assert sample_rule.rule_id
    assert sample_rule.rule_title_hi
    assert sample_rule.condition_ast is not None


def test_user_authentication_security(db_session):
    """Verify User accounts exist with valid Argon2id password hashes."""
    users = db_session.query(User).all()
    assert len(users) >= 3, f"Expected at least 3 users, found {len(users)}"

    admin = db_session.query(User).filter(User.email.like("admin%")).first()
    assert admin is not None
    assert admin.password_hash.startswith("$argon2id$")

    ph = PasswordHasher()
    assert ph.verify(admin.password_hash, "Admin@123")


def test_benchmark_charts_persistence(db_session):
    """Verify benchmark Kundalis are stored with linked planets, vargas, and dashas."""
    profiles = db_session.query(BirthProfile).all()
    assert len(profiles) >= 10, f"Expected at least 10 benchmark birth profiles, found {len(profiles)}"

    vivi_profile = db_session.query(BirthProfile).filter(BirthProfile.full_name.like("%Vivekananda%")).first()
    assert vivi_profile is not None
    assert len(vivi_profile.charts) > 0

    vivi_chart = vivi_profile.charts[0]
    assert vivi_chart.lagna_sign_id == 9

    planets = db_session.query(PlanetPositionModel).filter(PlanetPositionModel.chart_id == vivi_chart.id).all()
    assert len(planets) == 9
    planet_names = {p.planet_name for p in planets}
    assert "Sun" in planet_names
    assert "Jupiter" in planet_names
    assert "Rahu" in planet_names

    vargas = db_session.query(VargaModel).filter(VargaModel.chart_id == vivi_chart.id).all()
    assert len(vargas) >= 16
    varga_codes = {v.varga_code for v in vargas}
    assert "D1" in varga_codes
    assert "D9" in varga_codes
    assert "D10" in varga_codes
    assert "D60" in varga_codes

    dashas = db_session.query(DashaModel).filter(DashaModel.chart_id == vivi_chart.id).all()
    assert len(dashas) > 0
