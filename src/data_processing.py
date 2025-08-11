import pandas as pd


def get_key_insight(df: pd.DataFrame) -> str:
    """Return a short insight string based on the latest data.

    The function computes the year-over-year growth for the most recent
    month present in the dataframe and identifies the category with the
    highest registrations in that month.
    """

    if "vehicle_category" in df.columns:
        category_col = "vehicle_category"
    elif "category" in df.columns:
        category_col = "category"
    else:
        raise ValueError("No category column found in dataframe.")

    if "date" not in df.columns:
        raise ValueError("No date column found in dataframe.")

    df = df.copy()
    df["period"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()

    latest_period = df["period"].max()
    prev_year_period = latest_period - pd.DateOffset(years=1)

    latest_total = df[df["period"] == latest_period]["registrations"].sum()
    prev_total = df[df["period"] == prev_year_period]["registrations"].sum()

    yoy_growth = (
        (latest_total - prev_total) / prev_total * 100 if prev_total else float("nan")
    )

    top_category = (
        df[df["period"] == latest_period]
        .groupby(category_col)["registrations"]
        .sum()
        .idxmax()
    )

    growth_str = f"{yoy_growth:.2f}%" if pd.notnull(yoy_growth) else "N/A"
    return (
        f"Year-over-year growth is {growth_str} with {top_category} leading the registrations."
    )

