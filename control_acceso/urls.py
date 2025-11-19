from django.urls import path
from . import views

urlpatterns = [
    # Endpoints de validación y registro de acceso
    path('registros/validar_acceso/', views.validar_acceso, name='validar-acceso'),
    path('registros/registrar_acceso/', views.registrar_acceso, name='registrar-acceso'),
    path('registros/estadisticas/', views.estadisticas_acceso, name='estadisticas-acceso'),

    # CRUD de registros (opcional)
    path('registros/', views.listar_registros, name='listar-registros'),
]
