from django.urls import path
from authentication.views import EmpleadoUserCreateView, EmpleadoRegistroView
from authentication.dashboard_views import (
    dashboard_admin,
    dashboard_entrenador,
    dashboard_recepcion,
    dashboard_supervisor,
    dashboard_limpieza,
    dashboard_default
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Gestión de empleados
    path('admin/empleados/', EmpleadoUserCreateView.as_view(), name='admin_crear_empleado'),
    path('admin/empleados/registro/', EmpleadoRegistroView.as_view(), name='admin_registro_empleado'),
    path('admin/empleados/<int:pk>/', EmpleadoUserCreateView.as_view(), name='admin_usuario_operacion'),
    path('admin/empleados/<int:pk>/detalle', EmpleadoUserCreateView.as_view(), name='admin_usuario_detalle'),

    # Autenticación
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Dashboards por rol
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/entrenador/', dashboard_entrenador, name='dashboard_entrenador'),
    path('dashboard/recepcion/', dashboard_recepcion, name='dashboard_recepcion'),
    path('dashboard/supervisor/', dashboard_supervisor, name='dashboard_supervisor'),
    path('dashboard/limpieza/', dashboard_limpieza, name='dashboard_limpieza'),
    path('dashboard/', dashboard_default, name='dashboard_default'),
]
