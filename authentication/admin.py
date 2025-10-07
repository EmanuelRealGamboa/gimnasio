from django.contrib import admin
from .models import Persona, User, ContactoEmergencia

# Registro de modelos para el panel de administración
@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "apellido_paterno", "apellido_materno", "telefono")
	search_fields = ("nombre", "apellido_paterno", "apellido_materno", "telefono")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "email", "persona", "is_active", "is_staff", "is_superuser")
	search_fields = ("email",)
	list_filter = ("is_active", "is_staff", "is_superuser")

@admin.register(ContactoEmergencia)
class ContactoEmergenciaAdmin(admin.ModelAdmin):
	list_display = ("id", "persona", "nombre_contacto", "telefono_contacto", "parentesco")
	search_fields = ("nombre_contacto", "telefono_contacto", "parentesco")
