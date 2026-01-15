import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)


# ✅ ADD THIS NEW FUNCTION AT THE TOP
def add_merchant_variation(merchant_name):
    """
    Add realistic variations to merchant names
    This simulates how real bank statements look!

    Example:
    'TESCO STORES' might appear as:
    - 'TESCO STORES'
    - 'TESCO STORES 2341'
    - 'TESCO STORES LONDON'
    - 'TESCOSTORES'
    - 'tesco stores'
    """
    variations = [
        # 40% chance: Keep original (most common)
        lambda x: x,
        lambda x: x,
        lambda x: x,
        lambda x: x,

        # 20% chance: Add store/reference number
        lambda x: f"{x} {random.randint(1000, 9999)}",
        lambda x: f"{x} *{random.randint(100, 999)}",

        # 15% chance: Add location
        lambda x: f"{x} LONDON",
        lambda x: f"{x} UK",
        lambda x: f"{x} MANCHESTER",

        # 10% chance: Formatting changes
        lambda x: x.replace(" ", ""),  # Remove spaces
        lambda x: x.lower(),  # Lowercase

        # 10% chance: Add payment type
        lambda x: f"{x} CONTACTLESS",
        lambda x: f"{x} ONLINE",

        # 5% chance: Truncation (like SMS notifications)
        lambda x: x[:15] + "..." if len(x) > 15 else x,
    ]

    # Pick a random variation
    transform = random.choice(variations)
    return transform(merchant_name)


def generate_transactions(num_months=6):
    """
    Generate realistic UK bank transactions
    Think of this as creating a fake bank statement
    """

    # Define realistic UK merchants and categories
    merchants = {
        'Groceries': [
            'TESCO STORES', 'SAINSBURYS', 'ASDA', 'MORRISONS',
            'WAITROSE', 'LIDL UK', 'ALDI STORES'
        ],
        'Transport': [
            'TFL TRAVEL CHARGE', 'UBER TRIP', 'TRAINLINE',
            'NATIONAL RAIL', 'SHELL PETROL'
        ],
        'Subscriptions': [
            'SPOTIFY UK', 'NETFLIX.COM', 'AMAZON PRIME',
            'APPLE.COM/BILL', 'DISNEY PLUS'
        ],
        'Eating Out': [
            'PRET A MANGER', 'COSTA COFFEE', 'NANDOS',
            'PIZZA EXPRESS', 'GREGGS PLC'
        ],
        'Bills': [
            'BRITISH GAS', 'THAMES WATER', 'EE LIMITED',
            'COUNCIL TAX', 'INTERNET BROADBAND'
        ],
        'Shopping': [
            'AMAZON.CO.UK', 'PRIMARK', 'H&M UK',
            'ZARA UK', 'ARGOS LIMITED'
        ],
        'Income': [
            'PAYROLL ABC LTD', 'SALARY DEPOSIT',
            'FREELANCE PAYMENT'
        ]
    }

    # How much people typically spend in each category
    typical_amounts = {
        'Groceries': (15, 80),      # £15-£80 per shop
        'Transport': (5, 30),        # £5-£30 per trip
        'Subscriptions': (5, 15),    # £5-£15 monthly
        'Eating Out': (8, 40),       # £8-£40 per meal
        'Bills': (30, 150),          # £30-£150 per bill
        'Shopping': (20, 200),       # £20-£200 per purchase
        'Income': (2000, 2500)       # £2000-£2500 salary
    }

    # How often transactions happen per month
    frequency = {
        'Groceries': 12,       # ~3 times per week
        'Transport': 20,       # ~5 times per week
        'Subscriptions': 3,    # Monthly subscriptions
        'Eating Out': 8,       # ~2 times per week
        'Bills': 4,            # Monthly bills
        'Shopping': 5,         # Few times a month
        'Income': 1            # Once a month (salary)
    }

    transactions = []
    start_date = datetime.now() - timedelta(days=30 * num_months)

    # Generate transactions for each month
    for month in range(num_months):
        month_start = start_date + timedelta(days=30 * month)

        # Generate each type of transaction
        for category, merchant_list in merchants.items():
            num_transactions = frequency[category]

            for _ in range(num_transactions):
                # Random date within the month
                day_offset = random.randint(0, 29)
                transaction_date = month_start + timedelta(days=day_offset)

                # Random merchant from this category
                merchant = random.choice(merchant_list)

                # ✅ ADD THIS LINE: Apply realistic variations
                merchant = add_merchant_variation(merchant)

                # Random amount based on category
                min_amt, max_amt = typical_amounts[category]
                amount = round(random.uniform(min_amt, max_amt), 2)

                # Income is positive, expenses are negative
                if category == 'Income':
                    amount = abs(amount)
                else:
                    amount = -abs(amount)

                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'description': merchant,
                    'amount': amount,
                    'category': category  # In real life, we predict this!
                })

    # Create DataFrame (think of it as an Excel spreadsheet)
    df = pd.DataFrame(transactions)
    df = df.sort_values('date').reset_index(drop=True)

    return df


# Generate and save the data
if __name__ == "__main__":
    print("🏦 Generating synthetic bank transactions...")
    print("✨ Now with realistic merchant name variations!")

    # Create 6 months of data
    df = generate_transactions(num_months=6)

    # Save to CSV file (like Excel)
    df.to_csv('bank_transactions.csv', index=False)

    print(f"✅ Generated {len(df)} transactions")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"\n💰 Sample transactions (notice the variations!):")
    print(df.head(20))

    # Show spending by category
    print(f"\n📊 Spending by Category:")
    spending = df[df['amount'] < 0].groupby('category')['amount'].sum()
    print(spending.abs().sort_values(ascending=False))

    # Show merchant variation examples
    print(f"\n🔄 Merchant Variation Examples:")
    print("Here's how the same merchant appears differently:")
    for category in ['Groceries', 'Transport', 'Subscriptions']:
        examples = df[df['category'] ==
                      category]['description'].head(5).tolist()
        print(f"\n{category}:")
        for ex in examples:
            print(f"  • {ex}")
