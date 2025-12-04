from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirigir_a_login(request):
    """Redirige la raíz del sitio al login"""
    return redirect('login:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('poa/', include('poa.urls')),
    path('administrador/', include('administrador.urls')),
    path('auditor/', include('auditor.urls')),
    path('', redirigir_a_login),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
