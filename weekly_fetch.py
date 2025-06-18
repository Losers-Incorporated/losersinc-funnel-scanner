# weekly_fetch.py

from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
import os

# --- CONFIG ---
API_KEY = "qamoej8ga26cbfxh"
ACCESS_TOKEN_PATH = "token.txt"
EXCHANGE_LIST = ["NSE", "BSE"]

def get_weekly_data_override(symbol):
    """Fetches ~5 years of weekly OHLCV using safe 1900-day chunks from Kite Connect"""
    FROM_DATE = (dt.datetime.today() - pd.Timedelta(days=1825)).strftime("%Y-%m-%d")
    TO_DATE = dt.datetime.today().strftime("%Y-%m-%d")

    # --- AUTHENTICATION ---
    kite = KiteConnect(api_key=API_KEY)
    with open(ACCESS_TOKEN_PATH, "r") as f:
        kite.set_access_token(f.read().strip())

    # --- TOKEN FETCH ---
    token = None
    for exch in EXCHANGE_LIST:
        instruments = kite.instruments(exch)
        match = next((i for i in instruments if i["tradingsymbol"] == symbol), None)
        if match:
            token = match["instrument_token"]
            break

    if not token:
        print(f"❌ '{symbol}' not found on NSE/BSE")
        return None

    print(f"🔍 Found token for {symbol}")
    print(f"📊 Fetching data from {FROM_DATE} to {TO_DATE}...")

    # --- CHUNKED FETCH ---
    from_date = pd.to_datetime(FROM_DATE)
    to_date = pd.to_datetime(TO_DATE)
    all_data = []

    while from_date < to_date:
        chunk_end = min(from_date + pd.Timedelta(days=1900), to_date)
        chunk = kite.historical_data(
            token,
            from_date.strftime("%Y-%m-%d"),
            chunk_end.strftime("%Y-%m-%d"),
            interval="day"
        )
        all_data.extend(chunk)
        from_date = chunk_end + pd.Timedelta(days=1)

    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    weekly = df.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    os.makedirs("data", exist_ok=True)
    out_path = f"data/{symbol}_weekly_output.csv"
    weekly.to_csv(out_path)

    print(f"✅ Saved: {out_path}")
    return weekly
