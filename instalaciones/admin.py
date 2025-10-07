from django.contrib import admin
from .models import Sede, Espacio

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "direccion", "telefono")
	search_fields = ("nombre", "direccion")

@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "sede", "capacidad")
	search_fields = ("nombre",)
	list_filter = ("sede",)
