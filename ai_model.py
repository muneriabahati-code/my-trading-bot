import joblib

model = joblib.load("model.pkl")

def predict_trade(rsi, ma_fast, ma_slow):

    prediction = model.predict([[rsi, ma_fast, ma_slow]])

    if prediction[0] == 1:
        return "BUY"
    else:
        return "SELL"