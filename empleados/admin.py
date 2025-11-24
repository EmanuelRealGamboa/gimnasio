from django.contrib import admin
from .models import (
    Empleado,
    Entrenador,
    Cajero,
    PersonalLimpieza,
    SupervisorEspacio,
    TareaLimpieza,
    HorarioLimpieza,
    AsignacionTarea,
    ChecklistLimpieza
)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
	list_display = ("persona", "puesto", "departamento", "fecha_contratacion", "tipo_contrato", "salario", "estado", "rfc", "curp", "nss", "sede")
	search_fields = ("persona__nombre", "persona__apellido_paterno", "puesto", "departamento")
	list_filter = ("estado", "tipo_contrato", "sede")

@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
	list_display = ("empleado", "especialidad", "turno", "sede")
	search_fields = ("empleado__persona__nombre", "especialidad")
	list_filter = ("turno", "sede")

@admin.register(Cajero)
class CajeroAdmin(admin.ModelAdmin):
	list_display = ("empleado", "turno", "sede")
	search_fields = ("empleado__persona__nombre",)
	list_filter = ("turno", "sede")

@admin.register(PersonalLimpieza)
class PersonalLimpiezaAdmin(admin.ModelAdmin):
	list_display = ("empleado", "turno", "sede")
	search_fields = ("empleado__persona__nombre",)
	list_filter = ("turno", "sede")

@admin.register(SupervisorEspacio)
class SupervisorEspacioAdmin(admin.ModelAdmin):
	list_display = ("empleado", "turno", "sede")
	search_fields = ("empleado__persona__nombre",)
	list_filter = ("turno", "sede")


# ============================================
# ADMIN PARA MÓDULO DE LIMPIEZA
# ============================================

@admin.register(TareaLimpieza)
class TareaLimpiezaAdmin(admin.ModelAdmin):
	list_display = ("nombre", "tipo_espacio", "duracion_estimada", "prioridad", "activo", "fecha_creacion")
	search_fields = ("nombre", "descripcion")
	list_filter = ("tipo_espacio", "prioridad", "activo")
	ordering = ("-fecha_creacion",)


@admin.register(HorarioLimpieza)
class HorarioLimpiezaAdmin(admin.ModelAdmin):
	list_display = ("personal_limpieza", "espacio", "dia_semana", "hora_inicio", "hora_fin", "activo")
	search_fields = ("personal_limpieza__empleado__persona__nombre",)
	list_filter = ("dia_semana", "activo", "espacio__sede")
	ordering = ("dia_semana", "hora_inicio")


@admin.register(AsignacionTarea)
class AsignacionTareaAdmin(admin.ModelAdmin):
	list_display = ("tarea", "personal_limpieza", "espacio", "fecha", "hora_inicio", "hora_fin", "estado", "fecha_completada")
	search_fields = ("tarea__nombre", "personal_limpieza__empleado__persona__nombre")
	list_filter = ("estado", "fecha", "espacio__sede")
	ordering = ("-fecha", "hora_inicio")
	readonly_fields = ("fecha_creacion", "fecha_actualizacion")


@admin.register(ChecklistLimpieza)
class ChecklistLimpiezaAdmin(admin.ModelAdmin):
	list_display = ("asignacion", "verificado", "calificacion", "fecha_verificacion")
	search_fields = ("asignacion__tarea__nombre",)
	list_filter = ("verificado", "calificacion")
	readonly_fields = ("fecha_creacion",)
