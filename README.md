# FinanceAI — Open Banking Personal Finance Intelligence System

AI-powered personal finance dashboard inspired by UK Open Banking, built using Streamlit, ML, and time-series forecasting to deliver intelligent financial insights.

FinanceAI is a smart money assistant that looks at your bank transactions and helps you understand where your money goes, what bills are coming next, and whether you are likely to run out of money in the future.

Example: If you earn £2,000 a month and spend too much on food and subscriptions, FinanceAI can warn you that your balance may drop below £200 next month, future transactions and suggest saving or cutting unused subscriptions

---

## 🚀 Features

### 🏠 Dashboard
- **Current balance**
- **Income & expense overview**
- **Upcoming predicted payments**
- **Spending breakdown by merchant**
- **Recent transactions**
- **Cash-flow alerts**

### 🤖 AI Insights
- **Savings opportunity detection**
- **Subscription analysis (active vs unused)**
- **Spending pattern alerts**
- **Goal-based balance evaluation**
- **Financial health score**
- **Personalized recommendations**

### 📈 Forecast
- **ARIMA-based balance forecasting**
- **Trend fallback forecasting**
- **Low balance alerts (£200 threshold)**
- **Recurring transaction predictions**
- **Confidence scoring (High / Medium / Low)**

---

## 🧠 AI & Intelligence Logic

### Merchant Normalization
Cleans raw bank descriptions:
- Example: `TESCO STORES 1294` → `Tesco`
- Example: `APPLE.COM/BILL LONDON` → `Apple Services`

### Brand Mapping
- Maps merchants to canonical brands
- Enables subscription & recurring detection

### Recurring Transaction Detection
Uses:
- Date interval consistency
- Amount stability
- Frequency patterns

### Confidence Scoring
- **High** → Very likely to recur
- **Medium** → Probable recurrence
- **Low** → Weak or noisy pattern

### Balance Forecasting
- ARIMA time-series model
- Logistic Regression
- Fallback average-trend logic
- Date-range–dependent accuracy

---

## 🧱 Project Structure

```
open-banking-ml/
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_AI_Insights.py
│   └── 3_Forecast.py
│
├── utils/
│   ├── merchant_utils.py
│   ├── ml_models.py
│   └── styles.py
│
├── bank_transactions.csv
├── requirements.txt
└── README.md
```

---

## 🛠 Tech Stack

- **Python**
- **Streamlit**
- **Pandas / NumPy**
- **Statsmodels (ARIMA)**
- **Plotly**
- **Regex / NLP-style processing**

---

## 📊 Data Simulation

### Open Banking–Style Transactions
- Contactless & online payments
- Merchant noise & IDs
- Subscriptions & bills
- Salary transactions
- Realistic spending intervals

**⚠️ No real bank data is used.**

---

## ▶️ How to Run Locally

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/jainam1810/financeai-open-banking.git
cd financeai-open-banking
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App
```bash
streamlit run pages/1_Dashboard.py
```

---

## ⚠️ Important Notes

### Forecast Sensitivity
- Forecasts change significantly with date range
- More history → more stable predictions

### Scope
- UI & intelligence focused
- No real Open Banking APIs (yet)

---

### User Interface
- https://drive.google.com/file/d/13m88EsBa5mc8n9E_KlV0PIOucQZqB_Rg/view?usp=sharing

## 🔮 Future Enhancements

- Multi-bank selection
- Real Open Banking API integration
- Authentication & user profiles
- Category prediction ML model
- PDF export of insights
- Cloud deployment

For future enhancements we can use BERT / FinBERT for transaction understanding, LSTM(RNN) and XGBoost regressor for forecasting, DBSCAN / HDBSCAN & HMM for Recurring Payments & Subscriptions and few more

---

## 👤 Author

**Jainam Varia**  
Student | FinTech | Data | Machine Learning | AI

Built as a portfolio-grade Open Banking intelligence system.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
