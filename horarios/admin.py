from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TipoActividad, Horario, SesionClase, BloqueoHorario


@admin.register(TipoActividad)
class TipoActividadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'duracion_default', 'color_preview', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div>',
            obj.color_hex
        )
    color_preview.short_description = 'Color'


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = [
        'tipo_actividad', 'dia_semana', 'hora_inicio', 'hora_fin', 
        'entrenador_nombre', 'espacio_info', 'estado', 'cupo_maximo'
    ]
    list_filter = [
        'estado', 'dia_semana', 'tipo_actividad', 
        'espacio__sede', 'entrenador__sede'
    ]
    search_fields = [
        'tipo_actividad__nombre', 
        'entrenador__empleado__persona__nombre',
        'entrenador__empleado__persona__apellido_paterno',
        'espacio__nombre'
    ]
    date_hierarchy = 'fecha_inicio'
    list_editable = ['estado']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tipo_actividad', 'entrenador', 'espacio')
        }),
        ('Horario', {
            'fields': ('dia_semana', 'hora_inicio', 'hora_fin')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Configuración', {
            'fields': ('cupo_maximo', 'estado', 'observaciones')
        }),
    )
    
    def entrenador_nombre(self, obj):
        persona = obj.entrenador.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno}"
    entrenador_nombre.short_description = 'Entrenador'
    entrenador_nombre.admin_order_field = 'entrenador__empleado__persona__nombre'
    
    def espacio_info(self, obj):
        return f"{obj.espacio.nombre} ({obj.espacio.sede.nombre})"
    espacio_info.short_description = 'Espacio'
    espacio_info.admin_order_field = 'espacio__nombre'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tipo_actividad',
            'entrenador__empleado__persona',
            'espacio__sede'
        )


@admin.register(SesionClase)
class SesionClaseAdmin(admin.ModelAdmin):
    list_display = [
        'horario_info', 'fecha', 'entrenador_efectivo_nombre', 
        'espacio_efectivo_info', 'estado', 'ocupacion'
    ]
    list_filter = [
        'estado', 'fecha', 'horario__tipo_actividad',
        'horario__espacio__sede'
    ]
    search_fields = [
        'horario__tipo_actividad__nombre',
        'horario__entrenador__empleado__persona__nombre',
        'entrenador_override__empleado__persona__nombre'
    ]
    date_hierarchy = 'fecha'
    list_editable = ['estado']
    
    fieldsets = (
        ('Información Base', {
            'fields': ('horario', 'fecha', 'estado')
        }),
        ('Overrides (Cambios Específicos)', {
            'fields': (
                'entrenador_override', 'espacio_override',
                'hora_inicio_override', 'hora_fin_override', 'cupo_override'
            ),
            'classes': ('collapse',)
        }),
        ('Asistencia', {
            'fields': ('asistentes_registrados', 'observaciones')
        }),
    )
    
    def horario_info(self, obj):
        return f"{obj.horario.tipo_actividad.nombre} - {obj.horario.dia_semana.title()}"
    horario_info.short_description = 'Horario Base'
    
    def entrenador_efectivo_nombre(self, obj):
        entrenador = obj.entrenador_efectivo
        persona = entrenador.empleado.persona
        nombre = f"{persona.nombre} {persona.apellido_paterno}"
        if obj.entrenador_override:
            return format_html('<span style="color: orange;">{} (Sustituto)</span>', nombre)
        return nombre
    entrenador_efectivo_nombre.short_description = 'Entrenador'
    
    def espacio_efectivo_info(self, obj):
        espacio = obj.espacio_efectivo
        info = f"{espacio.nombre} ({espacio.sede.nombre})"
        if obj.espacio_override:
            return format_html('<span style="color: orange;">{} (Alternativo)</span>', info)
        return info
    espacio_efectivo_info.short_description = 'Espacio'
    
    def ocupacion(self, obj):
        porcentaje = (obj.asistentes_registrados / obj.cupo_efectivo) * 100 if obj.cupo_efectivo > 0 else 0
        color = 'green' if porcentaje < 80 else 'orange' if porcentaje < 100 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color, obj.asistentes_registrados, obj.cupo_efectivo, int(porcentaje)
        )
    ocupacion.short_description = 'Ocupación'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'horario__tipo_actividad',
            'horario__entrenador__empleado__persona',
            'horario__espacio__sede',
            'entrenador_override__empleado__persona',
            'espacio_override__sede'
        )


@admin.register(BloqueoHorario)
class BloqueoHorarioAdmin(admin.ModelAdmin):
    list_display = [
        'motivo', 'tipo_bloqueo', 'afectado', 'fecha_inicio', 
        'fecha_fin', 'duracion_display'
    ]
    list_filter = ['tipo_bloqueo', 'fecha_inicio', 'entrenador__sede', 'espacio__sede']
    search_fields = [
        'motivo', 'descripcion',
        'entrenador__empleado__persona__nombre',
        'espacio__nombre'
    ]
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Tipo de Bloqueo', {
            'fields': ('tipo_bloqueo', 'motivo', 'descripcion')
        }),
        ('Afectados', {
            'fields': ('entrenador', 'espacio'),
            'description': 'Selecciona al menos uno: entrenador o espacio'
        }),
        ('Período', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Metadatos', {
            'fields': ('creado_por',),
            'classes': ('collapse',)
        }),
    )
    
    def afectado(self, obj):
        partes = []
        if obj.entrenador:
            persona = obj.entrenador.empleado.persona
            partes.append(f"👨‍🏫 {persona.nombre} {persona.apellido_paterno}")
        if obj.espacio:
            partes.append(f"🏢 {obj.espacio.nombre}")
        return " + ".join(partes)
    afectado.short_description = 'Afectado'
    
    def duracion_display(self, obj):
        duracion = obj.fecha_fin - obj.fecha_inicio
        dias = duracion.days
        horas = duracion.seconds // 3600
        if dias > 0:
            return f"{dias}d {horas}h"
        return f"{horas}h"
    duracion_display.short_description = 'Duración'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'entrenador__empleado__persona',
            'espacio__sede'
        )


# Configuración adicional del admin
admin.site.site_header = "Administración de Horarios - Gimnasio"
admin.site.site_title = "Horarios Gimnasio"
admin.site.index_title = "Panel de Administración de Horarios"