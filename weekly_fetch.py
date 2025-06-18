from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
import os
import sys

# --- CONFIG ---
API_KEY = "qamoej8ga26cbfxh"
ACCESS_TOKEN_PATH = "token.txt"
EXCHANGE_LIST = ["NSE", "BSE"]

# --- USER INPUT ---
symbol = input("📥 Enter stock symbol (e.g., RPOWER, KMSUGAR): ").strip().upper()

# --- AUTO-RANGE LAST 1900 DAYS ---
TO_DATE = dt.datetime.today()
FROM_DATE = TO_DATE - pd.Timedelta(days=1900)

# Convert to string format for Zerodha API
FROM_DATE = FROM_DATE.strftime("%Y-%m-%d")
TO_DATE = TO_DATE.strftime("%Y-%m-%d")

# --- AUTHENTICATE ---
kite = KiteConnect(api_key=API_KEY)
with open(ACCESS_TOKEN_PATH, "r") as f:
    kite.set_access_token(f.read().strip())

# --- FIND TOKEN FROM EXCHANGE ---
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
    sys.exit()

print(f"🔍 Found token for {symbol} on {exchange}")
print(f"📊 Fetching daily data for {symbol} from {FROM_DATE} to {TO_DATE}...")

# --- FETCH DATA WITHIN 1900-DAY LIMIT ---
data = kite.historical_data(
    instrument_token=token,
    from_date=FROM_DATE,
    to_date=TO_DATE,
    interval="day"
)

# --- CREATE WEEKLY OHLCV DATAFRAME ---
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

weekly = df.resample('W').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

# --- SAVE AND PRINT ---
os.makedirs("data", exist_ok=True)
out_path = f"data/{symbol}_weekly_output.csv"
weekly.to_csv(out_path)

print(f"\n✅ Weekly data saved to: {out_path}")
print("\n📤 Last 5 rows of weekly data:")
print(weekly.tail())
