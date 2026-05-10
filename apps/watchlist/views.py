from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import WatchlistItem
from apps.dashboard.api_service import get_stock_data, get_multiple_stocks


@login_required
def watchlist_view(request):
    """Main watchlist page — shows user's saved stocks with live prices."""
    items = WatchlistItem.objects.filter(user=request.user)
    symbols = [item.symbol for item in items]

    stocks_data = []
    if symbols:
        for symbol in symbols:
            data = get_stock_data(symbol)
            if data:
                stocks_data.append(data)

    context = {
    'watchlist_items': items,
    'stocks_data': stocks_data,
    'stocks_json': json.dumps(stocks_data),
    'popular_symbols': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'WIPRO', 'BAJFINANCE', 'ICICIBANK', 'ADANIENT', 'SUNPHARMA'],
}
    return render(request, 'watchlist/watchlist.html', context)


@login_required
def add_to_watchlist(request):
    """Add a stock symbol to the user's watchlist."""
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        if not symbol:
            messages.error(request, 'Please enter a valid stock symbol.')
            return redirect('watchlist:watchlist')

        # Verify symbol exists via yfinance
        data = get_stock_data(symbol)
        if not data:
            messages.error(request, f'Symbol "{symbol}" not found on NSE. Please check and try again.')
            return redirect('watchlist:watchlist')

        obj, created = WatchlistItem.objects.get_or_create(
            user=request.user,
            symbol=symbol,
            defaults={'company_name': data.get('name', symbol)}
        )
        if created:
            messages.success(request, f'{data.get("name", symbol)} added to your watchlist.')
        else:
            messages.info(request, f'{symbol} is already in your watchlist.')

    return redirect('watchlist:watchlist')


@login_required
def remove_from_watchlist(request, pk):
    """Remove a stock from the user's watchlist."""
    item = get_object_or_404(WatchlistItem, pk=pk, user=request.user)
    symbol = item.symbol
    item.delete()
    messages.success(request, f'{symbol} removed from your watchlist.')
    return redirect('watchlist:watchlist')


@login_required
def watchlist_api(request):
    """JSON endpoint — returns live prices for all watchlist symbols."""
    items = WatchlistItem.objects.filter(user=request.user)
    symbols = [item.symbol for item in items]
    stocks_data = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        if data:
            stocks_data.append(data)
    return JsonResponse({'stocks': stocks_data})