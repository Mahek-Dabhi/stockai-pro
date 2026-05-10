from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.dashboard.api_service import get_stock_data, DEFAULT_STOCKS
from .predictor import get_prediction

@login_required
def prediction_view(request):
    symbol = request.GET.get('symbol', 'RELIANCE')
    stock = get_stock_data(symbol)
    prediction = None

    if stock:
        prices = stock['chart_prices']
        if len(prices) >= 15:
            prediction = get_prediction(prices)

    stocks_list = DEFAULT_STOCKS

    return render(request, 'ai_prediction/prediction.html', {
        'stock': stock,
        'prediction': prediction,
        'symbol': symbol,
        'stocks_list': stocks_list,
    })