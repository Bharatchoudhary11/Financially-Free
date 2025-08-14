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

    top_category = (
        df[df["period"] == latest_period]
        .groupby(category_col)["registrations"]
        .sum()
        .idxmax()
    )

    if prev_total:
        yoy_growth = (latest_total - prev_total) / prev_total * 100
        growth_str = f"{yoy_growth:.2f}%"
        metric = "Year-over-year"
    else:
        prev_month_period = latest_period - pd.DateOffset(months=1)
        prev_month_total = (
            df[df["period"] == prev_month_period]["registrations"].sum()
        )
        mom_growth = (
            (latest_total - prev_month_total) / prev_month_total * 100
            if prev_month_total
            else float("nan")
        )
        growth_str = f"{mom_growth:.2f}%" if pd.notnull(mom_growth) else "N/A"
        metric = "Month-over-month"

    return f"{metric} growth is {growth_str} with {top_category} leading the registrations."


def compute_yoy_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year comparison for each category.

    The function looks at the most recent month in the dataframe and
    compares registrations against the same month in the previous year.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing columns ``date``, ``registrations`` and either
        ``vehicle_category`` or ``category``.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns ``vehicle_category``, ``registrations``,
        ``prev_year_regs`` and ``yoy_pct`` where ``yoy_pct`` is the
        percentage change from the previous year. ``yoy_pct`` will be
        ``NaN`` when data for the prior year is unavailable.
    """

    if "vehicle_category" in df.columns:
        category_col = "vehicle_category"
    elif "category" in df.columns:
        category_col = "category"
    else:
        raise ValueError("No category column found in dataframe.")

    if "date" not in df.columns or "registrations" not in df.columns:
        raise ValueError("DataFrame must contain 'date' and 'registrations' columns.")

    df = df.copy()
    df["period"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()

    latest_period = df["period"].max()
    prev_year_period = latest_period - pd.DateOffset(years=1)

    current = (
        df[df["period"] == latest_period]
        .groupby(category_col)["registrations"]
        .sum()
    )
    previous = (
        df[df["period"] == prev_year_period]
        .groupby(category_col)["registrations"]
        .sum()
    )

    result = (
        pd.DataFrame({
            "registrations": current,
            "prev_year_regs": previous,
        })
        .fillna(0)
    )

    result["yoy_pct"] = (
        (result["registrations"] - result["prev_year_regs"]) / result["prev_year_regs"] * 100
    ).where(result["prev_year_regs"].ne(0))

    result = result.reset_index().rename(columns={category_col: "vehicle_category"})

    return result

