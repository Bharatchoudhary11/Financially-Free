import pandas as pd
from src.transform import compute_yoy_qoq, compute_category_growth


def test_compute_yoy_qoq_missing_months():
    """YoY should be computed even if intermediate months are absent."""
    df = pd.DataFrame({
        "date": ["2022-01-15", "2023-01-20"],
        "vehicle_category": ["Car", "Car"],
        "maker": ["A", "A"],
        "registrations": [100, 200],
    })
    monthly, _ = compute_yoy_qoq(df)
    res = monthly[monthly["period"] == pd.Timestamp("2023-01-01")]
    assert res["yoy_pct"].iloc[0] == 100.0


def test_compute_category_growth_missing_months():
    """Category YoY should be calculated when same month previous year exists."""
    df = pd.DataFrame({
        "date": ["2022-01-01", "2023-01-01"],
        "vehicle_category": ["Two-Wheeler", "Two-Wheeler"],
        "registrations": [50, 75],
    })
    monthly, _ = compute_category_growth(df)
    res = monthly[monthly["period"] == pd.Timestamp("2023-01-01")]
    assert res["yoy_pct"].iloc[0] == 50.0
