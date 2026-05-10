import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .api_service import get_stock_data, get_multiple_stocks, is_market_open, DEFAULT_STOCKS
from .indicators import calculate_rsi, calculate_ma

@login_required
def dashboard_view(request):
    stocks = get_multiple_stocks(DEFAULT_STOCKS)
    market_open = is_market_open()

    featured = stocks[0] if stocks else None
    if featured:
        prices = featured['chart_prices']
        featured['rsi'] = calculate_rsi(prices)
        featured['ma20'] = calculate_ma(prices, 20)
        featured['chart_dates_json'] = json.dumps(featured['chart_dates'])
        featured['chart_prices_json'] = json.dumps(featured['chart_prices'])
        featured['ma20_json'] = json.dumps(featured['ma20'])
        featured['rsi_json'] = json.dumps(featured['rsi'])
        featured['ohlc_json'] = json.dumps(featured['ohlc_data'])

    return render(request, 'dashboard/dashboard.html', {
        'stocks': stocks,
        'featured': featured,
        'market_open': market_open,
    })

@login_required
def stock_detail_view(request, symbol):
    data = get_stock_data(symbol)
    if not data:
        return redirect('dashboard')
    prices = data['chart_prices']
    data['rsi'] = calculate_rsi(prices)
    data['ma20'] = calculate_ma(prices, 20)
    data['chart_dates_json'] = json.dumps(data['chart_dates'])
    data['chart_prices_json'] = json.dumps(data['chart_prices'])
    data['ma20_json'] = json.dumps(data['ma20'])
    data['rsi_json'] = json.dumps(data['rsi'])
    data['ohlc_json'] = json.dumps(data['ohlc_data'])
    return render(request, 'dashboard/stock_detail.html', {'stock': data})

@login_required
def get_stock_api(request, symbol):
    data = get_stock_data(symbol)
    if data:
        return JsonResponse(data)
    return JsonResponse({'error': 'Stock not found'}, status=404)