"""
AI Insights Page
Shows smart recommendations and alerts
"""

from utils.merchant_utils import normalize_merchant
from utils.merchant_utils import map_to_brand
from utils.ml_models import forecast_balance_arima
from utils.ml_models import forecast_summary
from utils.ml_models import forecast_balance
from utils.ml_models import detect_recurring_transactions
from utils.ml_models import (
    calculate_savings_opportunity,
    analyze_subscriptions,
    detect_spending_patterns
)
from utils.styles import get_custom_css, format_currency
import streamlit as st
import pandas as pd
import sys
sys.path.append('..')

# Page config
st.set_page_config(
    page_title="AI Insights | FinanceAI",
    page_icon="🤖",
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

df["merchant_clean"] = df["description"].apply(normalize_merchant)
df["brand"] = df["merchant_clean"].apply(map_to_brand)

# Header
st.markdown("<h1 style='margin-bottom: 2rem; color:#1e293b;'>🤖 AI Insights</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;'>Smart recommendations powered by machine learning</p>", unsafe_allow_html=True)

# =========================
# 📅 Date Range Selector
# =========================

st.subheader("📅 Select Date Range")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.date_input(
    "Choose date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter data
filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

st.caption(
    f"Showing insights from {start_date.strftime('%d %b %Y')} "
    f"to {end_date.strftime('%d %b %Y')}"
)

# =========================
# 🎯 Savings Goal (USER INPUT)
# =========================

st.markdown("<h2 style='color:#1e293b;'>🎯 Savings Goal</h2>",
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    goal_amount = st.number_input(
        "Target balance (£)",
        min_value=500,
        step=500,
        value=5000
    )

with col2:
    goal_date = st.date_input(
        "Target date",
        value=pd.Timestamp.today() + pd.Timedelta(days=90)
    )


forecast_df = forecast_balance_arima(filtered_df, days=30)

if forecast_df is None:
    forecast_df = forecast_balance(filtered_df, days=30)


# =========================
# 🔮 Goal Evaluation
# =========================

goal_result = None

if forecast_df is not None and not forecast_df.empty:
    goal_date_ts = pd.to_datetime(goal_date)

    future_row = forecast_df[forecast_df["date"] >= goal_date_ts]

    if not future_row.empty:
        projected_balance = future_row.iloc[0]["balance"]

        goal_result = {
            "projected_balance": projected_balance,
            "achieved": projected_balance >= goal_amount
        }

summary = forecast_summary(forecast_df)

if summary and summary["low_balance_date"]:
    st.warning(
        f"⚠️ Forecast shows your balance may fall below £200 on "
        f"{summary['low_balance_date'].strftime('%d %b')}."
    )
recurring = detect_recurring_transactions(filtered_df)

df["merchant_clean"] = df["description"].apply(normalize_merchant)
df["brand"] = df["merchant_clean"].apply(map_to_brand)

recurring = detect_recurring_transactions(filtered_df)

upcoming = pd.DataFrame()

if recurring is not None and not recurring.empty and forecast_df is not None:
    today = pd.Timestamp.today()
    next_30 = today + pd.Timedelta(days=30)

    upcoming = recurring[
        (recurring["next_date"] >= today) &
        (recurring["next_date"] <= next_30)
    ].copy()

    # Merge forecast balance on date to assess risk
    upcoming["date"] = upcoming["next_date"].dt.normalize()
    forecast_df["date"] = forecast_df["date"].dt.normalize()

    upcoming = upcoming.merge(
        forecast_df,
        on="date",
        how="left"
    )

    upcoming["risk"] = upcoming["balance"] < 200

st.markdown("<h2 style='color:#1e293b;'>🔍 Goal Outcome</h2>",
            unsafe_allow_html=True)

if goal_result:
    if goal_result["achieved"]:
        st.markdown(f"""
        <div class="alert-card alert-success">
            <div style="display:flex; align-items:flex-start;">
                <span class="alert-icon">🎉</span>
                <div>
                    <div class="alert-title">Goal Achievable</div>
                    <div class="alert-text">
                        You are projected to have <strong>{format_currency(goal_result['projected_balance'])}</strong>
                        by <strong>{goal_date.strftime('%d %b %Y')}</strong>,
                        exceeding your goal of <strong>{format_currency(goal_amount)}</strong>.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        shortfall = goal_amount - goal_result["projected_balance"]

        st.markdown(f"""
        <div class="alert-card alert-danger">
            <div style="display:flex; align-items:flex-start;">
                <span class="alert-icon">⚠️</span>
                <div>
                    <div class="alert-title">Goal Not Reached</div>
                    <div class="alert-text">
                        You are projected to have <strong>{format_currency(goal_result['projected_balance'])}</strong>
                        by <strong>{goal_date.strftime('%d %b %Y')}</strong>,
                        which is <strong>{format_currency(shortfall)}</strong> short of your goal.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Not enough forecast data to evaluate your goal.\n"
            "forecast reliability decreases for goals more than 30 days")

# Savings Opportunity
savings_data = calculate_savings_opportunity(filtered_df)
if savings_data['amount'] > 0:
    st.markdown(f"""
    <div class="alert-card alert-success">
        <div style="display: flex; align-items: flex-start;">
            <span class="alert-icon">📈</span>
            <div style="flex: 1;">
                <div class="alert-title">Savings Opportunity</div>
                <div class="alert-text">
                Based on your recent cash flow, you typically keep a buffer after expenses.
                You can safely move <strong>{format_currency(savings_data['amount'])}</strong>
                to savings this month while maintaining a healthy balance.
                </div>
                <div style="margin-top: 1rem;">
                    <button class="custom-button">Transfer to Savings</button>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-card alert-info">
        <div style="display: flex; align-items: flex-start;">
            <span class="alert-icon">💡</span>
            <div>
                <div class="alert-title">Focus on Saving</div>
                <div class="alert-text">
                    Your expenses are close to your income. Try reducing discretionary spending to build savings.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    f"Based on transactions from {start_date.strftime('%d %b %Y')} "
    f"to {end_date.strftime('%d %b %Y')}"
)

st.markdown("<h2 style='color:#1e293b;'>📅 Upcoming Payments (Next 30 Days)</h2>",
            unsafe_allow_html=True)

if not upcoming.empty:
    for _, tx in upcoming.iterrows():
        risk_badge = (
            "<span style='color:#ef4444; font-weight:600;'>⚠️ May cause low balance</span>"
            if tx.get("risk") else
            "<span style='color:#22c55e; font-weight:600;'>Safe</span>"
        )

        st.markdown(f"""
        <div class="alert-card {'alert-danger' if tx.get('risk') else 'alert-success'}">
            <div style="display: flex; align-items: flex-start;">
                <span class="alert-icon">📌</span>
                <div>
                    <div class="alert-title">{tx['brand']} • {tx['category']}</div>
                    <div class="alert-text">
                        Scheduled on <strong>{tx['next_date'].strftime('%d %b')}</strong> • 
                        Amount: <strong>{format_currency(tx['amount'])}</strong><br>
                        {risk_badge}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No upcoming payments detected in the next 30 days.")


# Subscription Analysis
subscriptions = analyze_subscriptions(
    filtered_df.assign(name=filtered_df["brand"])
)
if subscriptions is not None and len(subscriptions) > 0:
    unused = subscriptions[subscriptions['status'] == 'Unused']
    total_yearly = subscriptions['yearly_cost'].sum()
    unused_yearly = unused['yearly_cost'].sum() if len(unused) > 0 else 0
    if len(unused) > 0:
        st.markdown(f"""
        <div class="alert-card alert-warning">
            <div style="display: flex; align-items: flex-start;">
                <span class="alert-icon">🔔</span>
                <div style="flex: 1;">
                    <div class="alert-title">Subscription Alert</div>
                    <div class="alert-text">
                        You have <strong>{len(unused)} unused subscriptions</strong> costing <strong>{format_currency(unused_yearly)}/year</strong>. 
                        Consider canceling to save <strong>{format_currency(unused_yearly)}/year</strong>.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Show subscription details
        st.markdown(
            "<h3 style='color:#1e293b; margin-top: 1.5rem;'>Your Subscriptions</h3>", unsafe_allow_html=True)

        for _, sub in subscriptions.iterrows():
            status_color = '#fecaca' if sub['status'] == 'Unused' else '#d1fae5'
            status_icon = '❌' if sub['status'] == 'Unused' else '✅'

            st.markdown(f"""
            <div class="subscription-item" style="background: {status_color};">
                <div>
                    <div class="subscription-name">{status_icon} {sub['name']}</div>
                    <div class="subscription-price">Last charged {sub['days_since']} days ago</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 700; font-size: 1.1rem;">{format_currency(sub['monthly_cost'])}/mo</div>
                    <div class="subscription-price">{format_currency(sub['yearly_cost'])}/year</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Spending Pattern Detection
patterns = detect_spending_patterns(filtered_df)
if len(patterns) > 0:
    st.markdown("<h3 style='color:#1e293b; margin-top: 1.5rem;'>📊 Spending Pattern Detected</h3>",
                unsafe_allow_html=True)

    for pattern in patterns:
        if pattern['type'] == 'increase':
            icon = '📈'
            alert_type = 'alert-danger'
            message = f"Your <strong>{pattern['category']}</strong> spending increased by <strong>{pattern['change']}%</strong> this month. You're spending {format_currency(pattern['current'])} vs your usual {format_currency(pattern['average'])}."
        else:
            icon = '📉'
            alert_type = 'alert-success'
            message = f"Great job! Your <strong>{pattern['category']}</strong> spending decreased by <strong>{pattern['change']}%</strong> this month."

        st.markdown(f"""
        <div class="alert-card {alert_type}">
            <div style="display: flex; align-items: flex-start;">
                <span class="alert-icon">{icon}</span>
                <div>
                    <div class="alert-title">Spending Pattern Alert</div>
                    <div class="alert-text">{message}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Financial Health Score
st.markdown("<h2 style='color:#1e293b; margin-top: 2rem;'>💪 Financial Health Score</h2>",
            unsafe_allow_html=True)

# Calculate score (0-100)
if savings_data['monthly_income'] > 0:
    savings_rate = (
        (savings_data['monthly_income'] - savings_data['monthly_expenses'])
        / savings_data['monthly_income']
    ) * 100
else:
    savings_rate = 0

score = min(100, max(0, savings_rate * 1.5))  # Simplified scoring

score_color = '#22c55e' if score >= 70 else '#eab308' if score >= 40 else '#ef4444'

st.markdown(f"""
<div class="insight-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 2rem;">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="flex: 1;">
            <div style="font-size: 3rem; font-weight: 700; color: {score_color}; margin-bottom: 0.5rem;">
                {score:.0f}/100
            </div>
            <div style="color: #64748b; font-size: 1.1rem;">
                {'Excellent' if score >= 70 else 'Good' if score >= 40 else 'Needs Improvement'}
            </div>
        </div>
        <div style="font-size: 4rem;">
            {'🌟' if score >= 70 else '👍' if score >= 40 else '💪'}
        </div>
    </div>
    <div class="progress-bar" style="margin-top: 1.5rem; height: 15px;">
        <div class="progress-fill" style="width: {score}%; background: {score_color};"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tips
st.markdown("<h2 style='color:#1e293b; margin-top: 2rem;'>💡 Personalized Tips</h2>",
            unsafe_allow_html=True)

tips = []

if savings_rate < 20:
    tips.append({
        'icon': '🎯',
        'title': 'Increase Your Savings Rate',
        'text': 'Try to save at least 20% of your income. Start small and increase gradually.'
    })

if len(unused) > 0:
    tips.append({
        'icon': '✂️',
        'title': 'Cancel Unused Subscriptions',
        'text': f'You could save {format_currency(unused_yearly)}/year by canceling unused subscriptions.'
    })

top_category = (
    filtered_df[filtered_df['amount'] < 0]
    .groupby('category')['amount']
    .sum()
    .abs()
    .idxmax()
)
tips.append({
    'icon': '📊',
    'title': f'Monitor Your {top_category} Spending',
    'text': f'{top_category} is your largest expense category. Look for ways to optimize.'
})

for tip in tips:
    st.markdown(f"""
    <div class="insight-card">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="font-size: 2rem;">{tip['icon']}</div>
            <div>
                <div style="font-weight: 600; font-size: 1.1rem; color: #1e293b; margin-bottom: 0.5rem;">
                    {tip['title']}
                </div>
                <div style="color: #64748b;">
                    {tip['text']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
