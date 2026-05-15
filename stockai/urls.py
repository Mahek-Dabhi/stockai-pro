from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# Simple health check — Render pings this instead of dashboard
def health_check(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('',        TemplateView.as_view(template_name='landing.html')),
    path('health/', health_check, name='health_check'),   # ← Render pings this
    path('admin/',  admin.site.urls),
    path('users/',      include('apps.users.urls')),
    path('dashboard/',  include('apps.dashboard.urls')),
    path('portfolio/',  include('apps.portfolio.urls')),
    path('chat/',       include('apps.ai_chat.urls')),
    path('prediction/', include('apps.ai_prediction.urls')),
    path('sentiment/',  include('apps.sentiment.urls')),
    path('alerts/',     include('apps.alerts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)