import os
import sys
import pandas as pd

# Ensure src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_processing import get_key_insight, compute_yoy_comparison


def test_get_key_insight_month_over_month():
    df = pd.DataFrame({
        "date": ["2024-03-01", "2024-04-01"],
        "vehicle_category": ["2W", "2W"],
        "registrations": [100, 150],
    })

    result = get_key_insight(df)
    assert "Month-over-month" in result
    assert "50.00%" in result


def test_compute_yoy_comparison():
    df = pd.DataFrame({
        "date": [
            "2023-04-01",
            "2024-04-01",
            "2023-04-01",
            "2024-04-01",
        ],
        "vehicle_category": ["2W", "2W", "4W", "4W"],
        "registrations": [100, 150, 200, 220],
    })

    result = compute_yoy_comparison(df)

    two_wheel = result[result["vehicle_category"] == "2W"].iloc[0]
    four_wheel = result[result["vehicle_category"] == "4W"].iloc[0]

    assert round(two_wheel["yoy_pct"], 2) == 50.0
    assert round(four_wheel["yoy_pct"], 2) == 10.0

