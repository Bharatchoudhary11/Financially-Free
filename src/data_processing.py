def get_key_insight(df):
    # Ensure column names match
    if "vehicle_category" in df.columns:
        category_col = "vehicle_category"
    elif "category" in df.columns:
        category_col = "category"
    else:
        raise ValueError("No category column found in dataframe.")

    yoy_growth = (
        df.groupby(category_col)["registrations"]
        .sum()
        .pct_change()
        .iloc[-1]
        * 100
    )
    
    top_category = df.groupby(category_col)["registrations"].sum().idxmax()

    return f"Year-over-year growth is {yoy_growth:.2f}% with {top_category} leading the registrations."
