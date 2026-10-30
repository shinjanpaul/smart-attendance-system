from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve

def serve_frontend(request):
    candidates = [
        settings.BASE_DIR.parent / 'frontend' / 'app.html',
        settings.BASE_DIR / 'frontend' / 'app.html',
        settings.BASE_DIR / 'app.html'
    ]
    for p in candidates:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse('Frontend file not found', status=404)

urlpatterns = [
    path('', serve_frontend, name='frontend-home'),
    path('app/', serve_frontend, name='frontend-app'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

