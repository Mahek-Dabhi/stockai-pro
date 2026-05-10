from django.urls import path
from . import views

urlpatterns = [
    path('', views.alerts_view, name='alerts'),
    path('add/', views.add_alert_view, name='add_alert'),
    path('delete/<int:pk>/', views.delete_alert_view, name='delete_alert'),
    path('check/', views.check_alerts_view, name='check_alerts'),
]   