import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

# Load data
data = pd.read_csv("market_data.csv")

X = data[["RSI", "MA_FAST", "MA_SLOW"]]
y = data["RESULT"]

# Train model
model = LogisticRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved!")