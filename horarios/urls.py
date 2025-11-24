from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TipoActividadViewSet, HorarioViewSet, SesionClaseViewSet, BloqueoHorarioViewSet,
    ReservaClaseViewSet, ReservaEquipoViewSet, ReservaEntrenadorViewSet,
    EstadisticasHorariosViewSet
)

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'tipos-actividad', TipoActividadViewSet, basename='tipoactividad')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'sesiones', SesionClaseViewSet, basename='sesionclase')
router.register(r'bloqueos', BloqueoHorarioViewSet, basename='bloqueoshorario')
router.register(r'reservas-clases', ReservaClaseViewSet, basename='reservaclase')
router.register(r'reservas-equipos', ReservaEquipoViewSet, basename='reservaequipo')
router.register(r'reservas-entrenadores', ReservaEntrenadorViewSet, basename='reservaentrenador')
router.register(r'estadisticas', EstadisticasHorariosViewSet, basename='estadisticas')

app_name = 'horarios'

urlpatterns = [
    # Incluir todas las rutas del router (sin 'api/' porque ya está en gym/urls.py)
    path('', include(router.urls)),

    # URLs adicionales específicas si necesitas
    # path('calendario/', CalendarioView.as_view(), name='calendario'),
    # path('disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
]

# Documentación de endpoints disponibles:
"""
ENDPOINTS DISPONIBLES:

=== TIPOS DE ACTIVIDAD ===
GET    /api/tipos-actividad/                    - Listar tipos de actividad
POST   /api/tipos-actividad/                    - Crear tipo de actividad
GET    /api/tipos-actividad/{id}/               - Obtener tipo específico
PUT    /api/tipos-actividad/{id}/               - Actualizar tipo
DELETE /api/tipos-actividad/{id}/               - Eliminar tipo
GET    /api/tipos-actividad/{id}/equipos_necesarios/ - Equipos necesarios

=== HORARIOS BASE ===
GET    /api/horarios/                           - Listar horarios
POST   /api/horarios/                           - Crear horario
GET    /api/horarios/{id}/                      - Obtener horario específico
PUT    /api/horarios/{id}/                      - Actualizar horario
DELETE /api/horarios/{id}/                      - Eliminar horario
GET    /api/horarios/calendario_semanal/        - Vista calendario semanal
GET    /api/horarios/disponibilidad/            - Verificar disponibilidad
POST   /api/horarios/{id}/generar_sesiones/     - Generar sesiones automáticamente

=== SESIONES DE CLASES ===
GET    /api/sesiones/                           - Listar sesiones
POST   /api/sesiones/                           - Crear sesión
GET    /api/sesiones/{id}/                      - Obtener sesión específica
PUT    /api/sesiones/{id}/                      - Actualizar sesión
DELETE /api/sesiones/{id}/                      - Eliminar sesión
GET    /api/sesiones/calendario_mensual/        - Vista calendario mensual
GET    /api/sesiones/{id}/reservas/             - Reservas de una sesión
POST   /api/sesiones/{id}/marcar_asistencia/    - Marcar asistencia masiva

=== BLOQUEOS DE HORARIOS ===
GET    /api/bloqueos/                           - Listar bloqueos
POST   /api/bloqueos/                           - Crear bloqueo
GET    /api/bloqueos/{id}/                      - Obtener bloqueo específico
PUT    /api/bloqueos/{id}/                      - Actualizar bloqueo
DELETE /api/bloqueos/{id}/                      - Eliminar bloqueo
GET    /api/bloqueos/activos/                   - Bloqueos activos

=== RESERVAS DE CLASES ===
GET    /api/reservas-clases/                    - Listar reservas de clases
POST   /api/reservas-clases/                    - Crear reserva de clase
GET    /api/reservas-clases/{id}/               - Obtener reserva específica
PUT    /api/reservas-clases/{id}/               - Actualizar reserva
DELETE /api/reservas-clases/{id}/               - Eliminar reserva
GET    /api/reservas-clases/mis_reservas/       - Reservas del cliente autenticado
POST   /api/reservas-clases/{id}/cancelar/      - Cancelar reserva

=== RESERVAS DE EQUIPOS ===
GET    /api/reservas-equipos/                   - Listar reservas de equipos
POST   /api/reservas-equipos/                   - Crear reserva de equipo
GET    /api/reservas-equipos/{id}/              - Obtener reserva específica
PUT    /api/reservas-equipos/{id}/              - Actualizar reserva
DELETE /api/reservas-equipos/{id}/              - Eliminar reserva
GET    /api/reservas-equipos/disponibilidad_equipo/ - Verificar disponibilidad
POST   /api/reservas-equipos/{id}/iniciar_uso/  - Iniciar uso del equipo
POST   /api/reservas-equipos/{id}/finalizar_uso/ - Finalizar uso del equipo

=== RESERVAS DE ENTRENADORES ===
GET    /api/reservas-entrenadores/              - Listar reservas de entrenadores
POST   /api/reservas-entrenadores/              - Crear reserva de entrenador
GET    /api/reservas-entrenadores/{id}/         - Obtener reserva específica
PUT    /api/reservas-entrenadores/{id}/         - Actualizar reserva
DELETE /api/reservas-entrenadores/{id}/         - Eliminar reserva
GET    /api/reservas-entrenadores/pendientes_aprobacion/ - Sesiones pendientes
POST   /api/reservas-entrenadores/{id}/aprobar/ - Aprobar sesión
POST   /api/reservas-entrenadores/{id}/iniciar_sesion/ - Iniciar sesión
POST   /api/reservas-entrenadores/{id}/completar_sesion/ - Completar sesión

=== ESTADÍSTICAS ===
GET    /api/estadisticas/ocupacion_semanal/     - Estadísticas de ocupación semanal
GET    /api/estadisticas/actividades_populares/ - Actividades más populares

=== PARÁMETROS DE FILTRADO COMUNES ===
- ?sede_id=X                    - Filtrar por sede
- ?fecha_inicio=YYYY-MM-DD      - Filtrar por fecha de inicio
- ?fecha_fin=YYYY-MM-DD         - Filtrar por fecha de fin
- ?estado=X                     - Filtrar por estado
- ?search=texto                 - Búsqueda por texto
- ?ordering=campo               - Ordenar por campo
- ?page=X                       - Paginación

=== EJEMPLOS DE USO ===

1. Obtener horarios de una sede específica:
   GET /api/horarios/?espacio__sede=1

2. Buscar actividades de yoga:
   GET /api/tipos-actividad/?search=yoga

3. Ver reservas de un cliente:
   GET /api/reservas-clases/mis_reservas/

4. Verificar disponibilidad de equipo:
   GET /api/reservas-equipos/disponibilidad_equipo/?activo_id=5&fecha=2025-01-15

5. Generar sesiones para un horario:
   POST /api/horarios/1/generar_sesiones/
   {
     "fecha_inicio": "2025-01-01",
     "fecha_fin": "2025-01-31"
   }

6. Crear reserva de clase:
   POST /api/reservas-clases/
   {
     "cliente": 1,
     "sesion_clase": 5,
     "observaciones": "Primera vez en yoga"
   }

7. Marcar asistencia:
   POST /api/sesiones/5/marcar_asistencia/
   {
     "asistencias": [
       {"reserva_id": 1, "asistio": true},
       {"reserva_id": 2, "asistio": false}
     ]
   }
"""
