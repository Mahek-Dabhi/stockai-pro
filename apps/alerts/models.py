from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    TYPE_CHOICES = [
        ('PRICE_ABOVE', 'Price Above'),
        ('PRICE_BELOW', 'Price Below'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, default='')
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} {self.alert_type} {self.target_price}"