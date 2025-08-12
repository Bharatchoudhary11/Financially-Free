import os
import sys
import pandas as pd

# Ensure src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_processing import get_key_insight


def test_get_key_insight_month_over_month():
    df = pd.DataFrame({
        "date": ["2024-03-01", "2024-04-01"],
        "vehicle_category": ["2W", "2W"],
        "registrations": [100, 150],
    })

    result = get_key_insight(df)
    assert "Month-over-month" in result
    assert "50.00%" in result

