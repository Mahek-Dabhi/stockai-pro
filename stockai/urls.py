from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('portfolio/', include('apps.portfolio.urls')),
    path('chat/', include('apps.ai_chat.urls')),
    path('prediction/', include('apps.ai_prediction.urls')),
    path('sentiment/', include('apps.sentiment.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('watchlist/', include('apps.watchlist.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)