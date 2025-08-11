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

    # Year over year percentage change
    monthly["registrations_prev_year"] = (
        monthly.groupby(["maker", "vehicle_category"])["registrations"].shift(12)
    )
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
    df["quarter"] = df["period"].dt.to_period("Q").dt.to_timestamp()

    monthly = (
        df.groupby(["period", "vehicle_category"], as_index=False)["registrations"]
        .sum()
        .sort_values(["vehicle_category", "period"])
    )
    monthly["prev_year_regs"] = monthly.groupby("vehicle_category")["registrations"].shift(12)
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

