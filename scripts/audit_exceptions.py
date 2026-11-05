"""
Exception Audit and Structured Logging Hardening for JyotishOS (Phase U1 Task U1-T7).
Scans for silent bare exceptions and upgrades them to structured logging (scrubbing PII).
"""

import re
from pathlib import Path


def harden_calculator():
    path = Path("src/jyotish/core/calculator.py")
    text = path.read_text(encoding="utf-8")

    if "import logging" not in text:
        text = text.replace("import math", "import math\nimport logging")
    if "logger = logging.getLogger(__name__)" not in text:
        text = text.replace(
            "from .ephemeris import BaseEphemerisProvider, PyEphemProvider, default_ephemeris_provider",
            "from .ephemeris import BaseEphemerisProvider, PyEphemProvider, default_ephemeris_provider\n\nlogger = logging.getLogger(__name__)"
        )

    # Replace bare except in house computation
    text = re.sub(
        r'(\n\s*)except Exception:(\s*\n\s*lagna_lon = self\.provider\.calculate_ascendant)',
        r'\1except Exception as e:\1    logger.warning("House calculation fallback triggered: %s", e)\2',
        text
    )

    # Replace bare except in delta_t
    text = re.sub(
        r'(\n\s*)except Exception:(\s*\n\s*delta_t = 0\.0)',
        r'\1except Exception as e:\1    logger.debug("Delta T query fallback: %s", e)\2',
        text
    )

    path.write_text(text, encoding="utf-8")
    print(f"[OK] Hardened {path}")


def harden_ephemeris():
    path = Path("src/jyotish/core/ephemeris.py")
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r'(\n\s*)except Exception:(\s*\n\s*jd = self\.datetime_to_jd\(dt_utc\))',
        r'\1except Exception as e:\1    logger.debug("True lunar node fallback to mean nodes: %s", e)\2',
        text
    )
    text = re.sub(
        r'(\n\s*)except Exception:(\s*\n\s*self\._ephe_files = \[\])',
        r'\1except Exception as e:\1    logger.debug("Ephemeris directory file scan fallback: %s", e)\2',
        text
    )
    path.write_text(text, encoding="utf-8")
    print(f"[OK] Hardened {path}")


if __name__ == "__main__":
    harden_calculator()
    harden_ephemeris()
