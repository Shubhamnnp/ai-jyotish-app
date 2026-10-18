"""
Client Kundali Vault & Quick Switch Service for JyotishOS.
Provides professional astrologer client management with tags (VIP, Marriage, Career, Health),
notes, quick search, 1-click session loading, and JSON backup/restore.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

try:
    from .folder_manager import default_folder_manager, DEFAULT_STORAGE_PATH
    from ..core.models import BirthData
except (ImportError, ValueError):
    from src.jyotish.services.folder_manager import default_folder_manager, DEFAULT_STORAGE_PATH
    from src.jyotish.core.models import BirthData

AVAILABLE_TAGS = [
    "🌟 VIP",
    "💍 विवाह (Marriage)",
    "💼 करियर (Career)",
    "🏥 स्वास्थ्य (Health)",
    "💰 धन व व्यापार (Wealth/Biz)",
    "👶 संतान (Progeny)",
    "⚖️ कानूनी विवाद (Legal)",
    "🏡 वास्तु/गृह (Property)"
]


class KundaliVaultService:
    """Manages client horoscopes with tagging, search, notes, and backup."""

    def __init__(self, db_path: str = DEFAULT_STORAGE_PATH):
        self.db_path = os.path.abspath(db_path)
        self.manager = default_folder_manager

    def list_all_clients(
        self,
        search_query: Optional[str] = None,
        tag_filter: Optional[str] = None,
        owner_email: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists all saved clients across all folders with optional search query, tag filter,
        and strict multi-tenant data isolation based on owner_email.
        Each user only sees their own saved clients + 10 benchmark demo charts.
        """
        clean_owner = owner_email.strip().lower() if owner_email else None
        folders = self.manager.list_folders(owner_email=clean_owner)
        all_clients = []
        seen_ids = set()

        for folder in folders:
            folder_name = folder.get("name", "General")
            for chart in folder.get("charts", []):
                cid = chart.get("id")
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)

                c_copy = dict(chart)
                c_copy["folder_id"] = folder.get("id", 0)
                c_copy["folder_name"] = folder_name
                # Ensure tags, notes & owner_email exist
                if "tags" not in c_copy:
                    c_copy["tags"] = ["🌟 VIP"] if "VIP" in folder_name else [" सामान्य"]
                if "notes" not in c_copy:
                    c_copy["notes"] = ""
                chart_owner = str(c_copy.get("owner_email", "")).strip().lower()

                # Multi-tenant data privacy isolation:
                # Benchmark demo charts (1000 <= cid <= 1015) are visible to all.
                # User charts are strictly visible ONLY to the owner who saved them.
                is_demo = isinstance(cid, int) and 1000 <= cid <= 1015
                if not is_demo:
                    if not clean_owner or chart_owner != clean_owner:
                        continue

                # Filter by tag
                if tag_filter and tag_filter != "सभी (All)":
                    if tag_filter not in c_copy.get("tags", []):
                        continue

                # Filter by search query
                if search_query:
                    q = search_query.lower().strip()
                    bdata = c_copy.get("birth_data", {})
                    name = str(c_copy.get("name", "")).lower()
                    city = str(bdata.get("city", "")).lower()
                    notes = str(c_copy.get("notes", "")).lower()
                    if q not in name and q not in city and q not in notes:
                        continue

                all_clients.append(c_copy)

        return all_clients

    def save_client(
        self,
        name: str,
        birth_data: Dict[str, Any],
        tags: Optional[List[str]] = None,
        notes: str = "",
        folder_id: int = 0,
        owner_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Saves a new client or updates an existing client in the vault with owner_email tracking.
        """
        tags = tags or [" सामान्य"]
        clean_owner = owner_email.strip().lower() if owner_email else "public"
        chart_entry = self.manager.save_chart(folder_id, name, birth_data, owner_email=clean_owner)
        chart_entry["tags"] = tags
        chart_entry["notes"] = notes
        chart_entry["owner_email"] = clean_owner

        # Update inside the folder
        for folder in self.manager.data.get("folders", []):
            for ch in folder.get("charts", []):
                if ch.get("id") == chart_entry["id"]:
                    ch["tags"] = tags
                    ch["notes"] = notes
                    ch["owner_email"] = clean_owner
                    break

        self.manager._save()
        return chart_entry

    def update_client(
        self,
        client_id: Any,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Updates tags or notes for an existing client."""
        updated = False
        for folder in self.manager.data.get("folders", []):
            for ch in folder.get("charts", []):
                if ch.get("id") == client_id:
                    if tags is not None:
                        ch["tags"] = tags
                    if notes is not None:
                        ch["notes"] = notes
                    updated = True
                    break
        if updated:
            self.manager._save()
        return updated

    def delete_client(self, client_id: Any, owner_email: Optional[str] = None) -> bool:
        """Deletes a client chart from all folders and recent list, ensuring ownership."""
        # Benchmark demo charts cannot be deleted
        if isinstance(client_id, int) and 1000 <= client_id <= 1015:
            return False

        clean_owner = owner_email.strip().lower() if owner_email else None
        deleted = False
        for folder in self.manager.data.get("folders", []):
            charts = folder.get("charts", [])
            new_charts = []
            for c in charts:
                if c.get("id") == client_id:
                    c_owner = str(c.get("owner_email", "")).strip().lower()
                    if clean_owner and c_owner and c_owner != clean_owner:
                        new_charts.append(c)
                        continue
                    deleted = True
                else:
                    new_charts.append(c)
            folder["charts"] = new_charts

        recents = self.manager.data.get("recent_charts", [])
        self.manager.data["recent_charts"] = [
            c for c in recents 
            if c.get("id") != client_id or (clean_owner and str(c.get("owner_email", "")).strip().lower() != clean_owner)
        ]
        if deleted:
            self.manager._save()
        return deleted

    def export_backup_json(self, owner_email: Optional[str] = None) -> str:
        """Exports the user's vault database as formatted JSON string."""
        clean_owner = owner_email.strip().lower() if owner_email else None
        folders = self.manager.list_folders(owner_email=clean_owner)
        recents = self.manager.list_recent_charts(owner_email=clean_owner)
        export_data = {
            "folders": folders,
            "recent_charts": recents
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def import_backup_json(self, json_content: str, owner_email: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        Imports and merges client charts from JSON string backup tagged with owner_email.
        """
        try:
            imported_data = json.loads(json_content)
            if not isinstance(imported_data, dict) or "folders" not in imported_data:
                return False, "अमान्य JSON प्रारूप (Invalid Vault Backup Format)", 0

            count = 0
            clean_owner = owner_email.strip().lower() if owner_email else "public"
            existing_folders = {f["id"]: f for f in self.manager.data.get("folders", [])}

            for imp_folder in imported_data.get("folders", []):
                f_id = imp_folder.get("id")
                # Do not duplicate or overwrite demo folder charts
                if f_id == 100:
                    continue
                if f_id in existing_folders:
                    target_f = existing_folders[f_id]
                    existing_chart_names = {c.get("name") for c in target_f.get("charts", []) if str(c.get("owner_email", "")).strip().lower() == clean_owner}
                    for ch in imp_folder.get("charts", []):
                        cid = ch.get("id")
                        if isinstance(cid, int) and 1000 <= cid <= 1015:
                            continue
                        if ch.get("name") not in existing_chart_names:
                            ch_copy = dict(ch)
                            ch_copy["owner_email"] = clean_owner
                            target_f.setdefault("charts", []).append(ch_copy)
                            count += 1
                else:
                    new_f = dict(imp_folder)
                    new_f["owner_email"] = clean_owner
                    valid_charts = []
                    for ch in imp_folder.get("charts", []):
                        cid = ch.get("id")
                        if isinstance(cid, int) and 1000 <= cid <= 1015:
                            continue
                        ch_copy = dict(ch)
                        ch_copy["owner_email"] = clean_owner
                        valid_charts.append(ch_copy)
                        count += 1
                    new_f["charts"] = valid_charts
                    self.manager.data.setdefault("folders", []).append(new_f)

            self.manager._save()
            return True, f"सफलतापूर्वक {count} कुण्डलियाँ वॉल्ट में पुनर्स्थापित की गईं।", count
        except Exception as e:
            return False, f"आयात त्रुटि: {str(e)}", 0


# Singleton instance
default_vault_service = KundaliVaultService()

