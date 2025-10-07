from django.contrib import admin
from .models import Credencial, RegistroAcceso

@admin.register(Credencial)
class CredencialAdmin(admin.ModelAdmin):
	list_display = ("id", "persona", "tipo_credencial", "identificador", "estado")
	search_fields = ("persona__nombre", "identificador")
	list_filter = ("estado", "tipo_credencial")

@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
	list_display = ("id", "credencial", "fecha_hora", "autorizado", "espacio")
	search_fields = ("credencial__identificador",)
	list_filter = ("autorizado", "espacio")
