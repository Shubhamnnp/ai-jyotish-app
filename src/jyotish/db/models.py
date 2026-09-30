"""
Declarative SQLAlchemy Models for Bharat Jyotish AI SaaS Enterprise Persistence.
Supports full multi-tenant schema, 12,500+ Shastriya rules with condition AST,
benchmarks, Vargas, Dashas, Argon2id protected users, and Retrospective Event Verifications.
"""

import uuid
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, Date, Time, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from .session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    tier = Column(String(50), default="standard")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="astrologer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    primary_contact_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="clients")
    birth_profiles = relationship("BirthProfile", back_populates="client", cascade="all, delete-orphan")


class CalculationProfile(Base):
    __tablename__ = "calculation_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    name = Column(String(100), nullable=False)
    ayanamsa = Column(String(50), default="Lahiri")
    house_system = Column(String(50), default="Placidus")
    node_type = Column(String(50), default="Mean")
    year_length = Column(String(50), default="365.2422")
    dasha_default = Column(String(50), default="Vimshottari")


class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_id = Column(String(36), ForeignKey("clients.id"), nullable=True)
    full_name = Column(String(255), nullable=False, index=True)
    relation_to_client = Column(String(50), default="self")
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone_offset = Column(Float, default=5.5)
    city_name = Column(String(100), nullable=False)
    country_code = Column(String(10), default="IN")
    birth_time_confidence = Column(String(50), default="Exact")
    is_rectified = Column(Boolean, default=False)
    rectified_time = Column(Time, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="birth_profiles")
    charts = relationship("Chart", back_populates="birth_profile", cascade="all, delete-orphan")


class Chart(Base):
    __tablename__ = "charts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    birth_profile_id = Column(String(36), ForeignKey("birth_profiles.id"), nullable=False)
    calculation_profile_id = Column(String(36), ForeignKey("calculation_profiles.id"), nullable=True)
    lagna_sign_id = Column(Integer, nullable=False)
    lagna_sign_name = Column(String(50), nullable=False)
    lagna_degree = Column(Float, nullable=False)
    lagna_longitude = Column(Float, nullable=False)
    panchang_data = Column(JSON, default=dict)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    birth_profile = relationship("BirthProfile", back_populates="charts")
    planets = relationship("PlanetPositionModel", back_populates="chart", cascade="all, delete-orphan")
    vargas = relationship("VargaModel", back_populates="chart", cascade="all, delete-orphan")
    dashas = relationship("DashaModel", back_populates="chart", cascade="all, delete-orphan")
    verifications = relationship("EventVerificationModel", back_populates="chart", cascade="all, delete-orphan")


class PlanetPositionModel(Base):
    __tablename__ = "planet_positions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chart_id = Column(String(36), ForeignKey("charts.id"), nullable=False, index=True)
    planet_name = Column(String(50), nullable=False, index=True)
    longitude = Column(Float, nullable=False)
    sign_id = Column(Integer, nullable=False)
    sign_name = Column(String(50), nullable=False)
    sign_degree = Column(Float, nullable=False)
    house_number = Column(Integer, nullable=False)
    speed = Column(Float, default=1.0)
    is_retrograde = Column(Boolean, default=False)
    is_combust = Column(Boolean, default=False)
    nakshatra_name = Column(String(50), nullable=False)
    nakshatra_pada = Column(Integer, nullable=False)
    nakshatra_lord = Column(String(50), nullable=False)
    dignity = Column(String(50), default="Neutral")

    chart = relationship("Chart", back_populates="planets")


class VargaModel(Base):
    __tablename__ = "vargas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chart_id = Column(String(36), ForeignKey("charts.id"), nullable=False, index=True)
    varga_code = Column(String(10), nullable=False, index=True)
    lagna_sign_id = Column(Integer, nullable=False)
    lagna_sign_name = Column(String(50), nullable=False)
    positions = Column(JSON, default=dict)

    chart = relationship("Chart", back_populates="vargas")


class DashaModel(Base):
    __tablename__ = "dashas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chart_id = Column(String(36), ForeignKey("charts.id"), nullable=False, index=True)
    system_name = Column(String(50), default="Vimshottari")
    level = Column(Integer, default=1)
    mahadasha_lord = Column(String(50), nullable=False)
    antardasha_lord = Column(String(50), nullable=True)
    pratyantardasha_lord = Column(String(50), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    chart = relationship("Chart", back_populates="dashas")


class ShastriyaRuleModel(Base):
    __tablename__ = "shastriya_rules"

    rule_id = Column(String(100), primary_key=True)
    rule_title_hi = Column(String(255), nullable=False)
    rule_title_en = Column(String(255), nullable=True)
    source_grantha = Column(String(100), nullable=False, index=True)
    chapter = Column(String(100), default="General")
    author = Column(String(100), nullable=True)
    era = Column(String(50), nullable=True)
    school = Column(String(50), default="Parashari", index=True)
    domain = Column(String(100), default="General")
    subdomain = Column(String(100), default="General")
    condition_ast = Column(JSON, nullable=False)
    polarity = Column(String(10), default="+")
    base_weight = Column(Float, default=1.0)
    conflict_group = Column(String(100), nullable=True)
    shloka_sanskrit = Column(Text, nullable=True)
    description_hi = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    varga_tags = Column(JSON, default=list)
    planet_tags = Column(JSON, default=list)
    house_tags = Column(JSON, default=list)
    version = Column(String(20), default="1.0.0")
    status = Column(String(50), default="Active")
    provenance = Column(String(100), default="Classical Translation")


class RuleConflict(Base):
    __tablename__ = "rule_conflicts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_id_primary = Column(String(100), nullable=False)
    rule_id_secondary = Column(String(100), nullable=False)
    relation_type = Column(String(50), nullable=False)
    resolution_principle = Column(String(255), nullable=True)


class EventVerificationModel(Base):
    __tablename__ = "event_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chart_id = Column(String(36), ForeignKey("charts.id"), nullable=False, index=True)
    event_theme = Column(String(100), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    candidate_window_start = Column(Date, nullable=True)
    candidate_window_end = Column(Date, nullable=True)
    status = Column(String(50), nullable=False)
    astrological_evidence_score = Column(Float, default=0.0)
    d1_evidence = Column(JSON, default=dict)
    prashna_evidence = Column(JSON, default=dict)
    d9_evidence = Column(JSON, default=dict)
    dasha_evidence = Column(JSON, default=dict)
    transit_evidence = Column(JSON, default=dict)
    rule_evidence_ids = Column(JSON, default=list)
    contradicting_evidence = Column(JSON, default=dict)
    ai_explanation_hi = Column(Text, nullable=True)
    ai_explanation_en = Column(Text, nullable=True)
    verified_by_user = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chart = relationship("Chart", back_populates="verifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=True)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
