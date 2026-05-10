from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio, Transaction
from apps.dashboard.api_service import get_stock_data

@login_required
def portfolio_view(request):
    holdings = Portfolio.objects.filter(user=request.user)
    portfolio_data = []
    total_invested = 0
    total_current = 0

    for holding in holdings:
        stock = get_stock_data(holding.symbol)
        if stock:
            current_price = stock['price']
            current_value = float(holding.quantity) * current_price
            invested = float(holding.total_invested)
            pnl = current_value - invested
            pnl_pct = (pnl / invested * 100) if invested else 0
            total_invested += invested
            total_current += current_value
            portfolio_data.append({
                'holding': holding,
                'current_price': current_price,
                'current_value': round(current_value, 2),
                'pnl': round(pnl, 2),
                'pnl_pct': round(pnl_pct, 2),
                'is_profit': pnl >= 0,
            })

    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

    return render(request, 'portfolio/portfolio.html', {
        'portfolio_data': portfolio_data,
        'total_invested': round(total_invested, 2),
        'total_current': round(total_current, 2),
        'total_pnl': round(total_pnl, 2),
        'total_pnl_pct': round(total_pnl_pct, 2),
        'is_profit': total_pnl >= 0,
    })

@login_required
def add_stock_view(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol').upper().strip()
        quantity = request.POST.get('quantity')
        buy_price = request.POST.get('buy_price')
        buy_date = request.POST.get('buy_date')

        stock = get_stock_data(symbol)
        if not stock:
            messages.error(request, f'Stock {symbol} not found!')
            return redirect('add_stock')

        Portfolio.objects.create(
            user=request.user,
            symbol=symbol,
            company_name=stock['name'],
            quantity=quantity,
            buy_price=buy_price,
            buy_date=buy_date,
        )
        Transaction.objects.create(
            user=request.user,
            symbol=symbol,
            company_name=stock['name'],
            transaction_type='BUY',
            quantity=quantity,
            price=buy_price,
        )
        messages.success(request, f'{symbol} added to portfolio!')
        return redirect('portfolio')

    return render(request, 'portfolio/add_stock.html')

@login_required
def sell_stock_view(request, pk):
    holding = get_object_or_404(Portfolio, pk=pk, user=request.user)
    Transaction.objects.create(
        user=request.user,
        symbol=holding.symbol,
        company_name=holding.company_name,
        transaction_type='SELL',
        quantity=holding.quantity,
        price=get_stock_data(holding.symbol)['price'],
    )
    holding.delete()
    messages.success(request, f'{holding.symbol} sold successfully!')
    return redirect('portfolio')

@login_required
def trade_history_view(request):
    transactions = Transaction.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'portfolio/trade_history.html',
        {'transactions': transactions})