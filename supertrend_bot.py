import pandas as pd
import numpy as np
import ta
import time
import requests

# === CONFIG ===
SYMBOL = 'BTCUSDT'
INTERVAL = '15m'
API_KEY = 'your_delta_api_key'
API_SECRET = 'your_delta_api_secret'

FACTOR = 3.0
ATR_PERIOD = 10
SL_POINTS = 100
TP_POINTS = 500
TRAIL_OFFSET = 100
TRAIL_AMOUNT = 100
USE_TRAILING = True
USE_BREAKEVEN = True
BREAKEVEN_TRIGGER = 200

# === MOCK: Fetch OHLCV from TradingView or Exchange API ===
def fetch_ohlcv():
    # Placeholder: Replace with real fetch from TradingView or exchange
    df = pd.read_csv('historical.csv')  # Example CSV
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# === SuperTrend Calculation ===
def calculate_supertrend(df, period=ATR_PERIOD, factor=FACTOR):
    atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'], period)
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + factor * atr
    lowerband = hl2 - factor * atr

    supertrend = np.zeros(len(df))
    direction = np.zeros(len(df))

    for i in range(1, len(df)):
        if df['close'][i] > upperband[i-1]:
            direction[i] = -1
        elif df['close'][i] < lowerband[i-1]:
            direction[i] = 1
        else:
            direction[i] = direction[i-1]

        if direction[i] == -1:
            supertrend[i] = lowerband[i]
        else:
            supertrend[i] = upperband[i]

    df['supertrend'] = supertrend
    df['direction'] = direction
    return df

# === Strategy Logic ===
def strategy(df):
    position = None
    entry_price = None
    moved_to_be = False

    for i in range(1, len(df)):
        long_signal = df['direction'][i] < 0 and df['direction'][i-1] >= 0
        short_signal = df['direction'][i] > 0 and df['direction'][i-1] <= 0
        price = df['close'][i]

        if long_signal:
            position = 'long'
            entry_price = price
            moved_to_be = False
            print(f"LONG ENTRY at {price}")
            place_order('buy', price)

        elif short_signal:
            position = 'short'
            entry_price = price
            moved_to_be = False
            print(f"SHORT ENTRY at {price}")
            place_order('sell', price)

        # Manage exits
        if position == 'long':
            if USE_BREAKEVEN and not moved_to_be and price - entry_price >= BREAKEVEN_TRIGGER:
                print("Long BE Triggered. Move SL to Entry.")
                moved_to_be = True
            if price - entry_price >= TP_POINTS:
                print("Long TP Hit")
                position = None
            elif entry_price - price >= SL_POINTS:
                print("Long SL Hit")
                position = None

        if position == 'short':
            if USE_BREAKEVEN and not moved_to_be and entry_price - price >= BREAKEVEN_TRIGGER:
                print("Short BE Triggered. Move SL to Entry.")
                moved_to_be = True
            if entry_price - price >= TP_POINTS:
                print("Short TP Hit")
                position = None
            elif price - entry_price >= SL_POINTS:
                print("Short SL Hit")
                position = None

# === API Placeholder ===
def place_order(side, price):
    print(f"Placing {side.upper()} order at {price}")
    # Example Delta API call:
    # requests.post('https://api.delta.exchange/orders', headers={...}, json={...})

# === Main Loop ===
if __name__ == "__main__":
    while True:
        df = fetch_ohlcv()
        df = calculate_supertrend(df)
        strategy(df)
        time.sleep(60 * 15)  # Run every 15 mins
