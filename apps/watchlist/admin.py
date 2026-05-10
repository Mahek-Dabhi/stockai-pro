from django.contrib import admin
from .models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'symbol', 'company_name', 'added_at')
    list_filter = ('user',)
    search_fields = ('symbol', 'company_name', 'user__username')