"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.interviews.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.recruiting.urls')),
    # django.conf.urls.static.static() se niega a registrar esto si DEBUG=False (por diseño de
    # Django, para no invitar a servir media así en producciones grandes) -- acá se usa la vista
    # de abajo directo, sin ese guard, porque Nginx ya proxya /media/ hasta Django igual que
    # /api/, /admin/ y /static/ (ver DECISIONS.md, Infra Fase 3/4) y el volumen de tráfico de este
    # proyecto no justifica montar un servidor de archivos aparte todavía.
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]