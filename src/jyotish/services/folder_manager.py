"""
Folder and Chart Storage Management Service for JyotishOS.

Manages folder hierarchies, saved birth charts, recent consultations,
10 benchmark demo charts, and automatic synchronization with Grahalakshanam cloud storage.
"""

from typing import Dict, Any, List, Optional
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "saved_charts_db.json")

BENCHMARK_DEMO_CHARTS = [
    {
        "id": 1001,
        "name": "Swami Vivekananda",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Swami Vivekananda",
            "birth_date": "1863-01-12",
            "birth_time": "06:33:00",
            "latitude": 22.5726,
            "longitude": 88.3639,
            "timezone_offset": 5.89,
            "city": "Kolkata, West Bengal",
            "confidence": "Exact"
        }
    },
    {
        "id": 1002,
        "name": "Mahatma Gandhi",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Mahatma Gandhi",
            "birth_date": "1869-10-02",
            "birth_time": "07:12:00",
            "latitude": 21.6417,
            "longitude": 69.6293,
            "timezone_offset": 5.5,
            "city": "Porbandar, Gujarat",
            "confidence": "Exact"
        }
    },
    {
        "id": 1003,
        "name": "Albert Einstein",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Albert Einstein",
            "birth_date": "1879-03-14",
            "birth_time": "11:30:00",
            "latitude": 48.4011,
            "longitude": 9.9876,
            "timezone_offset": 1.0,
            "city": "Ulm, Germany",
            "confidence": "Exact"
        }
    },
    {
        "id": 1004,
        "name": "Dr. APJ Abdul Kalam",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Dr. APJ Abdul Kalam",
            "birth_date": "1931-10-15",
            "birth_time": "01:15:00",
            "latitude": 9.2876,
            "longitude": 79.3129,
            "timezone_offset": 5.5,
            "city": "Rameswaram, Tamil Nadu",
            "confidence": "Exact"
        }
    },
    {
        "id": 1005,
        "name": "Steve Jobs",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Steve Jobs",
            "birth_date": "1955-02-24",
            "birth_time": "19:15:00",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timezone_offset": -8.0,
            "city": "San Francisco, USA",
            "confidence": "Exact"
        }
    },
    {
        "id": 1006,
        "name": "Rabindranath Tagore",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Rabindranath Tagore",
            "birth_date": "1861-05-07",
            "birth_time": "04:05:00",
            "latitude": 22.5726,
            "longitude": 88.3639,
            "timezone_offset": 5.89,
            "city": "Kolkata, West Bengal",
            "confidence": "Exact"
        }
    },
    {
        "id": 1007,
        "name": "Narendra Modi",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Narendra Modi",
            "birth_date": "1950-09-17",
            "birth_time": "11:00:00",
            "latitude": 23.7844,
            "longitude": 72.6394,
            "timezone_offset": 5.5,
            "city": "Vadnagar, Gujarat",
            "confidence": "Exact"
        }
    },
    {
        "id": 1008,
        "name": "Indira Gandhi",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Indira Gandhi",
            "birth_date": "1917-11-19",
            "birth_time": "23:11:00",
            "latitude": 25.4358,
            "longitude": 81.8463,
            "timezone_offset": 5.5,
            "city": "Allahabad, Uttar Pradesh",
            "confidence": "Exact"
        }
    },
    {
        "id": 1009,
        "name": "Amitabh Bachchan",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Amitabh Bachchan",
            "birth_date": "1942-10-11",
            "birth_time": "16:00:00",
            "latitude": 25.4358,
            "longitude": 81.8463,
            "timezone_offset": 5.5,
            "city": "Prayagraj, Uttar Pradesh",
            "confidence": "Exact"
        }
    },
    {
        "id": 1010,
        "name": "Sachin Tendulkar",
        "dateModified": "2026-09-19",
        "birth_data": {
            "name": "Sachin Tendulkar",
            "birth_date": "1973-04-24",
            "birth_time": "16:28:00",
            "latitude": 18.9220,
            "longitude": 72.8347,
            "timezone_offset": 5.5,
            "city": "Mumbai, Maharashtra",
            "confidence": "Exact"
        }
    }
]


class ChartFolderManager:
    """Manages folder hierarchies and saved birth charts."""

    def __init__(self, db_path: str = DEFAULT_STORAGE_PATH):
        self.db_path = os.path.abspath(db_path)
        self.data: Dict[str, Any] = self._load()
        self._ensure_demo_folder()

    def _ensure_demo_folder(self) -> None:
        folders = self.data.setdefault("folders", [])
        demo_f = next((f for f in folders if f["id"] == 100), None)
        if not demo_f:
            demo_f = {
                "id": 100,
                "name": "🌟 10 प्रामाणिक डेमो कुण्डलियाँ",
                "children": [],
                "charts": BENCHMARK_DEMO_CHARTS
            }
            folders.insert(0, demo_f)
            self._save()
        else:
            demo_f["charts"] = BENCHMARK_DEMO_CHARTS
            self._save()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading charts database: {e}")
        return {
            "folders": [
                {"id": 0, "name": "General Charts", "children": [], "charts": []},
                {"id": 1, "name": "Family & Relatives", "children": [], "charts": []},
                {"id": 2, "name": "VIP Consultations", "children": [], "charts": []}
            ],
            "recent_charts": []
        }

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving charts database: {e}")

    def list_folders(self) -> List[Dict[str, Any]]:
        self._ensure_demo_folder()
        return self.data.get("folders", [])

    def create_folder(self, name: str, parent_id: int = 0) -> Dict[str, Any]:
        new_id = int(datetime.now().timestamp())
        folder = {"id": new_id, "name": name, "children": [], "charts": []}
        self.data.setdefault("folders", []).append(folder)
        self._save()
        return folder

    def save_chart(self, folder_id: int, chart_name: str, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        chart_id = int(datetime.now().timestamp())
        chart_entry = {
            "id": chart_id,
            "name": chart_name,
            "dateModified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "birth_data": birth_data
        }

        # Add to matching folder or root folder
        target = next((f for f in self.data.get("folders", []) if f["id"] == folder_id), None)
        if not target and self.data.get("folders"):
            target = self.data["folders"][0]

        if target:
            target.setdefault("charts", []).append(chart_entry)

        # Also add to recent
        recents = self.data.setdefault("recent_charts", [])
        recents.insert(0, chart_entry)
        self.data["recent_charts"] = recents[:15]

        self._save()
        return chart_entry

    def list_recent_charts(self) -> List[Dict[str, Any]]:
        return self.data.get("recent_charts", [])

    def sync_from_grahalakshanam(self, gla_folders_files: Dict[str, Any]) -> int:
        """
        Imports folders and files fetched from Grahalakshanam account into local storage.
        Returns the number of imported charts.
        """
        imported_count = 0
        gla_files = gla_folders_files.get("files", [])

        target_folder = next((f for f in self.data.get("folders", []) if f["name"] == "Grahalakshanam Cloud"), None)
        if not target_folder:
            target_folder = {
                "id": 9999,
                "name": "Grahalakshanam Cloud",
                "children": [],
                "charts": []
            }
            self.data.setdefault("folders", []).append(target_folder)

        for gf in gla_files:
            cid = gf.get("id")
            name = gf.get("name")
            date_mod = gf.get("dateModified", "")
            # check if exists
            exists = any(c.get("id") == cid for c in target_folder.get("charts", []))
            if not exists:
                chart_item = {
                    "id": cid,
                    "name": name,
                    "dateModified": date_mod,
                    "source": "Grahalakshanam",
                    "birth_data": {}
                }
                target_folder.setdefault("charts", []).append(chart_item)
                imported_count += 1

        self._save()
        return imported_count


default_folder_manager = ChartFolderManager()
