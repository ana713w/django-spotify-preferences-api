"""
URLs principales del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_view(request):
    """Vista raíz de la API"""
    return JsonResponse({
        "message": "Bienvenido a Spotify Preferences API",
        "version": "1.0.0",
        "framework": "Django REST Framework",
        "admin": "/admin/",
        "endpoints": {
            "users": "/api/users/",
            "music": "/api/music/",
            "spotify": "/api/music/spotify/"
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view, name='root'),
    path('api/', include('api_view_users.urls')),
]