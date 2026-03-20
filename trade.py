import MetaTrader5 as mt5

mt5.initialize()

symbol = "EURUSD"
lot = 0.01

# get price
price = mt5.symbol_info_tick(symbol).ask

# trade request
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "deviation": 10,
    "magic": 100,
    "comment": "Python trade",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

# send order
result = mt5.order_send(request)

print(result)

mt5.shutdown()