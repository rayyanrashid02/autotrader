import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Parameters
tickers = ['BB.TO', 'WEED.TO', 'HUT.TO', 'SHOP.TO']
#start_cash = 10000
trade_fraction = 0.1
threshold = 0.01  # 10% move
# Define custom threshold per ticker
thresholds = {
    'BB.TO': 0.0075,
    'WEED.TO': 0.01,
    'HUT.TO': 0.008,
#    'LSPD.TO': 0.05,
    'SHOP.TO': 0.006
}

interval = '1m'
lookback_days = 5

def simulate_strategy(prices, threshold):
    """
    Simulate trading strategy based on a list of prices
    
    Args:
        prices: List of prices
        
    Returns:
        tuple: (final portfolio value, final price, initial portfolio value)
    """
    if not prices or len(prices) < 2:
        return start_cash, prices[-1] if prices else 0, start_cash

    cash = start_cash
    shares = 0
    last_price = prices[0]
    portfolio_values = []

    for price in prices:
        if last_price == 0 or pd.isna(price):
            continue

        change = (price - last_price) / last_price

        if change <= -threshold and cash > 0:
            invest = cash * trade_fraction
            buy_shares = invest / price
            shares += buy_shares
            cash -= invest
            last_price = price

        elif change >= threshold and shares > 0:
            sell_shares = shares * trade_fraction
            cash += sell_shares * price
            shares -= sell_shares
            last_price = price

        portfolio_values.append(cash + shares * price)
    
    if not portfolio_values:
        return start_cash, prices[-1] if prices else 0, start_cash
        
    return portfolio_values[-1], prices[-1], portfolio_values[0]

# # Download and simulate
# # Replace this with the date you want to simulate (must be a trading day)
# target_date = datetime(2025, 3, 27)  # Example: Dec 4, 2024

# # You need a little buffer before/after for yfinance to fetch 1m candles properly
# start = target_date
# end = target_date + timedelta(days=1)

# results = {}

# for ticker in tickers:
#     print(f"Processing {ticker}...")
#     try:
#         # Download data
#         stock = yf.Ticker(ticker)
#         history = stock.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), interval=interval)
        
#         if history.empty:
#             print(f"  No data returned for {ticker}")
#             results[ticker] = "No intraday data"
#             continue
            
#         print(f"  Downloaded data shape: {history.shape}")
#         print(f"  Downloaded columns: {history.columns.tolist()}")
        
#         # Extract today's close prices directly
#         today = datetime.today().date()
#         today_data = history[history.index.date == today]
        
#         if today_data.empty:
#             # Try yesterday if today is empty (might be weekend/holiday)
#             yesterday = (datetime.today() - timedelta(days=1)).date()
#             today_data = history[history.index.date == yesterday]
#             print(f"  No data for today, using {yesterday} instead")
            
#         if today_data.empty:
#             # Try the most recent day in the data
#             most_recent = history.index.date.max()
#             today_data = history[history.index.date == most_recent]
#             print(f"  Using most recent available date: {most_recent}")
        
#         if today_data.empty or 'Close' not in today_data.columns:
#             print(f"  No usable price data found")
#             results[ticker] = "No usable price data"
#             continue
            
#         # Extract prices as a simple list
#         prices = today_data['Close'].tolist()
#         print(f"  Found {len(prices)} price points for analysis")
        
#         # Run simulation
#         final_val, final_price, start_val = simulate_strategy(prices)
#         results[ticker] = {
#             'Start Value': round(start_val, 2),
#             'Final Value': round(final_val, 2),
#             'Change (%)': round((final_val - start_val) / start_val * 100, 2),
#             'Data Points': len(prices)
#         }

#     except Exception as e:
#         results[ticker] = f"Error: {str(e)}"
#         import traceback
#         print(traceback.format_exc())

# # Display results
# print("\nFinal Results:")
# for k, v in results.items():
#     print(f"{k}: {v}")

#######################################################
print("\n30-Day Compounding Results (Per Ticker):")

compound_results = {}

for ticker in tickers:
    print(f"\nProcessing {ticker} for 30-day compounding...")
    try:
        # Download 8 days of 1-minute data to get 5 trading days
        comp_start = datetime.today() - timedelta(days=8)
        comp_end = datetime.today() #- timedelta(days=1)
        stock = yf.Ticker(ticker)
        history = stock.history(start=comp_start.strftime('%Y-%m-%d'), end=comp_end.strftime('%Y-%m-%d'), interval='1m')

        if history.empty:
            print("  No data.")
            compound_results[ticker] = "No data"
            continue

        # Group by day
        history['Date'] = history.index.date
        unique_days = sorted(history['Date'].unique())[-30:]  # Use the last 30 trading days
        capital = 1000.0
        capital_history = []

        for day in unique_days:
            day_data = history[history['Date'] == day]
            if day_data.empty or 'Close' not in day_data.columns:
                continue

            prices = day_data['Close'].dropna().tolist()
            if len(prices) < 2:
                continue

            # Use updated capital as start_cash
            global start_cash
            start_cash = capital  # update shared variable
            final_val, _, _ = simulate_strategy(prices, threshold=thresholds[ticker])
            capital = final_val
            capital_history.append((str(day), round(capital, 2)))

        # Save results
        compound_results[ticker] = {
            'Initial': 1000.0,
            'Final': round(capital, 2),
            'Total Return (%)': round((capital - 1000) / 1000 * 100, 2),
            'Days Simulated': len(capital_history),
            'Daily Breakdown': capital_history
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        compound_results[ticker] = f"Error: {str(e)}"

# Show results
for k, v in compound_results.items():
    print(f"\n{k}:")
    if isinstance(v, dict):
        print(f"  Initial: ${v['Initial']}")
        print(f"  Final: ${v['Final']}")
        print(f"  Total Return: {v['Total Return (%)']}%")
        print(f"  Days Simulated: {v['Days Simulated']}")
    else:
        print(f"  {v}")

# print("\nSimulated Future Loop (Ideal Conditions):")

# n_simulated_days = 70  # ⬅️ change this to however many future days you want to simulate
# loop_results = {}

# for ticker in tickers:
#     print(f"\nSimulating ideal future for {ticker}...")
#     try:
#         # Get last 8 calendar days to capture 5 trading days
#         loop_start = datetime.today() - timedelta(days=8)
#         loop_end = datetime.today()
#         stock = yf.Ticker(ticker)
#         history = stock.history(start=loop_start.strftime('%Y-%m-%d'), end=loop_end.strftime('%Y-%m-%d'), interval='1m')

#         if history.empty:
#             print("  No data.")
#             loop_results[ticker] = "No data"
#             continue

#         # Group by actual trading days
#         history['Date'] = history.index.date
#         real_days = sorted(history['Date'].unique())[-5:]
#         day_blocks = []

#         for day in real_days:
#             day_data = history[history['Date'] == day]
#             prices = day_data['Close'].dropna().tolist()
#             if len(prices) >= 2:
#                 day_blocks.append(prices)

#         if len(day_blocks) < 5:
#             loop_results[ticker] = "Insufficient valid days"
#             continue

#         # Repeat those 5 days over n_simulated_days
#         synthetic_days = []
#         while len(synthetic_days) < n_simulated_days:
#             synthetic_days.extend(day_blocks)

#         # Simulate
#         capital = 1000.0
#         capital_history = []
#         for i, prices in enumerate(synthetic_days[:n_simulated_days]):
#             global start_cash
#             start_cash = capital
#             final_val, _, _ = simulate_strategy(prices, threshold=thresholds[ticker])
#             capital = final_val
#             capital_history.append((f"Day {i+1}", round(capital, 2)))

#         # Save results
#         loop_results[ticker] = {
#             'Initial': 1000.0,
#             'Final': round(capital, 2),
#             'Total Return (%)': round((capital - 1000) / 1000 * 100, 2),
#             'Days Simulated': len(capital_history),
#             'Daily Breakdown': capital_history
#         }

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         loop_results[ticker] = f"Error: {str(e)}"

# # Show results
# for k, v in loop_results.items():
#     print(f"\n{k}:")
#     if isinstance(v, dict):
#         print(f"  Initial: ${v['Initial']}")
#         print(f"  Final: ${v['Final']}")
#         print(f"  Total Return: {v['Total Return (%)']}%")
#         print(f"  Days Simulated: {v['Days Simulated']}")
#     else:
#         print(f"  {v}")
