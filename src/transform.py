import pandas as pd


def compute_yoy_qoq(df: pd.DataFrame):
    """Return monthly and quarterly aggregates with YoY/QoQ percentages.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing at least the columns ``date``, ``vehicle_category``,
        ``maker`` and ``registrations``.

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        A tuple with the monthly and quarterly aggregated data.
    """

    # Ensure we don't mutate the input DataFrame
    df = df.copy()

    # Calculate the month start for each record
    df["period"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()

    # Monthly aggregation per maker and category
    monthly = (
        df.groupby(["period", "vehicle_category", "maker"], as_index=False)[
            "registrations"
        ]
        .sum()
        .sort_values(["maker", "vehicle_category", "period"])
    )

    # Year over year percentage change.
    # Using ``shift(12)`` assumes there are 12 consecutive monthly rows for each
    # maker/category combination.  The dataset in this project can have missing
    # months which would result in NaNs even when there is data for the same
    # month in the previous year.  To make the calculation robust we instead
    # align each row with the matching period from the previous year using a
    # merge on the shifted period.

    prev_year = monthly[["maker", "vehicle_category", "period", "registrations"]].copy()
    prev_year["period"] = prev_year["period"] + pd.DateOffset(years=1)
    prev_year = prev_year.rename(columns={"registrations": "registrations_prev_year"})
    monthly = monthly.merge(
        prev_year,
        on=["maker", "vehicle_category", "period"],
        how="left",
    )
    monthly = monthly.sort_values(["maker", "vehicle_category", "period"])
    monthly["yoy_pct"] = (
        (monthly["registrations"] - monthly["registrations_prev_year"]) / monthly["registrations_prev_year"]
        * 100
    ).where(monthly["registrations_prev_year"].ne(0))

    # Quarterly aggregation and QoQ change
    monthly["quarter"] = monthly["period"].dt.to_period("Q").dt.to_timestamp()
    quarterly = (
        monthly.groupby(["quarter", "vehicle_category", "maker"], as_index=False)[
            "registrations"
        ]
        .sum()
        .sort_values(["maker", "vehicle_category", "quarter"])
    )
    quarterly["prev_q_regs"] = (
        quarterly.groupby(["maker", "vehicle_category"])["registrations"].shift(1)
    )
    quarterly["qoq_pct"] = (
        (quarterly["registrations"] - quarterly["prev_q_regs"]) / quarterly["prev_q_regs"]
        * 100
    ).where(quarterly["prev_q_regs"].ne(0))

    return monthly, quarterly


def compute_category_growth(df: pd.DataFrame):
    """Aggregate registrations by vehicle category and compute YoY/QoQ.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing columns ``date``, ``vehicle_category`` and
        ``registrations``.

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        Monthly category totals with YoY percentage and quarterly totals
        with QoQ percentage.
    """

    df = df.copy()
    df["period"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby(["period", "vehicle_category"], as_index=False)["registrations"]
        .sum()
        .sort_values(["vehicle_category", "period"])
    )
    monthly["quarter"] = monthly["period"].dt.to_period("Q").dt.to_timestamp()

    # Similar to ``compute_yoy_qoq`` we avoid ``shift(12)`` to handle missing
    # months.  We join on the period offset by one year which ensures that a
    # YoY value is produced whenever data for the same month in the previous
    # year exists, even if intermediate months are absent.
    prev_year = monthly[["vehicle_category", "period", "registrations"]].copy()
    prev_year["period"] = prev_year["period"] + pd.DateOffset(years=1)
    prev_year = prev_year.rename(columns={"registrations": "prev_year_regs"})
    monthly = monthly.merge(prev_year, on=["vehicle_category", "period"], how="left")
    monthly = monthly.sort_values(["vehicle_category", "period"])
    monthly["yoy_pct"] = (
        (monthly["registrations"] - monthly["prev_year_regs"]) / monthly["prev_year_regs"] * 100
    ).where(monthly["prev_year_regs"].ne(0))

    quarterly = (
        monthly.groupby(["quarter", "vehicle_category"], as_index=False)["registrations"]
        .sum()
        .sort_values(["vehicle_category", "quarter"])
    )
    quarterly["prev_q_regs"] = quarterly.groupby("vehicle_category")["registrations"].shift(1)
    quarterly["qoq_pct"] = (
        (quarterly["registrations"] - quarterly["prev_q_regs"]) / quarterly["prev_q_regs"] * 100
    ).where(quarterly["prev_q_regs"].ne(0))

    return monthly, quarterly

