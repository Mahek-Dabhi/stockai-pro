from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('stock/<str:symbol>/', views.stock_detail_view, name='stock_detail'),
    path('api/stock/<str:symbol>/', views.get_stock_api, name='stock_api'),
]