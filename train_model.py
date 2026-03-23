import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

def train_ai():
    print("🧠 Initializing AI Training Sequence...")
    
    # 1. Load Data Safely
    if not os.path.exists("market_data.csv"):
        print("🚨 ERROR: market_data.csv not found!")
        print("Please ensure your historical data file is in the same folder.")
        return
        
    try:
        data = pd.read_csv("market_data.csv")
    except Exception as e:
        print(f"🚨 ERROR loading CSV: {e}")
        return

    # Ensure required columns exist
    required_cols = ["RSI", "MA_FAST", "MA_SLOW", "RESULT"]
    for col in required_cols:
        if col not in data.columns:
            print(f"🚨 ERROR: Missing column '{col}' in CSV.")
            return

    # 2. Prepare Features and Target
    X = data[["RSI", "MA_FAST", "MA_SLOW"]]
    y = data["RESULT"]

    # 3. Split Data (80% train, 20% test)
    # This prevents the AI from "memorizing" the answers and forces it to learn.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"📊 Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")

    # 4. Build the AI Pipeline
    # The Scaler shrinks RSI and MAs to the same mathematical scale automatically.
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000))
    ])

    # 5. Train the Model
    print("⚙️ Training AI model...")
    pipeline.fit(X_train, y_train)

    # 6. Evaluate the Model
    print("🧪 Testing AI against unseen data...")
    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print("\n" + "="*40)
    print(f"🏆 AI ACCURACY: {accuracy * 100:.2f}%")
    print("="*40)
    print("Detailed Report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print("="*40 + "\n")

    # 7. Save the Brain
    joblib.dump(pipeline, "model.pkl")
    print("✅ SUCCESS: 'model.pkl' (Pipeline) saved and ready for live trading!")

if __name__ == "__main__":
    train_ai()
