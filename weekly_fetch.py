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
    """Fetches full weekly OHLCV from Kite Connect in 2000-day safe chunks."""
    FROM_DATE = "2010-01-01"
    TO_DATE = dt.datetime.today().strftime("%Y-%m-%d")

    # --- AUTHENTICATE ---
    kite = KiteConnect(api_key=API_KEY)
    with open(ACCESS_TOKEN_PATH, "r") as f:
        kite.set_access_token(f.read().strip())

    # --- FIND TOKEN FROM EXCHANGES ---
    token = None
    for exch in EXCHANGE_LIST:
        instruments = kite.instruments(exch)
        match = next((i for i in instruments if i["tradingsymbol"] == symbol), None)
        if match:
            token = match["instrument_token"]
            exchange = exch
            break

    if not token:
        print(f"❌ Symbol '{symbol}' not found on NSE or BSE.")
        return None

    print(f"🔍 Found token for {symbol} on {exchange}")
    print(f"📊 Fetching daily data for {symbol} from {FROM_DATE} to {TO_DATE}...")

    # --- CHUNKED DAILY FETCH ---
    from_date = pd.to_datetime(FROM_DATE)
    to_date = pd.to_datetime(TO_DATE)
    all_data = []

    while from_date < to_date:
        chunk_end = min(from_date + pd.Timedelta(days=1900), to_date)
        chunk = kite.historical_data(
            instrument_token=token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=chunk_end.strftime("%Y-%m-%d"),
            interval="day"
        )
        all_data.extend(chunk)
        from_date = chunk_end + pd.Timedelta(days=1)

    # --- CONVERT TO WEEKLY ---
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

    # --- SAVE CSV ---
    os.makedirs("data", exist_ok=True)
    out_path = f"data/{symbol}_weekly_output.csv"
    weekly.to_csv(out_path)

    print(f"✅ Weekly data saved to: {out_path}")
    print(f"📤 Last 5 rows of weekly data:")
    print(weekly.tail())

    return weekly


# --- Manual inline test for Colab or Script Run ---
if __name__ == "__main__":
    symbol = input("📥 Enter stock symbol (e.g., RPOWER, IRFC): ").strip().upper()
    weekly = get_weekly_data_override(symbol)
