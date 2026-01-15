"""
Machine Learning utilities for the Finance AI app
Contains all the smart AI logic!
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from statsmodels.tsa.arima.model import ARIMA
from utils.merchant_utils import normalize_merchant, map_to_brand


def load_categorizer():
    """Load the trained ML model"""
    try:
        with open('categorizer_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except FileNotFoundError:
        return None, None


def predict_category(description, model, vectorizer):
    """Predict category for a transaction"""
    if model is None or vectorizer is None:
        return "Unknown"
    prediction = model.predict(vectorizer.transform([description]))[0]
    return prediction


def detect_recurring_transactions(df):
    """
    Detect recurring transactions with confidence scoring
    """

    recurring = []

    for desc in df["description"].unique():
        tx = df[df["description"] == desc].sort_values("date")

        if len(tx) < 2:
            continue

        dates = pd.to_datetime(tx["date"])
        intervals = dates.diff().dt.days.dropna()

        if intervals.empty:
            continue

        avg_interval = intervals.mean()
        std_interval = intervals.std()

        # Must be roughly monthly or consistent
        if not (25 <= avg_interval <= 35 or std_interval < 5):
            continue

        amounts = tx["amount"].abs()
        amount_std_pct = amounts.std() / amounts.mean() if amounts.mean() != 0 else 1

        # ---------- CONFIDENCE ----------
        if len(tx) >= 6 and abs(avg_interval - 30) <= 2 and amount_std_pct < 0.05:
            confidence = "High"
        elif len(tx) >= 3 and abs(avg_interval - 30) <= 4:
            confidence = "Medium"
        else:
            confidence = "Low"

        last_tx = tx.iloc[-1]
        next_date = last_tx["date"] + timedelta(days=int(avg_interval))

        merchant_clean = normalize_merchant(last_tx["description"])
        brand = map_to_brand(merchant_clean)

        if next_date > pd.Timestamp.now():

            recurring.append({
                "description": last_tx["description"],
                "merchant_clean": merchant_clean,
                "brand": brand,
                "category": last_tx["category"],
                "amount": last_tx["amount"],
                "next_date": next_date,
                "confidence": confidence
            })

    return pd.DataFrame(recurring)


def calculate_savings_opportunity(df):
    """
    Calculate how much can safely be moved to savings
    Analyzes cash flow to find safe buffer amount
    """
    # Get income and expenses
    monthly_income = df[df['amount'] > 0].groupby(
        pd.to_datetime(df['date']).dt.to_period('M')
    )['amount'].sum().mean()

    monthly_expenses = abs(df[df['amount'] < 0].groupby(
        pd.to_datetime(df['date']).dt.to_period('M')
    )['amount'].sum().mean())

    # Calculate average surplus
    surplus = monthly_income - monthly_expenses

    # Safe savings = 70% of surplus (keep 30% as buffer)
    safe_savings = max(0, surplus * 0.7)

    return {
        'amount': round(safe_savings, 2),
        'monthly_income': round(monthly_income, 2),
        'monthly_expenses': round(monthly_expenses, 2),
        'surplus': round(surplus, 2)
    }


def analyze_subscriptions(df):
    """
    Analyze subscriptions using canonical merchant (brand)
    """

    if "brand" not in df.columns:
        raise ValueError(
            "brand column missing. Normalize merchants before calling.")

    subs = df[df["category"] == "Subscriptions"].copy()

    if subs.empty:
        return None

    summary = (
        subs.groupby("brand")
        .agg(
            count=("amount", "count"),
            avg=("amount", "mean"),
            last_date=("date", "max")
        )
        .reset_index()
    )

    summary["monthly_cost"] = summary["avg"].abs()
    summary["yearly_cost"] = summary["monthly_cost"] * 12

    summary["last_date"] = pd.to_datetime(summary["last_date"])
    summary["days_since"] = (datetime.now() - summary["last_date"]).dt.days
    summary["status"] = summary["days_since"].apply(
        lambda x: "Unused" if x > 60 else "Active"
    )

    summary.rename(columns={"brand": "name"}, inplace=True)

    return summary.sort_values("yearly_cost", ascending=False)


def detect_spending_patterns(df):
    """
    Detect unusual spending patterns
    Compares current month vs previous months
    """
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')

    # Get current and previous month
    current_month = df['month'].max()
    previous_months = df[df['month'] < current_month]
    current_data = df[df['month'] == current_month]

    alerts = []

    # Analyze by category
    for category in df['category'].unique():
        if category == 'Income':
            continue

        # Current month spending
        current_spending = abs(
            current_data[current_data['category'] == category]['amount'].sum())

        # Average previous spending
        prev_spending = abs(previous_months[previous_months['category'] == category].groupby(
            'month')['amount'].sum().mean())

        if prev_spending > 0:
            change_pct = ((current_spending - prev_spending) /
                          prev_spending) * 100

            # Alert if increased by >20%
            if change_pct > 20:
                alerts.append({
                    'category': category,
                    'change': round(change_pct, 1),
                    'current': round(current_spending, 2),
                    'average': round(prev_spending, 2),
                    'type': 'increase'
                })
            # Alert if decreased by >30% (unusual)
            elif change_pct < -30:
                alerts.append({
                    'category': category,
                    'change': round(abs(change_pct), 1),
                    'current': round(current_spending, 2),
                    'average': round(prev_spending, 2),
                    'type': 'decrease'
                })

    return alerts


def calculate_daily_balance(df):
    """
    Calculate daily account balance
    Used for forecasting
    """
    df['date'] = pd.to_datetime(df['date'])
    daily_balance = df.groupby('date')['amount'].sum(
    ).cumsum() + 1000  # Start with £1000

    return pd.DataFrame({
        'date': daily_balance.index,
        'balance': daily_balance.values
    })


def predict_low_balance_dates(df, threshold=100):
    """
    Predict when balance might drop below threshold
    This is the "cash flow alert" feature!
    """
    balance_df = calculate_daily_balance(df)

    # Simple forecast: assume same spending pattern continues
    last_30_days_change = balance_df['balance'].iloc[-30:].diff().mean()

    current_balance = balance_df['balance'].iloc[-1]
    current_date = balance_df['date'].iloc[-1]

    # Predict next 30 days
    predictions = []
    for i in range(1, 31):
        future_date = current_date + timedelta(days=i)
        predicted_balance = current_balance + (last_30_days_change * i)
        predictions.append({
            'date': future_date,
            'predicted_balance': predicted_balance
        })

    # Find first date below threshold
    pred_df = pd.DataFrame(predictions)
    low_dates = pred_df[pred_df['predicted_balance'] < threshold]

    if len(low_dates) > 0:
        return low_dates.iloc[0]
    return None


def forecast_balance(df, days=30, start_balance=1000):
    """
    Forecast future daily balances based on recent cashflow trend
    Used by both Forecast page & AI Insights
    """

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])

    daily = df.groupby('date')['amount'].sum().sort_index()
    balance = daily.cumsum() + start_balance

    if len(balance) < 30:
        return None

    avg_daily_change = balance.diff().tail(30).mean()

    last_balance = balance.iloc[-1]
    last_date = balance.index[-1]

    forecast = []
    for i in range(1, days + 1):
        forecast.append({
            "date": last_date + timedelta(days=i),
            "balance": last_balance + avg_daily_change * i
        })

    return pd.DataFrame(forecast)


def forecast_balance_arima(balance_df, days=30):
    from statsmodels.tsa.arima.model import ARIMA

    ts = balance_df.set_index("date")["balance"]

    model = ARIMA(ts, order=(1, 1, 1))
    model_fit = model.fit()

    forecast_res = model_fit.get_forecast(steps=days)
    forecast = forecast_res.predicted_mean
    conf_int = forecast_res.conf_int()

    future_dates = pd.date_range(
        ts.index[-1] + pd.Timedelta(days=1),
        periods=days
    )

    return pd.DataFrame({
        "date": future_dates,
        "balance": forecast.values,
        "lower": conf_int.iloc[:, 0].values,
        "upper": conf_int.iloc[:, 1].values
    })


def forecast_summary(forecast_df, threshold=200):
    if forecast_df is None or forecast_df.empty:
        return None

    min_balance = forecast_df["balance"].min()
    low_days = forecast_df[forecast_df["balance"] < threshold]

    return {
        "min_balance": min_balance,
        "low_balance_date": low_days.iloc[0]["date"] if not low_days.empty else None
    }


def forecast_balance_arima(df, days=30):
    """
    Forecast future balance using ARIMA.
    Returns DataFrame with future dates and predicted balance.
    """

    if df is None or len(df) < 30:
        return None

    # Ensure datetime
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Build daily balance series
    daily = (
        df.groupby(df["date"].dt.date)["amount"]
        .sum()
        .cumsum()
    )

    # Start with realistic base balance
    daily = daily + 1000

    # ARIMA requires numeric index
    series = daily.values

    try:
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()

        forecast = model_fit.forecast(steps=days)

    except Exception:
        # Fallback if ARIMA fails
        avg_change = daily.diff().mean()
        last_value = daily.iloc[-1]
        forecast = [last_value + avg_change * i for i in range(1, days + 1)]

    future_dates = [
        daily.index[-1] + pd.Timedelta(days=i)
        for i in range(1, days + 1)
    ]

    return pd.DataFrame({
        "date": pd.to_datetime(future_dates),
        "balance": forecast
    })
