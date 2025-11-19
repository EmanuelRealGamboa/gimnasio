from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MembresiaViewSet, SuscripcionMembresiaViewSet

router = DefaultRouter()
router.register(r'membresias', MembresiaViewSet, basename='membresia')
router.register(r'suscripciones', SuscripcionMembresiaViewSet, basename='suscripcion')

urlpatterns = [
    path('', include(router.urls)),
]
