from utils.merchant_utils import map_to_brand
from utils.merchant_utils import normalize_merchant
from utils.ml_models import detect_recurring_transactions
from utils.ml_models import predict_low_balance_dates
from utils.styles import get_custom_css, get_category_icon, get_category_color, format_currency
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.append('..')

# Page config
st.set_page_config(
    page_title="Dashboard | FinanceAI",
    page_icon="🏠",
    layout="wide"
)

# Load custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load data


@st.cache_data
def load_data():
    df = pd.read_csv('bank_transactions.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    return df


df = load_data()

df["merchant_clean"] = df["description"].apply(normalize_merchant)
df["brand"] = df["merchant_clean"].apply(map_to_brand)

predicted_tx = detect_recurring_transactions(df)

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("<h1 style='margin:0; color:#1e293b;'>💼 FinanceAI</h1>",
                unsafe_allow_html=True)

# Date Range Selector

st.subheader("📅 Select Date Range")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.date_input(
    "Choose date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter the data
filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

with col3:
    st.markdown("<div style='text-align:right; padding:10px;'>⚙️ Settings</div>",
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Calculate key metrics (date-aware)

# we added 1000 to make forecasting more better and real, During production we will use curr_balance = bank_APIs
current_balance = filtered_df['amount'].sum() + 1000

range_income = filtered_df[filtered_df['amount'] > 0]['amount'].sum()
range_expenses = abs(filtered_df[filtered_df['amount'] < 0]['amount'].sum())

today = pd.Timestamp.today()

mtd_df = df[df["date"].dt.to_period("M") == today.to_period("M")]

mtd_income = mtd_df[mtd_df["amount"] > 0]["amount"].sum()
mtd_expenses = abs(mtd_df[mtd_df["amount"] < 0]["amount"].sum())


# Big Balance Card
st.markdown(f"""
<div class="balance-card">
    <div class="balance-label">Current Balance</div>
    <div class="balance-amount">{format_currency(current_balance)}</div>
    <div style="display: flex; gap: 2rem; margin-top: 1.5rem;">
        <div class="metric-card" style="flex: 1;">
            <div class="metric-label">Income (Selected Range)</div>
            <div class="metric-value">{format_currency(range_income)}</div>
        </div>
        <div class="metric-card" style="flex: 1;">
        <div class="metric-label">Expenses (Selected Range)</div>
        <div class="metric-value">{format_currency(range_expenses)}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:#1e293b;'>📅 Upcoming Payments</h2>",
            unsafe_allow_html=True)

if predicted_tx is not None and len(predicted_tx) > 0:
    upcoming = predicted_tx.sort_values("next_date").head(5)

    for _, tx in upcoming.iterrows():
        icon = get_category_icon(tx["category"])
        date_str = tx["next_date"].strftime("%d %b")
        amount_color = "#ef4444" if tx["amount"] < 0 else "#22c55e"
        sign = "-" if tx["amount"] < 0 else "+"

        st.markdown(f"""
        <div class="prediction-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>{icon} {tx['brand']} • {tx['category']}</strong><br>
                    <span style="color:#64748b;">{date_str} • {tx['confidence']} confidence</span>
                </div>
                <div style="font-weight:700; color:{amount_color}; font-size:1.2rem;">
                    {sign}{format_currency(tx['amount'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No upcoming payments detected yet.")

if predicted_tx is not None and len(predicted_tx) > 0:
    upcoming_cost = predicted_tx[predicted_tx["amount"] < 0]["amount"].sum()

    st.markdown(f"""
    <div class="alert-card alert-info">
        <div style="display:flex; align-items:center;">
            <span class="alert-icon">⏳</span>
            <div>
                <div class="alert-title">Upcoming Payments</div>
                <div class="alert-text">
                    You have <strong>{len(predicted_tx)}</strong> upcoming payments
                    totaling <strong>{format_currency(abs(upcoming_cost))}</strong>
                    in the next 30 days.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Cash Flow Alert
low_balance = predict_low_balance_dates(filtered_df, threshold=100)
if low_balance is not None:
    alert_date = low_balance['date'].strftime('%d %b')
    st.markdown(f"""
    <div class="alert-card alert-warning">
        <div style="display: flex; align-items: center;">
            <span class="alert-icon">⚠️</span>
            <div>
                <div class="alert-title">Cash Flow Alert</div>
                <div class="alert-text">Your balance may drop below £100 on {alert_date}. Consider moving expenses or transferring funds.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Spending by Category
st.markdown("<h2 style='color:#1e293b;'>📊 Spending by Category</h2>",
            unsafe_allow_html=True)

spending_data = (
    filtered_df[filtered_df['amount'] < 0]
    .groupby('merchant_clean')['amount']
    .sum()
    .abs()
    .sort_values(ascending=False)
    .head(10)
)
max_spending = spending_data.max()

for category, amount in spending_data.items():
    icon = get_category_icon(category)
    percentage = (amount / max_spending) * 100

    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; font-size: 1.1rem;">{icon} {category} </span>
            <span style="font-weight: 700; font-size: 1.1rem;">{format_currency(amount)}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Recent Transactions
st.markdown("<h2 style='color:#1e293b;'>📝 Recent Transactions</h2>",
            unsafe_allow_html=True)

recent = filtered_df.sort_values('date', ascending=False).head(10)

for _, transaction in recent.iterrows():
    icon = get_category_icon(transaction['category'])
    color_class = get_category_color(transaction['category'])
    date_str = pd.to_datetime(transaction['date']).strftime('%d %b')

    amount_color = '#22c55e' if transaction['amount'] > 0 else '#1e293b'
    amount_prefix = '+' if transaction['amount'] > 0 else ''

    st.markdown(f"""
    <div class="transaction-item">
        <div class="transaction-icon {color_class}">{icon}</div>
        <div style="flex: 1;">
            <div style="font-weight: 600; font-size: 1.05rem; color: #1e293b;">{transaction['merchant_clean']}</div>
            <div style="color: #64748b; font-size: 0.9rem;">{transaction['category']} • {date_str}</div>
        </div>
        <div style="font-weight: 700; font-size: 1.2rem; color: {amount_color};">
            {amount_prefix}{format_currency(transaction['amount'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Quick Stats
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#1e293b;'>📈 Quick Stats</h2>",
            unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_transaction = filtered_df[filtered_df['amount'] < 0]['amount'].mean()
    st.markdown(f"""
    <div class="insight-card">
        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Avg Transaction</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b;">{format_currency(avg_transaction)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    transaction_count = len(filtered_df[filtered_df['amount'] < 0])
    st.markdown(f"""
    <div class="insight-card">
        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Total Transactions</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b;">{transaction_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    top_category = spending_data.index[0]
    st.markdown(f"""
    <div class="insight-card">
        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Top Category</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #1e293b;">{get_category_icon(top_category)} {top_category}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    savings_rate = (
        (range_income - range_expenses) / range_income * 100
        if range_income > 0 else 0
    )
    st.markdown(f"""
    <div class="insight-card">
        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Savings Rate</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #22c55e;">{savings_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
