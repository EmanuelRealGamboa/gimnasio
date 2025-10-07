from django.contrib import admin
from .models import Rol, Permiso, RolPermiso, PersonaRol

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "descripcion")
	search_fields = ("nombre",)

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "descripcion")
	search_fields = ("nombre",)

@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
	list_display = ("id", "rol", "permiso")
	list_filter = ("rol", "permiso")

@admin.register(PersonaRol)
class PersonaRolAdmin(admin.ModelAdmin):
	list_display = ("id", "persona", "rol")
	list_filter = ("rol",)
