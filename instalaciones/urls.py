from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SedeViewSet, EspacioViewSet

router = DefaultRouter()
router.register(r'sedes', SedeViewSet, basename='sede')
router.register(r'espacios', EspacioViewSet, basename='espacio')

urlpatterns = [
    path('', include(router.urls)),
]
