import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# === Parameters ===
tickers_to_scan = ['BB.TO', 'WEED.TO', 'HUT.TO', 'LSPD.TO', 'SHOP.TO', 'SU.TO', 'CVE.TO', 'BTE.TO', 'MEG.TO', 'VET.TO']
interval = '1m'
days_to_fetch = 5
oscillation_threshold = 0.008
trend_threshold = 0.03
min_oscillations = 4

# === Functions ===

def fetch_data(ticker):
    end = datetime.today()
    start = end - timedelta(days=days_to_fetch)
    data = yf.Ticker(ticker).history(start=start, end=end, interval=interval)
    return data

def is_trending(net_change):
    return abs(net_change) > trend_threshold

def is_oscillating(prices, threshold):
    count = 0
    for i in range(1, len(prices)):
        change = abs(prices[i] - prices[i - 1]) / prices[i - 1]
        if change >= threshold:
            count += 1
    return count >= min_oscillations

def check_ticker(ticker):
    df = fetch_data(ticker)
    if df.empty or len(df) < 100:
        return None
    prices = df['Close'].dropna().values
    net_change = (prices[-1] - prices[0]) / prices[0]
    volatility = np.std(np.diff(prices) / prices[:-1])

    if is_trending(net_change):
        return None
    if not is_oscillating(prices, oscillation_threshold):
        return None

    return {
        'Ticker': ticker,
        'Net Change (%)': round(net_change * 100, 2),
        'Volatility': round(volatility, 5)
    }

# === Run the Check ===
import time

results = []
for t in tickers_to_scan:
    time.sleep(1.5)  # ⬅️ Wait 1.5 seconds between each API call to avoid rate limits
    result = check_ticker(t)
    if result:
        results.append(result)
filtered = [r for r in results if r is not None]

# === Output ===
df = pd.DataFrame(filtered)
print("\nQualified Stocks for Grid Strategy:\n")
print(df.to_string(index=False))
