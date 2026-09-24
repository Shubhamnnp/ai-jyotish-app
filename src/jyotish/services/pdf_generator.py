"""
Direct 1-Click Native PDF Engine for Vedic Kundali Reports.
Converts publication-grade HTML Kundali dossiers into genuine, high-fidelity
printable PDF documents using Chromium/Edge headless engine, with automated
fallbacks for cross-platform and cloud environments.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import logging
from typing import Optional, Dict, Any

from ..core.models import KundaliChart
from .report_generator import default_report_generator
from .master_calculator import default_master_calculator

logger = logging.getLogger(__name__)


class NativePDFService:
    """Enterprise-grade Native PDF Generator for Kundali Dossiers."""

    def __init__(self):
        self._cached_browser_path: Optional[str] = None

    def find_browser_executable(self) -> Optional[str]:
        """Locates Chromium/Edge executable across Windows, Linux, and macOS."""
        if self._cached_browser_path and os.path.exists(self._cached_browser_path):
            return self._cached_browser_path

        # 1. Explicit Environment Variables
        env_vars = ["CHROME_BIN", "EDGE_BIN", "PUPPETEER_EXECUTABLE_PATH", "CHROMIUM_PATH"]
        for ev in env_vars:
            p = os.environ.get(ev)
            if p and os.path.exists(p):
                self._cached_browser_path = p
                return p

        # 2. Windows Default Locations
        if sys.platform == "win32":
            win_candidates = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            ]
            for candidate in win_candidates:
                if os.path.exists(candidate):
                    self._cached_browser_path = candidate
                    return candidate

        # 3. PATH search via shutil.which (Linux / Docker / Mac / Cloud)
        cli_names = [
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
            "msedge",
            "chrome",
        ]
        for name in cli_names:
            w = shutil.which(name)
            if w and os.path.exists(w):
                self._cached_browser_path = w
                return w

        # 4. Standard Linux / Docker paths
        linux_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/chromium",
        ]
        for lp in linux_paths:
            if os.path.exists(lp):
                self._cached_browser_path = lp
                return lp

        # 5. macOS paths
        mac_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
        for mp in mac_paths:
            if os.path.exists(mp):
                self._cached_browser_path = mp
                return mp

        return None

    def html_to_pdf_bytes(
        self,
        html_content: str,
        landscape: bool = False,
        timeout_sec: int = 60,
    ) -> Optional[bytes]:
        """Converts raw HTML string into PDF binary bytes using headless Chromium."""
        browser_bin = self.find_browser_executable()
        if not browser_bin:
            logger.warning("No Chromium/Edge browser binary found for headless PDF generation.")
            # Fallback to Playwright if installed
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.set_content(html_content, wait_until="networkidle")
                    pdf_bytes = page.pdf(
                        format="A4",
                        print_background=True,
                        landscape=landscape,
                        margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"}
                    )
                    browser.close()
                    return pdf_bytes
            except Exception as e_pw:
                logger.error(f"Playwright PDF fallback failed: {e_pw}")

            # Fallback to WeasyPrint if installed
            try:
                from weasyprint import HTML
                return HTML(string=html_content).write_pdf()
            except Exception as e_wp:
                logger.error(f"WeasyPrint fallback failed: {e_wp}")

            return None

        temp_html = None
        temp_pdf = None
        try:
            # Create temporary file with absolute path
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as f:
                f.write(html_content)
                temp_html = os.path.abspath(f.name)

            temp_pdf = os.path.abspath(temp_html.rsplit(".", 1)[0] + ".pdf")

            cmd = [
                browser_bin,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-pdf-header-footer",
                f"--print-to-pdf={temp_pdf}",
            ]
            if landscape:
                cmd.append("--landscape")
            cmd.append(temp_html)

            # Windows-specific startupinfo to prevent console popup
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                startupinfo=startupinfo,
            )

            if proc.returncode == 0 and os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                with open(temp_pdf, "rb") as pf:
                    pdf_data = pf.read()
                return pdf_data
            else:
                err_msg = proc.stderr.decode("utf-8", errors="ignore")
                logger.error(f"Headless PDF conversion failed (code {proc.returncode}): {err_msg}")
                return None

        except Exception as exc:
            logger.error(f"Exception during PDF rendering: {exc}")
            return None
        finally:
            # Safe cleanup of temporary files
            if temp_html and os.path.exists(temp_html):
                try:
                    os.remove(temp_html)
                except Exception:
                    pass
            if temp_pdf and os.path.exists(temp_pdf):
                try:
                    os.remove(temp_pdf)
                except Exception:
                    pass

    def generate_kundali_pdf(
        self,
        chart: KundaliChart,
        master_data: Optional[Dict[str, Any]] = None,
        astro_name: str = "ज्योतिषाचार्य पं. शुभम तिवारी",
        astro_phone: str = "+91-9452155742",
        astro_org: str = "वैदिक ज्योतिष अनुसंधान केंद्र",
        timeout_sec: int = 90,
    ) -> Optional[bytes]:
        """Direct 1-Click generation of full Kundali PDF from KundaliChart."""
        if master_data is None:
            master_data = default_master_calculator.calculate_all(chart)

        html_content = default_report_generator.generate_html_report(
            chart,
            master_data=master_data,
            astro_name=astro_name,
            astro_phone=astro_phone,
            astro_org=astro_org,
        )

        return self.html_to_pdf_bytes(html_content, timeout_sec=timeout_sec)


# Global Singleton
default_pdf_service = NativePDFService()
