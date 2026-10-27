from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def serve_frontend(request):
    html_path = settings.BASE_DIR.parent / 'frontend' / 'app.html'
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse('Frontend file not found', status=404)

urlpatterns = [
    path('', serve_frontend, name='frontend-home'),
    path('app/', serve_frontend, name='frontend-app'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

