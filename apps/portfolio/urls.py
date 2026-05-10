from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_view, name='portfolio'),
    path('add/', views.add_stock_view, name='add_stock'),
    path('sell/<int:pk>/', views.sell_stock_view, name='sell_stock'),
    path('history/', views.trade_history_view, name='trade_history'),
]