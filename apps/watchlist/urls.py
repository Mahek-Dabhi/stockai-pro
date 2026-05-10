from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.watchlist_view, name='watchlist'),
    path('add/', views.add_to_watchlist, name='add'),
    path('remove/<int:pk>/', views.remove_from_watchlist, name='remove'),
    path('api/', views.watchlist_api, name='api'),
]