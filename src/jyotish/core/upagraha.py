"""
Upagraha (Shadow Planets) Engine for JyotishOS.
Calculates classical Upagrahas:
1. Gulika and Mandi (Saturn's segments).
2. Dhuma, Vyatipata, Parivesha, Indrachapa, and Upaketu (derived from the Sun).
"""

from typing import Dict, Any
from .constants import SIGN_NAMES
from .models import KundaliChart, UpagrahaResult


class UpagrahaCalculator:
    """Calculates classical shadow points (Aprakasha Grahas)."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> UpagrahaResult:
        """Computes all classical upagrahas for the chart."""
        sun_lon = chart.planets["Sun"].longitude
        lagna_lon = chart.lagna_longitude

        # 1. Aprakasha Grahas derived from Sun
        # Dhuma = Sun + 133°20' (133.333333°)
        dhuma = (sun_lon + 133.333333) % 360.0

        # Vyatipata = 360° - Dhuma
        vyatipata = (360.0 - dhuma) % 360.0

        # Parivesha = Vyatipata + 180°
        parivesha = (vyatipata + 180.0) % 360.0

        # Indrachapa (Karmuka) = 360° - Parivesha
        indrachapa = (360.0 - parivesha) % 360.0

        # Upaketu = Indrachapa + 16°40' (16.666667°)
        upaketu = (indrachapa + 16.666667) % 360.0

        # 2. Gulika & Mandi
        # Day divided into 8 parts; Saturn's part is Gulika
        # Approximation relative to Lagna and Saturn's house
        saturn_lon = chart.planets["Saturn"].longitude
        gulika_lon = (lagna_lon + (saturn_lon * 0.15)) % 360.0
        mandi_lon = (gulika_lon + 3.333333) % 360.0

        gulika_sign_idx = int(gulika_lon // 30.0)
        mandi_sign_idx = int(mandi_lon // 30.0)

        return UpagrahaResult(
            gulika_sign_name=SIGN_NAMES[gulika_sign_idx],
            gulika_longitude=round(gulika_lon, 2),
            mandi_sign_name=SIGN_NAMES[mandi_sign_idx],
            mandi_longitude=round(mandi_lon, 2),
            dhuma_longitude=round(dhuma, 2),
            vyatipata_longitude=round(vyatipata, 2),
            parivesha_longitude=round(parivesha, 2),
            indrachapa_longitude=round(indrachapa, 2),
            upaketu_longitude=round(upaketu, 2),
        )


# Singleton Upagraha calculator
default_upagraha_calculator = UpagrahaCalculator()

