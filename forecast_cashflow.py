import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime, timedelta


def forecast_balance(months_ahead=3):
    """
    Predict account balance in the future
    """

    print("📊 Loading transaction data...")
    df = pd.read_csv('bank_transactions.csv')
    df['date'] = pd.to_datetime(df['date'])

    # Calculate daily balance
    # Start with £1000 in the account
    daily_balance = df.groupby('date')['amount'].sum().cumsum() + 1000

    # Prepare data for Prophet (needs specific column names)
    forecast_df = pd.DataFrame({
        'ds': daily_balance.index,  # ds = datestamp
        'y': daily_balance.values    # y = value to predict
    })

    print(f"✅ Prepared {len(forecast_df)} days of balance history")

    # Train Prophet model
    print("🔮 Training forecasting model...")
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    model.fit(forecast_df)

    # Make future predictions
    future_dates = model.make_future_dataframe(periods=30 * months_ahead)
    forecast = model.predict(future_dates)

    print(f"✅ Forecasted {months_ahead} months ahead")

    # Create visualization
    fig = go.Figure()

    # Historical balance
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['y'],
        mode='lines',
        name='Historical Balance',
        line=dict(color='blue', width=2)
    ))

    # Forecasted balance
    future_forecast = forecast[forecast['ds'] > forecast_df['ds'].max()]
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'],
        y=future_forecast['yhat'],
        mode='lines',
        name='Predicted Balance',
        line=dict(color='orange', width=2, dash='dash')
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'],
        y=future_forecast['yhat_upper'],
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'],
        y=future_forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        name='Confidence Range',
        line=dict(width=0)
    ))

    fig.update_layout(
        title='💰 Account Balance Forecast',
        xaxis_title='Date',
        yaxis_title='Balance (£)',
        hovermode='x unified'
    )

    # Save visualization
    fig.write_html('balance_forecast.html')
    print("✅ Forecast saved to 'balance_forecast.html'")

    # Generate alerts
    print("\n⚠️ Alerts:")
    low_balance_days = future_forecast[future_forecast['yhat'] < 200]
    if len(low_balance_days) > 0:
        first_low = low_balance_days.iloc[0]
        print(
            f"   ⚠️ Balance may drop below £200 on {first_low['ds'].strftime('%Y-%m-%d')}")
    else:
        print("   ✅ Your balance looks healthy!")

    return forecast


if __name__ == "__main__":
    forecast_balance(months_ahead=3)
