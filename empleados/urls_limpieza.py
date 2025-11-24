from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_limpieza import (
    TareaLimpiezaViewSet,
    PersonalLimpiezaViewSet,
    HorarioLimpiezaViewSet,
    AsignacionTareaViewSet,
    ChecklistLimpiezaViewSet,
    estadisticas_limpieza
)

router = DefaultRouter()
router.register(r'tareas', TareaLimpiezaViewSet, basename='tareas-limpieza')
router.register(r'personal', PersonalLimpiezaViewSet, basename='personal-limpieza')
router.register(r'horarios', HorarioLimpiezaViewSet, basename='horarios-limpieza')
router.register(r'asignaciones', AsignacionTareaViewSet, basename='asignaciones-limpieza')
router.register(r'checklists', ChecklistLimpiezaViewSet, basename='checklists-limpieza')

urlpatterns = [
    path('estadisticas/', estadisticas_limpieza, name='estadisticas-limpieza'),
    path('', include(router.urls)),
]
