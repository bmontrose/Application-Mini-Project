import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

def analyze_breakouts(ticker, start_date, end_date, volume_threshold, price_threshold, holding_period):
    # Get the data
    df = get_stock_data(ticker, start_date, end_date)
    
    if len(df) < 20:  # Need at least 20 days for moving average
        return pd.DataFrame()
    
    # Calculate 20-day average volume
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
    
    # Calculate daily returns
    df['Daily_Return'] = df['Close'].pct_change() * 100
    
    # Find breakout days
    breakout_days = df[
        (df['Volume'] > df['Volume_MA20'] * (1 + volume_threshold/100)) &  # Volume condition
        (df['Daily_Return'] > price_threshold)  # Price change condition
    ].index
    
    # Calculate future returns for each breakout
    results = []
    for day in breakout_days:
        entry_price = df.loc[day, 'Close']
        future_slice = df.loc[day:].head(holding_period + 1)
        
        if len(future_slice) >= holding_period:
            exit_price = future_slice['Close'].iloc[holding_period]
            holding_return = ((exit_price - entry_price) / entry_price) * 100
            
            results.append({
                'Date': day.strftime('%Y-%m-%d'),
                'Entry_Price': round(entry_price, 2),
                'Exit_Price': round(exit_price, 2),
                'Return': round(holding_return, 2),
                'Volume': int(df.loc[day, 'Volume']),
                'Avg_Volume': int(df.loc[day, 'Volume_MA20']),
                'Volume_Increase': round((df.loc[day, 'Volume'] / df.loc[day, 'Volume_MA20'] - 1) * 100, 2),
                'Daily_Price_Change': round(df.loc[day, 'Daily_Return'], 2)
            })
    
    return pd.DataFrame(results)
