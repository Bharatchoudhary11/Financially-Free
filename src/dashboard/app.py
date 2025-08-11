import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Vehicle Registrations — Investor Dashboard", layout="wide")

DB_PATH = "data/vahan.db"

@st.cache_data
def load_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT date, vehicle_category, maker, registrations FROM registrations", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['registrations'] = pd.to_numeric(df['registrations'], errors='coerce').fillna(0).astype(int)
    df['vehicle_category'] = df['vehicle_category'].astype(str)
    df['maker'] = df['maker'].astype(str)
    df['period'] = df['date'].dt.to_period('M').dt.to_timestamp()
    df['year'] = df['period'].dt.year
    df['month'] = df['period'].dt.month
    return df

def compute_monthly_aggs(df):
    monthly = df.groupby(['period','vehicle_category','maker'], as_index=False)['registrations'].sum()
    monthly = monthly.sort_values(['maker','vehicle_category','period'])
    monthly['registrations_prev_year'] = monthly.groupby(['maker','vehicle_category'])['registrations'].shift(12)
    monthly['yoy_pct'] = (monthly['registrations'] - monthly['registrations_prev_year']) / monthly['registrations_prev_year'] * 100
    monthly['quarter'] = monthly['period'].dt.to_period('Q').dt.to_timestamp()
    q = monthly.groupby(['quarter','vehicle_category','maker'], as_index=False)['registrations'].sum().sort_values(['maker','vehicle_category','quarter'])
    q['prev_q_regs'] = q.groupby(['maker','vehicle_category'])['registrations'].shift(1)
    q['qoq_pct'] = (q['registrations'] - q['prev_q_regs']) / q['prev_q_regs'] * 100
    return monthly, q

df = load_db()

# Sidebar controls
with st.sidebar:
    st.header("Filters")

    min_date = df['period'].min().date()
    max_date = df['period'].max().date()
    date_range = st.date_input(
        "Date range (month granularity)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Handle tuple or single date
    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range, max_date

    vehicle_cats = sorted(df['vehicle_category'].unique().tolist())
    makers_all = sorted(df['maker'].unique().tolist())

    selected_cats = st.multiselect(
        "Vehicle category",
        vehicle_cats,
        default=vehicle_cats,
    )

    selected_makers = st.multiselect(
        "Manufacturers (multi-select)",
        makers_all,
        default=makers_all[:10],
    )

    # CSS to make long multi-selects scrollable
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] .stMultiSelect {
            max-height: 200px;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

mask = (df['period'] >= pd.to_datetime(start_date)) & (df['period'] <= pd.to_datetime(end_date))
mask &= df['vehicle_category'].isin(selected_cats)
mask &= df['maker'].isin(selected_makers)
df_f = df[mask].copy()

if df_f.empty:
    st.warning("No data for the selected filters / date range.")
    st.stop()

monthly, quarterly = compute_monthly_aggs(df_f)

st.title("Vehicle Registrations — Investor Dashboard")
latest_period = df_f['period'].max()
latest_total = int(df_f[df_f['period'] == latest_period]['registrations'].sum())

totals_latest = df_f[df_f['period'] == latest_period].groupby('vehicle_category', as_index=False)['registrations'].sum()
totals_prev_year = df_f[df_f['period'] == (latest_period - pd.DateOffset(years=1))].groupby('vehicle_category', as_index=False)['registrations'].sum()
tot = totals_latest.merge(totals_prev_year, on='vehicle_category', how='left', suffixes=('','_prev'))
tot['yoy_pct'] = (tot['registrations'] - tot['registrations_prev']) / tot['registrations_prev'] * 100

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

st.markdown("---")

# Time series: overall trend
st.subheader("Overall monthly registrations (trend)")
ts = df_f.groupby('period', as_index=False)['registrations'].sum().sort_values('period')

if ts.empty:
    st.info("No data available for overall monthly registrations.")
else:
    ts['period'] = pd.to_datetime(ts['period'])
    chart = alt.Chart(ts).mark_line(point=True).encode(
        x=alt.X('period:T', title='Month'),
        y=alt.Y('registrations:Q', title='Registrations'),
        tooltip=['period:T', 'registrations:Q']
    ).properties(height=300, width=600)  # width must be a number
    st.altair_chart(chart, use_container_width=True)


# Category breakdown (stacked area)
st.subheader("Category-wise monthly trend")
cat_ts = df_f.groupby(['period', 'vehicle_category'], as_index=False)['registrations'].sum()

if cat_ts.empty:
    st.info("No data available for category-wise monthly trend.")
else:
    cat_ts['period'] = pd.to_datetime(cat_ts['period'])
    area = alt.Chart(cat_ts).mark_area().encode(
        x='period:T',
        y='registrations:Q',
        color='vehicle_category:N',
        tooltip=['period:T', 'vehicle_category:N', 'registrations:Q']
    ).properties(height=320)
    st.altair_chart(area, use_container_width=True)

st.subheader(f"Top manufacturers — YoY (%) — latest month {latest_period.strftime('%Y-%m')}")
lm = monthly[monthly['period'] == latest_period].copy()
lm = lm.sort_values('yoy_pct', ascending=False).reset_index(drop=True)
if lm.empty:
    st.write("No monthly manufacturer data for latest period.")
else:
    st.dataframe(lm[['maker','vehicle_category','registrations','registrations_prev_year','yoy_pct']].fillna("N/A").round(2))

st.subheader("Top manufacturers — QoQ (%) — latest quarter")
latest_q = quarterly['quarter'].max()
qq = quarterly[quarterly['quarter'] == latest_q].sort_values('qoq_pct', ascending=False).reset_index(drop=True)
if qq.empty:
    st.write("No quarterly manufacturer data for latest quarter.")
else:
    st.dataframe(qq[['maker','vehicle_category','registrations','prev_q_regs','qoq_pct']].fillna("N/A").round(2))

st.markdown("---")
st.download_button("Download filtered data (CSV)", df_f.to_csv(index=False), file_name="vahan_filtered.csv")

st.markdown("""
**Notes / Next steps**
- This app is DB-first and expects `data/vahan.db` to exist with `registrations` table.
- To populate with live Vahan data we can add a scraper that finds the JSON/XHR endpoints or uses Playwright/Selenium.
""")
