import streamlit as st
import pandas as pd
import sqlite3
import sys
import os
import altair as alt

# --- Fix imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.data_processing import get_key_insight
from src.transform import compute_yoy_qoq, compute_category_growth

st.set_page_config(page_title="Vehicle Registrations — Investor Dashboard", layout="wide")

DB_PATH = "data/vahan.db"

@st.cache_data
def load_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        "SELECT date, vehicle_category, maker, registrations FROM registrations",
        conn,
    )
    conn.close()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["registrations"] = (
        pd.to_numeric(df["registrations"], errors="coerce").fillna(0).astype(int)
    )
    df["vehicle_category"] = df["vehicle_category"].astype(str)
    df["maker"] = df["maker"].astype(str)
    df["period"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df

# Load data
df = load_db()

# Sidebar filters
with st.sidebar:
    st.header("Filters")

    if df.empty:
        st.error("No data found in the database.")
        st.stop()

    if df['period'].isnull().all():
        st.error("Date data missing or invalid in the database.")
        st.stop()

    min_date = df['period'].min()
    max_date = df['period'].max()

    # Convert pandas timestamps to python dates
    min_date = min_date.date() if pd.notnull(min_date) else None
    max_date = max_date.date() if pd.notnull(max_date) else None

    date_range = st.date_input(
        "Date range (month granularity)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range, max_date

    vehicle_cats = sorted(df['vehicle_category'].unique().tolist())
    makers_all = sorted(df['maker'].unique().tolist())

    selected_cats = st.multiselect("Vehicle category", vehicle_cats, default=vehicle_cats)
    selected_makers = st.multiselect("Manufacturers", makers_all, default=makers_all[:10])

mask = (df['period'] >= pd.to_datetime(start_date)) & (df['period'] <= pd.to_datetime(end_date))
mask &= df['vehicle_category'].isin(selected_cats)
mask &= df['maker'].isin(selected_makers)
df_f = df[mask].copy()

if df_f.empty:
    st.warning("No data for the selected filters / date range.")
    st.stop()

monthly, quarterly = compute_yoy_qoq(df_f)
cat_month, cat_quarter = compute_category_growth(df_f)

# Dashboard header
st.title("Vehicle Registrations — Investor Dashboard")

latest_period = df_f["period"].max()
latest_total = int(df_f[df_f["period"] == latest_period]["registrations"].sum())

c1, c2, c3 = st.columns([2,2,2])
with c1:
    st.metric("Latest month (period)", latest_period.strftime("%Y-%m"))
with c2:
    st.metric("Total registrations (latest month)", f"{latest_total:,}")
with c3:
    total_prev_year = df_f[df_f['period'] == (latest_period - pd.DateOffset(years=1))]['registrations'].sum()
    if total_prev_year > 0:
        total_yoy = round(100 * (latest_total - total_prev_year) / total_prev_year, 2)
        st.metric("Total YoY (%)", f"{total_yoy} %")
    else:
        st.metric("Total YoY (%)", "N/A")

cat_latest = cat_month[cat_month["period"] == latest_period]
st.subheader(f"Category YoY (%) — latest month {latest_period.strftime('%Y-%m')}")
if not cat_latest.empty:
    st.dataframe(
        cat_latest[["vehicle_category", "registrations", "prev_year_regs", "yoy_pct"]]
        .fillna("N/A")
        .round(2)
    )
    # Visualise YoY change per category for quick comparison
    cat_yoy = cat_latest.dropna(subset=["yoy_pct"])
    if not cat_yoy.empty:
        bar = (
            alt.Chart(cat_yoy)
            .mark_bar()
            .encode(
                x=alt.X("vehicle_category:N", title="Category"),
                y=alt.Y("yoy_pct:Q", title="YoY %"),
                tooltip=["vehicle_category", alt.Tooltip("yoy_pct:Q", format=".2f")],
            )
            .properties(height=300)
        )
        st.altair_chart(bar, use_container_width=True)
    else:
        st.info("Not enough data for YoY comparison.")

latest_q = cat_quarter["quarter"].max()
cat_q_latest = cat_quarter[cat_quarter["quarter"] == latest_q]
st.subheader("Category QoQ (%) — latest quarter")
if not cat_q_latest.empty:
    st.dataframe(
        cat_q_latest[["vehicle_category", "registrations", "prev_q_regs", "qoq_pct"]]
        .fillna("N/A")
        .round(2)
    )
    qbar = (
        alt.Chart(cat_q_latest)
        .mark_bar()
        .encode(
            x=alt.X("vehicle_category:N", title="Category"),
            y=alt.Y("qoq_pct:Q", title="QoQ %"),
            tooltip=["vehicle_category", alt.Tooltip("qoq_pct:Q", format=".2f")],
        )
        .properties(height=300)
    )
    st.altair_chart(qbar, use_container_width=True)

st.markdown("---")

# Time series: overall trend
st.subheader("Overall monthly registrations (trend)")
ts = df_f.groupby('period', as_index=False)['registrations'].sum().sort_values('period')
if not ts.empty:
    ts['period'] = pd.to_datetime(ts['period'])
    chart = alt.Chart(ts).mark_line(point=True).encode(
        x=alt.X('period:T', title='Month'),
        y=alt.Y('registrations:Q', title='Registrations'),
        tooltip=['period:T', 'registrations:Q']
    ).properties(height=300, width=600)
    st.altair_chart(chart, use_container_width=True)

# Category breakdown
st.subheader("Category-wise monthly trend")
cat_ts = df_f.groupby(['period', 'vehicle_category'], as_index=False)['registrations'].sum()
if not cat_ts.empty:
    cat_ts['period'] = pd.to_datetime(cat_ts['period'])
    area = alt.Chart(cat_ts).mark_area().encode(
        x='period:T',
        y='registrations:Q',
        color='vehicle_category:N',
        tooltip=['period:T', 'vehicle_category:N', 'registrations:Q']
    ).properties(height=320)
    st.altair_chart(area, use_container_width=True)

# Top manufacturers — YoY
st.subheader(f"Top manufacturers — YoY (%) — latest month {latest_period.strftime('%Y-%m')}")
lm = monthly[monthly['period'] == latest_period].copy().sort_values('yoy_pct', ascending=False)
if not lm.empty:
    st.dataframe(
        lm[
            [
                "maker",
                "vehicle_category",
                "registrations",
                "registrations_prev_year",
                "yoy_pct",
            ]
        ]
        .fillna("N/A")
        .round(2)
    )
    lm_yoy = lm.dropna(subset=["yoy_pct"])
    if not lm_yoy.empty:
        mbar = (
            alt.Chart(lm_yoy)
            .mark_bar()
            .encode(
                x=alt.X("maker:N", title="Manufacturer"),
                y=alt.Y("yoy_pct:Q", title="YoY %"),
                color="vehicle_category:N",
                tooltip=[
                    "maker",
                    "vehicle_category",
                    alt.Tooltip("yoy_pct:Q", format=".2f"),
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(mbar, use_container_width=True)
    else:
        st.info("Not enough data for YoY comparison.")

# Top manufacturers — QoQ
st.subheader("Top manufacturers — QoQ (%) — latest quarter")
qq = quarterly[quarterly['quarter'] == latest_q].sort_values('qoq_pct', ascending=False)
if not qq.empty:
    st.dataframe(
        qq[["maker", "vehicle_category", "registrations", "prev_q_regs", "qoq_pct"]]
        .fillna("N/A")
        .round(2)
    )
    mqbar = (
        alt.Chart(qq)
        .mark_bar()
        .encode(
            x=alt.X("maker:N", title="Manufacturer"),
            y=alt.Y("qoq_pct:Q", title="QoQ %"),
            color="vehicle_category:N",
            tooltip=[
                "maker",
                "vehicle_category",
                alt.Tooltip("qoq_pct:Q", format=".2f"),
            ],
        )
        .properties(height=300)
    )
    st.altair_chart(mqbar, use_container_width=True)

# Download button
st.markdown("---")
st.download_button("Download filtered data (CSV)", df_f.to_csv(index=False), file_name="vahan_filtered.csv")

# Key Investment Insight section
st.markdown("### 📊 Key Investment Insight")
insight = get_key_insight(df_f)
st.success(insight)
