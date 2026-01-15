"""
Main App Entry Point
This is the home page with navigation to other pages
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styles import get_custom_css, format_currency

# Page config
st.set_page_config(
    page_title="FinanceAI - Open Banking Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load data


@st.cache_data
def load_data():
    try:
        df = pd.read_csv('bank_transactions.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        return df
    except FileNotFoundError:
        st.error(
            "⚠️ No transaction data found! Please run `python generate_data.py` first.")
        st.stop()


df = load_data()

# Hero Section
st.markdown("""
<div style="text-align: center; padding: 3rem 0 2rem 0;">
    <h1 style="font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #6e4982 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">
        Finance AI
    </h1>
    <p style="font-size: 1.3rem; color: #64748b; max-width: 600px; margin: 0 auto;">
        Your AI-powered personal financial advisor powered by Open Banking
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation Cards
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <a href="/Dashboard" target="_self" style="text-decoration: none;">
        <div class="insight-card" style="text-align: center; padding: 2rem; cursor: pointer; 
                    transition: all 0.3s; border: 2px solid transparent;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🏠</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Dashboard</h3>
            <p style="color: #64748b; margin: 0;">View your financial overview and recent transactions</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href="/AI_Insights" target="_self" style="text-decoration: none;">
        <div class="insight-card" style="text-align: center; padding: 2rem; cursor: pointer; 
                    transition: all 0.3s; border: 2px solid transparent;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">AI Insights</h3>
            <p style="color: #64748b; margin: 0;">Get smart recommendations and spending alerts</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <a href="/Forecast" target="_self" style="text-decoration: none;">
        <div class="insight-card" style="text-align: center; padding: 2rem; cursor: pointer; 
                    transition: all 0.3s; border: 2px solid transparent;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Forecast</h3>
            <p style="color: #64748b; margin: 0;">Predict future balance and upcoming payments</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Quick Stats
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color:#1e293b; margin-bottom: 2rem;'>📊 Quick Overview</h2>",
            unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

current_balance = df['amount'].sum() + 1000
total_income = df[df['amount'] > 0]['amount'].sum()
total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
transaction_count = len(df)

with col1:
    st.markdown(f"""
    <div class="insight-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div style="text-align: center;">
            <div style="opacity: 0.9; font-size: 0.9rem; margin-bottom: 0.5rem;">Current Balance</div>
            <div style="font-size: 2.2rem; font-weight: 700;">{format_currency(current_balance)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Total Income</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #22c55e;">{format_currency(total_income)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Total Expenses</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #ef4444;">{format_currency(total_expenses)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">Transactions</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #667eea;">{transaction_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Spending Chart
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color:#1e293b; margin-bottom: 1.5rem;'>📈 Spending Over Time</h2>",
            unsafe_allow_html=True)

monthly_spending = df[df['amount'] < 0].groupby(
    'month')['amount'].sum().abs().reset_index()
monthly_spending.columns = ['Month', 'Amount']

fig = px.bar(
    monthly_spending,
    x='Month',
    y='Amount',
    title='',
    color='Amount',
    color_continuous_scale=['#667eea', '#764ba2']
)

fig.update_layout(
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# Features Section
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color:#1e293b; margin-bottom: 2rem;'>✨ Features</h2>",
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Smart Categorization</h4>
            <p style="color: #64748b; font-size: 0.95rem;">
                AI automatically categorizes your transactions with 95%+ accuracy using NLP
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔮</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Cash Flow Prediction</h4>
            <p style="color: #64748b; font-size: 0.95rem;">
                Predicts your future balance and warns you about potential low-balance situations
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="insight-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💡</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Personalized Insights</h4>
            <p style="color: #64748b; font-size: 0.95rem;">
                Identifies savings opportunities, subscription waste, and spending patterns
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #64748b; border-top: 1px solid #e5e7eb; margin-top: 3rem;">
    <p style="margin: 0;">Built with ❤️ using Open Banking APIs, Scikit-Learn, Prophet & Streamlit</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
        🔒 Your data is secure and never shared with third parties
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar (hidden but accessible)
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Stats")
    st.metric("Total Transactions", len(df))
    st.metric("Current Balance", format_currency(current_balance))

    st.markdown("## 🏦 Accounts")

    selected_bank = st.radio(
        "",
        ["Ⓜ️ Monzo", "🐎 Lloyds"],
        index=0
    )
