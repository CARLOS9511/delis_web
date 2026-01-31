"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirigir raíz al dashboard
    path('', RedirectView.as_view(url='/reportes/dashboard/', permanent=False)),
    
    # URLs de cada módulo
    #path('usuarios/', include('usuarios.urls')),
   
    path('', include('usuarios.urls')),

    path('inventario/', include('inventario.urls')),
    path('produccion/', include('produccion.urls')),
    path('despacho/', include('despacho.urls')),
    path('ventas/', include('ventas.urls')),
    path('sucursales/', include('sucursales.urls')),
    path('reportes/', include('reportes.urls')),
    #apiis saldos
    path('despacho/', include('despacho.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar admin
admin.site.site_header = "Sistema Delis"
admin.site.site_title = "Admin"
admin.site.index_title = "Panel de Administración"
