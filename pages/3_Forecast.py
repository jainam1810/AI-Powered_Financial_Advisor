
from utils.merchant_utils import map_to_brand
from utils.merchant_utils import normalize_merchant
from utils.ml_models import forecast_balance_arima
from utils.ml_models import forecast_balance
from utils.ml_models import detect_recurring_transactions, calculate_daily_balance
from utils.styles import get_custom_css, format_currency, get_category_icon
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.append('..')

# Page config
st.set_page_config(
    page_title="Forecast | FinanceAI",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load data


@st.cache_data
def load_data():
    df = pd.read_csv('bank_transactions.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df


df = load_data()

# Header
st.markdown("<h1 style='margin-bottom: 2rem; color:#1e293b;'>📈 Cash Flow Forecast</h1>",
            unsafe_allow_html=True)


# History Window Selector


st.subheader("📅 Select History Window")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.date_input(
    "Use transactions from",
    value=(max_date - pd.Timedelta(days=90), max_date),
    min_value=min_date,
    max_value=max_date
)

history_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

st.caption(
    f"Forecast based on data from {start_date.strftime('%d %b %Y')} "
    f"to {end_date.strftime('%d %b %Y')}\n"
    "\nAdvice - For better results, choose the recent 90 days window"
)

forecast_days = st.slider(
    "Forecast horizon (days)",
    min_value=7,
    max_value=90,
    value=30,
    step=7
)

# Get balance data
balance_df = calculate_daily_balance(history_df)
current_balance = balance_df['balance'].iloc[-1]
current_date = balance_df['date'].iloc[-1]


forecast_df = forecast_balance_arima(history_df, days=forecast_days)

if forecast_df is None:
    st.warning("Not enough data for ML forecast. Using simple trend instead.")
    forecast_df = forecast_balance(history_df, days=forecast_days)


if forecast_df is None or forecast_df.empty:
    st.warning("Not enough data to generate forecast.")
    st.stop()

future_dates = forecast_df["date"]
future_balances = forecast_df["balance"].values

end_of_month_balance = future_balances[-1]

# Top metrics
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 15px; color: white;">
        <div style="font-size: 0.9rem; opacity: 0.9;">Current Balance</div>
        <div style="font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem;">
            {format_currency(current_balance)}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    balance_change = end_of_month_balance - current_balance
    change_color = '#22c55e' if balance_change > 0 else '#ef4444'
    change_icon = '📈' if balance_change > 0 else '📉'

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); 
                padding: 1.5rem; border-radius: 15px; color: white;">
        <div style="font-size: 0.9rem; opacity: 0.9;">End of Month (Predicted)</div>
        <div style="font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem;">
            {format_currency(end_of_month_balance)}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Predicted Balance Chart
st.markdown("<h2 style='color:#1e293b;'>Predicted Balance</h2>",
            unsafe_allow_html=True)

fig = go.Figure()

# Historical data
fig.add_trace(go.Scatter(
    x=balance_df['date'].iloc[-60:],
    y=balance_df['balance'].iloc[-60:],
    mode='lines',
    name='Historical',
    line=dict(color='#667eea', width=3),
    hovertemplate='%{y:,.2f}<extra></extra>'
))

# Forecast (ML ARIMA or fallback)
fig.add_trace(go.Scatter(
    x=forecast_df["date"],
    y=forecast_df["balance"],
    mode='lines',
    name='Predicted (ML)',
    line=dict(color='#22c55e', width=3, dash='dash'),
    hovertemplate='%{y:,.2f}<extra></extra>'
))

# Low balance threshold line
fig.add_hline(
    y=200,
    line_dash="dot",
    line_color="red",
    annotation_text="Low Balance Alert (£200)",
    annotation_position="right"
)

# Find if balance goes below threshold
low_balance_dates = [i for i, bal in enumerate(future_balances) if bal < 200]
if low_balance_dates:
    first_low = low_balance_dates[0]
    bal = future_balances[first_low]
    bal_text = f"-£{abs(bal):,.2f}" if bal < 0 else f"£{bal:,.2f}"
    fig.add_annotation(
        x=future_dates[first_low],
        y=future_balances[first_low],

        text=(
            f"Low Balance<br>"
            f"{future_dates[first_low].strftime('%d %b')}: {bal_text}"
        ),
        showarrow=True,
        arrowhead=2,
        bgcolor="rgba(239, 68, 68, 0.8)",
        font=dict(color='white', size=12),
        bordercolor='white',
        borderwidth=2,
        borderpad=4,
        arrowcolor='red'
    )

fig.update_layout(
    height=450,
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        title='Date'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        title='Balance (£)'
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# Low balance alert
if low_balance_dates:
    alert_date = future_dates[low_balance_dates[0]].strftime('%d %b')
    alert_balance = future_balances[low_balance_dates[0]]

    st.markdown(f"""
    <div class="alert-card alert-danger">
        <div style="display: flex; align-items: flex-start;">
            <span class="alert-icon">⚠️</span>
            <div>
                <div class="alert-title">Low Balance Alert</div>
                <div class="alert-text">
                    Your balance is predicted to drop to <strong>{format_currency(alert_balance)}</strong> on <strong>{alert_date}</strong>.
                    Consider postponing non-essential purchases or transferring funds.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Predicted Transactions
st.markdown("<h2 style='color:#1e293b;'>📅 Predicted Transactions</h2>",
            unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; margin-bottom: 1.5rem;'>Based on your recurring payment patterns</p>",
            unsafe_allow_html=True)

history_df["merchant_clean"] = history_df["description"].apply(
    normalize_merchant)
history_df["brand"] = history_df["merchant_clean"].apply(map_to_brand)

recurring = detect_recurring_transactions(history_df)


# Resolve recurring amount column safely
if not recurring.empty:
    if "monthly_cost" in recurring.columns:
        amount_col = "monthly_cost"
    elif "amount" in recurring.columns:
        amount_col = "amount"
    else:
        st.error(
            f"Recurring transactions missing amount column. "
            f"Available columns: {list(recurring.columns)}"
        )
        st.stop()

if len(recurring) > 0:
    # Sort by next date
    recurring = recurring.sort_values('next_date')

    for _, trans in recurring.iterrows():
        icon = get_category_icon(trans['category'])
        date_str = trans['next_date'].strftime('%d %b')

        amount = trans[amount_col]
        # Determine card color based on amount
        if amount > 0:
            card_style = "border-left: 4px solid #22c55e;"
            amount_color = "#22c55e"
            amount_prefix = "+"
        else:
            card_style = "border-left: 4px solid #667eea;"
            amount_color = "#1e293b"
            amount_prefix = ""

        confidence_badge = f"""
        <span style="background: {'#22c55e' if trans['confidence'] == 'High' else '#eab308'}; 
                     color: white; padding: 0.25rem 0.75rem; border-radius: 20px; 
                     font-size: 0.8rem; font-weight: 600;">
            {trans['confidence']} confidence
        </span>
        """

        st.markdown(f"""
        <div class="prediction-card" style="{card_style}">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div>
                        <div class="prediction-title">{trans['brand']} • {trans['category']}</div>
                        <div class="prediction-date">{date_str} • {confidence_badge}</div>
                    </div>
                </div>
                <div class="prediction-amount" style="color: {amount_color};">
                    {amount_prefix}{format_currency(amount)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No recurring transactions detected yet. Keep using the app to build prediction patterns!")

# Summary insights
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#1e293b;'>💡 Forecast Insights</h2>",
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    income_df = history_df[history_df["amount"] > 0]

    predicted_income = (
        income_df
        .groupby(income_df["date"].dt.to_period("M"))["amount"]
        .sum()
        .mean()
        if not income_df.empty
        else 0
    )
    st.markdown(f"""
    <div class="insight-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">💰</div>
            <div>
                <div style="color: #15803d; font-size: 0.9rem;">Expected Income</div>
                <div style="font-size: 2rem; font-weight: 700; color: #15803d;">
                    {format_currency(predicted_income)}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    predicted_expenses = (
        abs(recurring[recurring[amount_col] < 0][amount_col].sum())
        if not recurring.empty
        else 0
    )
    st.markdown(f"""
    <div class="insight-card" style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">💸</div>
            <div>
                <div style="color: #991b1b; font-size: 0.9rem;">Expected Expenses</div>
                <div style="font-size: 2rem; font-weight: 700; color: #991b1b;">
                    {format_currency(predicted_expenses)}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
