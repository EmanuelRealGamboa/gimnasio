"""
URL configuration for gym project.

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
from authentication.views import EmpleadoUserCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('api/', include('roles.urls')),
    path('api/', include('clientes.urls')),
    path('api/', include('membresias.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/facturacion/', include('facturacion.urls')),
    path('api/ventas/', include('ventas.urls')),
    path('api/instalaciones/', include('instalaciones.urls')),
    path('api/gestion-equipos/', include('gestion_equipos.urls')),

]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
