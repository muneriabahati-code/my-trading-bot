import MetaTrader5 as mt5
import pandas as pd
import time

# connect
mt5.initialize()

symbol = "EURUSD"
lot = 0.01

# function to check open trades
def has_open_trade():
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0

# function to get data
def get_data():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
    df = pd.DataFrame(rates)
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()
    return df

# function to place trade
def place_trade(order_type):
    tick = mt5.symbol_info_tick(symbol)

    if order_type == "buy":
        price = tick.ask
        sl = price - 0.0020   # 20 pips
        tp = price + 0.0040   # 40 pips
        order = mt5.ORDER_TYPE_BUY
    else:
        price = tick.bid
        sl = price + 0.0020
        tp = price - 0.0040
        order = mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123,
        "comment": "Real Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    print(result)

# main loop
while True:
    df = get_data()
    last = df.iloc[-1]

    if not has_open_trade():

        if last['ma20'] > last['ma50']:
            print("BUY SIGNAL")
            place_trade("buy")

        elif last['ma20'] < last['ma50']:
            print("SELL SIGNAL")
            place_trade("sell")

    else:
        print("Trade already open")

    time.sleep(60)  # run every 1 minute