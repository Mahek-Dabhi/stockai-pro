import os
import requests
from datetime import datetime
import pytz

# ── Twelvedata API ────────────────────────────────────────────────────────────
# Works on cloud servers (no IP blocking unlike Yahoo Finance)
# Free tier: 8,000 requests/day | https://twelvedata.com
TWELVEDATA_KEY = os.getenv('TWELVEDATA_API_KEY', '')
BASE_URL       = 'https://api.twelvedata.com'

# ── Market hours ──────────────────────────────────────────────────────────────

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    open_time  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    is_weekday = now.weekday() < 5
    return is_weekday and open_time <= now <= close_time


# ── Default watchlist ─────────────────────────────────────────────────────────

DEFAULT_STOCKS = [
    'RELIANCE',
    'TCS',
    'HDFCBANK',
    'INFY',
    'ICICIBANK',
    'WIPRO',
]


def td_symbol(symbol):
    """Twelvedata format for NSE stocks: SYMBOL:NSE"""
    return f"{symbol}:NSE"


# ── Fetch live quote ──────────────────────────────────────────────────────────

def _fetch_quote(symbol):
    try:
        r = requests.get(
            f"{BASE_URL}/quote",
            params={
                'symbol': td_symbol(symbol),
                'apikey': TWELVEDATA_KEY,
            },
            timeout=10
        )
        data = r.json()
        if data.get('status') == 'error' or 'close' not in data:
            print(f"[api_service] Quote error for {symbol}: {data.get('message', 'unknown')}")
            return None
        return data
    except Exception as e:
        print(f"[api_service] Quote request failed for {symbol}: {e}")
        return None


# ── Fetch historical OHLCV ────────────────────────────────────────────────────

def _fetch_history(symbol, outputsize=30):
    try:
        r = requests.get(
            f"{BASE_URL}/time_series",
            params={
                'symbol':     td_symbol(symbol),
                'interval':   '1day',
                'outputsize': outputsize,
                'apikey':     TWELVEDATA_KEY,
            },
            timeout=10
        )
        data = r.json()
        if data.get('status') == 'error' or 'values' not in data:
            print(f"[api_service] History error for {symbol}: {data.get('message', 'unknown')}")
            return None
        # API returns newest-first — reverse to oldest-first for charts
        return list(reversed(data['values']))
    except Exception as e:
        print(f"[api_service] History request failed for {symbol}: {e}")
        return None


# ── Single stock fetch ────────────────────────────────────────────────────────

def get_stock_data(symbol):
    """
    Fetch live + historical data for one NSE stock via Twelvedata.
    Returns a dict on success, None on any failure.
    """
    quote   = _fetch_quote(symbol)
    history = _fetch_history(symbol)

    if not quote or not history:
        print(f"[api_service] No data for {symbol} — skipping.")
        return None

    try:
        current_price = float(quote.get('close', 0))
        prev_close    = float(quote.get('previous_close', current_price))

        if current_price <= 0:
            return None

        change     = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        # Build chart data from history bars
        chart_dates  = []
        chart_prices = []
        ohlc_data    = []

        for bar in history:
            try:
                dt    = datetime.strptime(bar['datetime'], '%Y-%m-%d')
                close = round(float(bar['close']), 2)
                open_ = round(float(bar['open']),  2)
                high  = round(float(bar['high']),  2)
                low   = round(float(bar['low']),   2)

                chart_dates.append(dt.strftime('%d %b'))
                chart_prices.append(close)
                ohlc_data.append({
                    'x': int(dt.timestamp() * 1000),  # Unix ms for Chart.js
                    'o': open_,
                    'h': high,
                    'l': low,
                    'c': close,
                })
            except Exception:
                continue

        if not chart_prices:
            return None

        return {
            'symbol':       symbol,
            'name':         quote.get('name', symbol),
            'price':        round(current_price, 2),
            'change':       round(change, 2),
            'change_pct':   round(change_pct, 2),
            'volume':       int(float(quote.get('volume', 0))),
            'market_cap':   0,
            'high':         round(float(quote.get('high', current_price)), 2),
            'low':          round(float(quote.get('low',  current_price)), 2),
            'chart_dates':  chart_dates,
            'chart_prices': chart_prices,
            'ohlc_data':    ohlc_data,
            'is_positive':  change >= 0,
        }

    except Exception as e:
        print(f"[api_service] Parse error for {symbol}: {e}")
        return None


# ── Multiple stocks ───────────────────────────────────────────────────────────

def get_multiple_stocks(symbols):
    stocks = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        if data:
            stocks.append(data)
    return stocks