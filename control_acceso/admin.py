from django.contrib import admin
from .models import Credencial, RegistroAcceso

@admin.register(Credencial)
class CredencialAdmin(admin.ModelAdmin):
	list_display = ("id", "persona", "tipo_credencial", "identificador", "estado")
	search_fields = ("persona__nombre", "identificador")
	list_filter = ("estado", "tipo_credencial")

@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
	list_display = ("id", "cliente", "sede", "fecha_hora_entrada", "autorizado", "membresia_nombre")
	search_fields = ("cliente__persona__nombre", "cliente__persona__apellido_paterno", "cliente__persona__apellido_materno")
	list_filter = ("autorizado", "sede", "fecha_hora_entrada")
	readonly_fields = ("fecha_hora_entrada", "tiempo_permanencia")

	def tiempo_permanencia(self, obj):
		"""Muestra el tiempo de permanencia en el admin"""
		return f"{obj.tiempo_permanencia} minutos" if obj.tiempo_permanencia else "Aún en instalaciones"
	tiempo_permanencia.short_description = "Tiempo de Permanencia"
