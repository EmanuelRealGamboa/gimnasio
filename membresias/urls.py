from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MembresiaViewSet

router = DefaultRouter()
router.register(r'membresias', MembresiaViewSet, basename='membresia')

urlpatterns = [
    path('', include(router.urls)),
]
