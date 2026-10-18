"""
Unit tests for multi-tenant Kundali Vault & Folder Manager data isolation.
Verifies that charts saved by one user (e.g. axemple@gmail.com) are NEVER visible
to or modifiable by another user (e.g. deepakexample@gmail.com).
"""

import os
import tempfile
import pytest
from src.jyotish.services.folder_manager import ChartFolderManager
from src.jyotish.services.vault import KundaliVaultService


@pytest.fixture
def isolated_vault():
    """Creates a temporary isolated ChartFolderManager and KundaliVaultService."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    manager = ChartFolderManager(db_path=tmp_path)
    vault = KundaliVaultService(db_path=tmp_path)
    vault.manager = manager

    yield vault, manager

    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        pass


def test_multi_tenant_chart_isolation(isolated_vault):
    vault, manager = isolated_vault

    user_a = "axemple@gmail.com"
    user_b = "deepakexample@gmail.com"

    # User A saves Manish, Ramesh, Komal
    sample_birth = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "city": "Delhi"
    }
    c_manish = vault.save_client(name="Manish", birth_data=sample_birth, owner_email=user_a)
    c_ramesh = vault.save_client(name="Ramesh", birth_data=sample_birth, owner_email=user_a)
    c_komal = vault.save_client(name="Komal", birth_data=sample_birth, owner_email=user_a)

    # User B saves Rajesh, Mahesh, Suresh
    c_rajesh = vault.save_client(name="Rajesh", birth_data=sample_birth, owner_email=user_b)
    c_mahesh = vault.save_client(name="Mahesh", birth_data=sample_birth, owner_email=user_b)
    c_suresh = vault.save_client(name="Suresh", birth_data=sample_birth, owner_email=user_b)

    # 1. Check User A view
    clients_a = vault.list_all_clients(owner_email=user_a)
    names_a = [c["name"] for c in clients_a]

    assert "Manish" in names_a
    assert "Ramesh" in names_a
    assert "Komal" in names_a

    # User B's charts MUST NOT be visible to User A
    assert "Rajesh" not in names_a
    assert "Mahesh" not in names_a
    assert "Suresh" not in names_a

    # Benchmark demo charts (e.g. Swami Vivekananda) should be visible
    assert any("Vivekananda" in n for n in names_a)

    # 2. Check User B view
    clients_b = vault.list_all_clients(owner_email=user_b)
    names_b = [c["name"] for c in clients_b]

    assert "Rajesh" in names_b
    assert "Mahesh" in names_b
    assert "Suresh" in names_b

    # User A's charts MUST NOT be visible to User B
    assert "Manish" not in names_b
    assert "Ramesh" not in names_b
    assert "Komal" not in names_b

    # 3. Check Unauthenticated / Public view (owner_email=None)
    clients_guest = vault.list_all_clients(owner_email=None)
    names_guest = [c["name"] for c in clients_guest]

    assert "Manish" not in names_guest
    assert "Rajesh" not in names_guest
    # Only benchmark demo charts visible
    assert all(1000 <= c["id"] <= 1015 for c in clients_guest)

    # 4. Check Folder Manager isolation
    folders_a = manager.list_folders(owner_email=user_a)
    all_charts_in_folders_a = [
        c["name"] for f in folders_a for c in f.get("charts", [])
    ]
    assert "Manish" in all_charts_in_folders_a
    assert "Rajesh" not in all_charts_in_folders_a

    # 5. Check Recent Charts isolation
    recents_a = manager.list_recent_charts(owner_email=user_a)
    recent_names_a = [c["name"] for c in recents_a]
    assert "Manish" in recent_names_a
    assert "Rajesh" not in recent_names_a

    # 6. Check Deletion Cross-Tenant Protection
    # User A cannot delete User B's chart
    deleted_cross = vault.delete_client(client_id=c_rajesh["id"], owner_email=user_a)
    # Chart should still exist for User B
    clients_b_after = vault.list_all_clients(owner_email=user_b)
    names_b_after = [c["name"] for c in clients_b_after]
    assert "Rajesh" in names_b_after

    # User B can delete their own chart
    deleted_own = vault.delete_client(client_id=c_rajesh["id"], owner_email=user_b)
    assert deleted_own is True
    clients_b_after_delete = vault.list_all_clients(owner_email=user_b)
    names_b_after_delete = [c["name"] for c in clients_b_after_delete]
    assert "Rajesh" not in names_b_after_delete

