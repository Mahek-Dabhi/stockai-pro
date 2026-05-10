from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Alert
from apps.dashboard.api_service import get_stock_data

@login_required
def alerts_view(request):
    alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'alerts/alerts.html', {'alerts': alerts})

@login_required
def add_alert_view(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol').upper().strip()
        alert_type = request.POST.get('alert_type')
        target_price = request.POST.get('target_price')

        stock = get_stock_data(symbol)
        if not stock:
            messages.error(request, f'Stock {symbol} not found!')
            return redirect('alerts')

        Alert.objects.create(
            user=request.user,
            symbol=symbol,
            company_name=stock['name'],
            alert_type=alert_type,
            target_price=target_price,
            current_price=stock['price'],
        )
        messages.success(request, f'Alert created for {symbol}!')
        return redirect('alerts')
    return redirect('alerts')

@login_required
def delete_alert_view(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, 'Alert deleted!')
    return redirect('alerts')

@login_required
def check_alerts_view(request):
    alerts = Alert.objects.filter(user=request.user, status='ACTIVE')
    triggered = []
    for alert in alerts:
        stock = get_stock_data(alert.symbol)
        if stock:
            current = stock['price']
            alert.current_price = current
            if alert.alert_type == 'PRICE_ABOVE' and current >= float(alert.target_price):
                alert.status = 'TRIGGERED'
                alert.triggered_at = timezone.now()
                triggered.append(alert.symbol)
            elif alert.alert_type == 'PRICE_BELOW' and current <= float(alert.target_price):
                alert.status = 'TRIGGERED'
                alert.triggered_at = timezone.now()
                triggered.append(alert.symbol)
            alert.save()
    return render(request, 'alerts/alerts.html', {
        'alerts': Alert.objects.filter(user=request.user).order_by('-created_at'),
        'triggered': triggered,
    })