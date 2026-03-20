import MetaTrader5 as mt5
import pandas as pd

mt5.initialize()

symbol = "EURUSD"
lot = 0.01

# get market data
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)

df = pd.DataFrame(rates)

# calculate moving averages
df['ma10'] = df['close'].rolling(10).mean()
df['ma20'] = df['close'].rolling(20).mean()

# get latest values
last = df.iloc[-1]

# get price
price = mt5.symbol_info_tick(symbol).ask

# BUY condition
if last['ma10'] > last['ma20']:
    print("BUY SIGNAL")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 10,
        "magic": 100,
        "comment": "MA Buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    mt5.order_send(request)

# SELL condition
elif last['ma10'] < last['ma20']:
    print("SELL SIGNAL")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": 10,
        "magic": 100,
        "comment": "MA Sell",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    mt5.order_send(request)

mt5.shutdown()