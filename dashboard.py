import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# -------- SETTINGS --------
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAME = mt5.TIMEFRAME_M5

# -------- INIT --------
if not mt5.initialize():
    st.error("MT5 not connected")
    st.stop()

st.set_page_config(layout="wide")
st.title("🚀 PRO Trading Dashboard")

# -------- ACCOUNT INFO --------
account = mt5.account_info()

col1, col2, col3 = st.columns(3)

col1.metric("Balance", f"{account.balance:.2f}")
col2.metric("Equity", f"{account.equity:.2f}")
col3.metric("Open Trades", mt5.positions_total())

st.divider()

# -------- FUNCTION --------
def get_data(symbol):
    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 200)
    if rates is None:
        return None

    df = pd.DataFrame(rates)
    if df.empty:
        return None

    df['time'] = pd.to_datetime(df['time'], unit='s')

    # indicators
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()

    return df

def get_signal(df):
    last = df.iloc[-1]

    if last['ma20'] > last['ma50']:
        return "BUY"
    elif last['ma20'] < last['ma50']:
        return "SELL"
    return "WAIT"

# -------- CHART GRID --------
cols = st.columns(len(SYMBOLS))

for i, symbol in enumerate(SYMBOLS):
    with cols[i]:

        st.subheader(symbol)

        df = get_data(symbol)

        if df is None:
            st.warning("No data")
            continue

        signal = get_signal(df)

        # signal color
        if signal == "BUY":
            st.success("BUY SIGNAL")
        elif signal == "SELL":
            st.error("SELL SIGNAL")
        else:
            st.info("WAIT")

        # chart
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ))

        fig.add_trace(go.Scatter(x=df['time'], y=df['ma20'], name="MA20"))
        fig.add_trace(go.Scatter(x=df['time'], y=df['ma50'], name="MA50"))

        st.plotly_chart(fig, use_container_width=True)

# -------- OPEN TRADES --------
st.divider()
st.subheader("📌 Open Positions")

positions = mt5.positions_get()

if positions:
    pos_data = []
    for p in positions:
        pos_data.append({
            "Symbol": p.symbol,
            "Type": "BUY" if p.type == 0 else "SELL",
            "Volume": p.volume,
            "Profit": p.profit
        })

    st.dataframe(pd.DataFrame(pos_data))
else:
    st.write("No open trades")

# -------- AUTO REFRESH --------
st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

st.experimental_rerun()