import os
import sys
import pandas as pd

# Ensure src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest import _load_vahan_records


def test_load_vahan_records_csv(tmp_path):
    df = pd.DataFrame({
        "date": ["2025-01-01", "2025-02-01"],
        "vehicle_category": ["2W", "4W"],
        "maker": ["A", "B"],
        "registrations": [100, 200],
    })
    csv_file = tmp_path / "sample.csv"
    df.to_csv(csv_file, index=False)

    records = list(_load_vahan_records(str(csv_file)))
    assert records == [
        ("2025-01-01", "2W", "A", 100),
        ("2025-02-01", "4W", "B", 200),
    ]
