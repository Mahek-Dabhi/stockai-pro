import pandas as pd

def calculate_rsi(prices, period=14):
    try:
        s = pd.Series(prices)
        delta = s.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return [round(r, 2) if not pd.isna(r) else None for r in rsi.tolist()]
    except:
        return []

def calculate_ma(prices, period=20):
    try:
        s = pd.Series(prices)
        ma = s.rolling(period).mean()
        return [round(r, 2) if not pd.isna(r) else None for r in ma.tolist()]
    except:
        return []