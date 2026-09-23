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
        tag_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists all saved clients across all folders with optional search query and tag filter.
        """
        folders = self.manager.list_folders()
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
                # Ensure tags & notes exist
                if "tags" not in c_copy:
                    c_copy["tags"] = ["🌟 VIP"] if "VIP" in folder_name else [" सामान्य"]
                if "notes" not in c_copy:
                    c_copy["notes"] = ""

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
        folder_id: int = 0
    ) -> Dict[str, Any]:
        """
        Saves a new client or updates an existing client in the vault.
        """
        tags = tags or [" सामान्य"]
        chart_entry = self.manager.save_chart(folder_id, name, birth_data)
        chart_entry["tags"] = tags
        chart_entry["notes"] = notes

        # Update inside the folder
        for folder in self.manager.data.get("folders", []):
            for ch in folder.get("charts", []):
                if ch.get("id") == chart_entry["id"]:
                    ch["tags"] = tags
                    ch["notes"] = notes
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

    def delete_client(self, client_id: Any) -> bool:
        """Deletes a client chart from all folders and recent list."""
        deleted = False
        for folder in self.manager.data.get("folders", []):
            charts = folder.get("charts", [])
            initial_len = len(charts)
            folder["charts"] = [c for c in charts if c.get("id") != client_id]
            if len(folder["charts"]) < initial_len:
                deleted = True

        recents = self.manager.data.get("recent_charts", [])
        self.manager.data["recent_charts"] = [c for c in recents if c.get("id") != client_id]
        if deleted:
            self.manager._save()
        return deleted

    def export_backup_json(self) -> str:
        """Exports the entire vault database as formatted JSON string."""
        return json.dumps(self.manager.data, indent=2, ensure_ascii=False)

    def import_backup_json(self, json_content: str) -> Tuple[bool, str, int]:
        """
        Imports and merges client charts from JSON string backup.
        """
        try:
            imported_data = json.loads(json_content)
            if not isinstance(imported_data, dict) or "folders" not in imported_data:
                return False, "अमान्य JSON प्रारूप (Invalid Vault Backup Format)", 0

            count = 0
            existing_folders = {f["id"]: f for f in self.manager.data.get("folders", [])}

            for imp_folder in imported_data.get("folders", []):
                f_id = imp_folder.get("id")
                if f_id in existing_folders:
                    target_f = existing_folders[f_id]
                    existing_chart_names = {c.get("name") for c in target_f.get("charts", [])}
                    for ch in imp_folder.get("charts", []):
                        if ch.get("name") not in existing_chart_names:
                            target_f.setdefault("charts", []).append(ch)
                            count += 1
                else:
                    self.manager.data.setdefault("folders", []).append(imp_folder)
                    count += len(imp_folder.get("charts", []))

            self.manager._save()
            return True, f"सफलतापूर्वक {count} कुण्डलियाँ वॉल्ट में पुनर्स्थापित की गईं।", count
        except Exception as e:
            return False, f"आयात त्रुटि: {str(e)}", 0


# Singleton instance
default_vault_service = KundaliVaultService()

