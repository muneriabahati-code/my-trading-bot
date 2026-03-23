import MetaTrader5 as mt5
import pandas as pd
import time
import joblib
import numpy as np
from datetime import datetime

# -------- LOAD AI MODEL --------
print("Loading AI Model...")
try:
    model = joblib.load("model.pkl")
    print("Model loaded successfully!")
except FileNotFoundError:
    print("🚨 ERROR: model.pkl not found!")
    exit()

# -------- SETTINGS --------
SYMBOL = "EURUSD"
LOT_SIZE = 0.01

# -------- INIT --------
if not mt5.initialize():
    print("🚨 MT5 connection failed")
    exit()
print(f"✅ Connected to MT5. Starting automated trading for {SYMBOL}...")

# -------- FUNCTIONS --------
def has_open_trade():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions is not None and len(positions) > 0

def get_ai_data():
    # Pull 100 candles
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 100)
    if rates is None: return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate Features
    df['ma_fast'] = df['close'].rolling(20).mean()
    df['ma_slow'] = df['close'].rolling(50).mean()
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    df.dropna(inplace=True)
    return df

def place_trade(order_type):
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print("🚨 Market closed or tick data unavailable.")
        return

    # 0.0020 is 20 pips (assuming a 4-digit broker, or 200 points on 5-digit)
    if order_type == "BUY":
        price = tick.ask
        sl = price - 0.0020  
        tp = price + 0.0040  
        order = mt5.ORDER_TYPE_BUY
    else:
        price = tick.bid
        sl = price + 0.0020
        tp = price - 0.0040
        order = mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123,
        "comment": "AI Bot Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"🚨 Order Failed: {result.comment}")
    else:
        print(f"✅ TRADE PLACED: {order_type} at {price}")

# -------- MAIN LOOP --------
while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    
    if not has_open_trade():
        df = get_ai_data()
        
        if df is not None and not df.empty:
            last = df.iloc[-1]
            
            # Feed data to AI
            features = np.array([last['rsi'], last['ma_fast'], last['ma_slow']]).reshape(1, -1)
            prediction = model.predict(features)
            
            if prediction[0] == 1:
                print(f"[{current_time}] 🤖 AI SIGNAL: BUY. Executing trade...")
                place_trade("BUY")
            else:
                print(f"[{current_time}] 🤖 AI SIGNAL: SELL. Executing trade...")
                place_trade("SELL")
        else:
            print(f"[{current_time}] ⏳ Waiting for market data...")
            
    else:
        print(f"[{current_time}] 🛡️ Trade already open. Managing risk...")

    # Sleep for 60 seconds before checking the market again
    time.sleep(60)
