cat > src/transform.py << 'EOF'
import pandas as pd

def compute_yoy_qoq(df):
    # Monthly aggregation
    df['period'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly = df.groupby(['period','vehicle_category','maker'])['registrations'].sum().reset_index()
    monthly['period_start'] = monthly['period'].dt.to_timestamp()

    # YoY
    monthly = monthly.sort_values(['maker','vehicle_category','period_start'])
    monthly['registrations_prev_year'] = monthly.groupby(['maker','vehicle_category'])['registrations'].shift(12)
    monthly['yoy_pct'] = (monthly['registrations'] - monthly['registrations_prev_year']) / monthly['registrations_prev_year'] * 100

    # QoQ
    monthly['quarter'] = monthly['period'].dt.to_timestamp().dt.to_period('Q')
    q = monthly.groupby(['quarter','vehicle_category','maker'])['registrations'].sum().reset_index()
    q = q.sort_values(['maker','vehicle_category','quarter'])
    q['prev_q_regs'] = q.groupby(['maker','vehicle_category'])['registrations'].shift(1)
    q['qoq_pct'] = (q['registrations'] - q['prev_q_regs']) / q['prev_q_regs'] * 100

    return monthly, q
EOF
