from django.contrib import admin
from .models import Empleado, Entrenador, Cajero, PersonalLimpieza, SupervisorEspacio

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
