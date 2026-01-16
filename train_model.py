import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import pickle


def train_transaction_categorizer():

    print("📚 Loading transaction data...")
    df = pd.read_csv('bank_transactions.csv')

    # Remove income transactions (we only categorize spending)
    df = df[df['category'] != 'Income'].copy()

    print(f"✅ Loaded {len(df)} transactions")
    print(f"📊 Categories: {df['category'].unique()}")

    # Step 1: Prepare the text (X) and labels (y)
    X = df['description']  # What the bank shows
    y = df['category']      # What it actually is

    # Step 2: Split into training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\n📖 Training on {len(X_train)} transactions")
    print(f"🧪 Testing on {len(X_test)} transactions")

    # Step 3: Convert text to numbers
    print("\n🔤 Converting text to numbers...")
    vectorizer = TfidfVectorizer(
        max_features=100,  # Use top 100 most important words
        ngram_range=(1, 2)  # Look at 1-word and 2-word phrases
    )

    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)

    # Step 4: Train the model
    print("🧠 Training the ML model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_vectorized, y_train)

    # Step 5: Test how good it is
    print("\n✅ Testing the model...")
    y_pred = model.predict(X_test_vectorized)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n🎯 Accuracy: {accuracy * 100:.2f}%")
    print("\n📊 Detailed Performance:")
    print(classification_report(y_test, y_pred))

    # Step 6: Save the model
    print("\n💾 Saving the model...")
    with open('categorizer_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    print("✅ Model saved successfully!")

    # Step 7: Test with real examples
    print("\n🧪 Testing with example transactions:")
    test_examples = [
        "TESCO STORES LONDON",
        "TFL TRAVEL CHARGE",
        "SPOTIFY UK SUBSCRIPTION",
        "NANDOS RESTAURANT"
    ]

    for example in test_examples:
        prediction = model.predict(vectorizer.transform([example]))[0]
        print(f"  '{example}' → {prediction}")


if __name__ == "__main__":
    train_transaction_categorizer()
