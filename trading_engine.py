import MetaTrader5 as mt5
import pandas as pd
from config import *
from datetime import datetime

# ------------------ INIT ------------------
def initialize():
    if not mt5.initialize():
        print("MT5 initialization failed")
        return False
    return True

# ------------------ ACCOUNT ------------------
def get_balance():
    return mt5.account_info().balance

def calculate_lot(balance):
    risk_amount = balance * (RISK_PERCENT / 100)
    lot = risk_amount / (STOP_LOSS_PIPS * 10)
    return max(round(lot, 2), 0.01)  # minimum lot protection

# ------------------ MARKET DATA ------------------
def get_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
    df = pd.DataFrame(rates)

    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df

# ------------------ CONDITIONS ------------------
def generate_signal():
    df = get_data()
    last = df.iloc[-1]

    if last['ma20'] > last['ma50'] and last['rsi'] < 70:
        return "BUY"

    elif last['ma20'] < last['ma50'] and last['rsi'] > 30:
        return "SELL"

    return None

# ------------------ TRADE CHECK ------------------
def can_trade():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions is None or len(positions) == 0

# ------------------ EXECUTION ------------------
def execute_trade():

    if not initialize():
        return

    if not can_trade():
        log("Trade skipped: already open")
        return

    signal = generate_signal()

    if signal is None:
        log("No signal")
        return

    balance = get_balance()
    lot = calculate_lot(balance)

    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if signal == "BUY" else tick.bid

    sl = price - (STOP_LOSS_PIPS * 0.0001) if signal == "BUY" else price + (STOP_LOSS_PIPS * 0.0001)
    tp = price + (TAKE_PROFIT_PIPS * 0.0001) if signal == "BUY" else price - (TAKE_PROFIT_PIPS * 0.0001)

    order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "UpgradedBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    log(f"{signal} | Lot:{lot} | Price:{price} | SL:{sl} | TP:{tp} | Result:{result}")

# ------------------ LOGGING ------------------
def log(message):
    with open("trades_log.txt", "a") as f:
        f.write(f"{datetime.now()} - {message}\n")