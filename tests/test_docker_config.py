"""
Unit tests for Docker containerization, compose syntax, and deployment docs (Phase 6, Task P6-T8).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.8, P6-T8).
"""

import os
import yaml
import pytest


def test_dockerfile_configuration():
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile must exist at repo root"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "FROM python:3.11-slim" in content or "FROM python:3." in content
    assert "EPHE_PATH=/app/ephe" in content
    assert "HEALTHCHECK" in content
    assert "/health" in content
    assert "fonts-" in content


def test_docker_compose_syntax_and_services():
    compose_path = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml must exist at repo root"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    assert "services" in compose_data
    services = compose_data["services"]

    # 1. API Service
    assert "api" in services
    api_svc = services["api"]
    assert "healthcheck" in api_svc
    assert any("/app/ephe" in v for v in api_svc.get("volumes", []))
    assert any("JYOTISH_ENCRYPTION_KEY" in e for e in api_svc.get("environment", []))

    # 2. UI Service
    assert "ui" in services
    ui_svc = services["ui"]
    assert "depends_on" in ui_svc
    assert any("/app/ephe" in v for v in ui_svc.get("volumes", []))

    # 3. Database & Redis
    assert "postgres" in services
    assert "redis" in services


def test_deployment_documentation_completeness():
    docs_path = os.path.join(os.path.dirname(__file__), "..", "docs", "DEPLOYMENT.md")
    assert os.path.exists(docs_path), "docs/DEPLOYMENT.md must exist"

    with open(docs_path, "r", encoding="utf-8") as f:
        doc = f.read()

    assert "Swiss Ephemeris" in doc
    assert "EPHE_PATH" in doc
    assert "docker compose up" in doc
    assert "/health" in doc
    assert "GDPR" in doc or "DPDP" in doc

