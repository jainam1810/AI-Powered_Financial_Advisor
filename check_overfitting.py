import pandas as pd
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('bank_transactions.csv')
df = df[df['category'] != 'Income'].copy()

print("=" * 60)
print("🔍 OVERFITTING ANALYSIS")
print("=" * 60)

# 1. Check unique merchants
print(f"\n📊 Total transactions: {len(df)}")
print(f"📝 Unique merchant names: {df['description'].nunique()}")
print(f"📂 Number of categories: {df['category'].nunique()}")

# 2. Check if merchants appear in both train/test
X = df['description']
y = df['category']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

train_merchants = set(X_train.unique())
test_merchants = set(X_test.unique())
overlap = train_merchants.intersection(test_merchants)

print(f"\n🔄 Data Leakage Check:")
print(f"   Merchants in training: {len(train_merchants)}")
print(f"   Merchants in test: {len(test_merchants)}")
print(f"   Overlap (same merchants in both): {len(overlap)}")
print(f"   Overlap percentage: {len(overlap)/len(test_merchants)*100:.1f}%")

if len(overlap) == len(test_merchants):
    print("\n   ⚠️  100% OVERLAP! This explains the 100% accuracy.")
    print("   The test set contains ONLY merchants the model has seen!")
    print("   This is NOT overfitting - it's just a very easy problem.")
else:
    print("\n   ✅ Test set has some new merchants (good!)")

# 3. Check merchant-category consistency
print(f"\n🔍 Merchant Ambiguity Check:")
merchant_categories = df.groupby('description')['category'].unique()
ambiguous = merchant_categories[merchant_categories.apply(len) > 1]

if len(ambiguous) > 0:
    print(f"   ⚠️  Found {len(ambiguous)} merchants with multiple categories:")
    for merchant, cats in ambiguous.items():
        print(f"      '{merchant}' → {list(cats)}")
else:
    print("   ✅ Each merchant name maps to exactly ONE category")
    print("   💡 This means 100% accuracy is EXPECTED, not overfitting!")

# 4. Show category distribution
print(f"\n📊 Category Distribution:")
print(df['category'].value_counts())

print("\n" + "=" * 60)
print("💡 VERDICT:")
print("=" * 60)

if len(overlap) == len(test_merchants) and len(ambiguous) == 0:
    print("✅ Your model is NOT overfitted!")
    print("✅ 100% accuracy is correct because:")
    print("   • Each merchant always belongs to the same category")
    print("   • Test merchants were also in training (data leakage)")
    print("   • The problem is essentially memorizing a dictionary")
    print("\n⚠️  However, in REAL banking data:")
    print("   • Merchant names have typos and variations")
    print("   • Same merchant might appear differently")
    print("   • You'd get 85-95% accuracy, not 100%")
else:
    print("⚠️  There might be actual overfitting issues")

print("=" * 60)
