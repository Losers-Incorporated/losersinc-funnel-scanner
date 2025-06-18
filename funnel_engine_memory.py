import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

# 🧠 Assumes `weekly` DataFrame already exists in memory (from weekly_fetch.py)

def run_funnel_engine(symbol, weekly):
    df = weekly.copy()

    # --- Compute Indicators ---
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

    # --- Define Params ---
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    volume_avg = df['volume'].rolling(3).mean().iloc[-1]
    atr = latest['atr']

    zone_low = df['close'].rolling(5).min().iloc[-1]
    zone_high = df['close'].rolling(5).max().iloc[-1]

    entry_zone = f"{round(prev['close'] - 0.5 * atr, 2)}–{round(latest['close'], 2)}"
    stop = round(latest['low'] - atr, 2)
    target = f"{round(latest['close'] + 1.5 * atr, 2)}–{round(latest['close'] + 2.5 * atr, 2)}"

    bias = "Bullish" if latest['close'] > zone_high and latest['rsi'] > 60 else "Neutral"
    funnel_shape = "Base Breakout Funnel" if latest['close'] > zone_high else "Inside Funnel"
    rsi_momentum = f"RSI ~{int(latest['rsi'])}"
    vol_confirmation = "Volume above 3W avg ✅" if latest['volume'] > volume_avg else "Low/flat volume ⚠️"

    # --- Output Table ---
    print("\n🧠 Funnel Signal Summary (Live Memory Version):\n")
    print("| Ticker | Bias   | Funnel Shape        | RSI Momentum | Volume Confirmation       | Entry Zone      | Stop  | Target Zone           |")
    print("|--------|--------|---------------------|---------------|----------------------------|------------------|--------|------------------------|")
    print(f"| {symbol} | {bias} | {funnel_shape} | {rsi_momentum:<13} | {vol_confirmation:<26} | {entry_zone:<16} | {stop:<6} | {target:<22} |")
