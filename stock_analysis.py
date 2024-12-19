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
                'Date': day,
                'Entry_Price': entry_price,
                'Exit_Price': exit_price,
                'Return': holding_return,
                'Volume': df.loc[day, 'Volume'],
                'Avg_Volume': df.loc[day, 'Volume_MA20'],
                'Volume_Increase': (df.loc[day, 'Volume'] / df.loc[day, 'Volume_MA20'] - 1) * 100,
                'Daily_Price_Change': df.loc[day, 'Daily_Return']
            })
    
    return pd.DataFrame(results)
