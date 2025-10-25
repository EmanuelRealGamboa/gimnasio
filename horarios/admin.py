from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    TipoActividad, Horario, SesionClase, BloqueoHorario,
    EquipoActividad, ClienteMembresia, ReservaClase, 
    ReservaEquipo, ReservaEntrenador
)


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


@admin.register(EquipoActividad)
class EquipoActividadAdmin(admin.ModelAdmin):
    list_display = ['tipo_actividad', 'activo_info', 'cantidad_necesaria', 'obligatorio']
    list_filter = ['obligatorio', 'tipo_actividad', 'activo__categoria']
    search_fields = ['tipo_actividad__nombre', 'activo__nombre', 'activo__codigo']
    
    def activo_info(self, obj):
        return f"{obj.activo.codigo} - {obj.activo.nombre}"
    activo_info.short_description = 'Activo'


@admin.register(ClienteMembresia)
class ClienteMembresiaAdmin(admin.ModelAdmin):
    list_display = ['cliente_nombre', 'membresia', 'fecha_inicio', 'fecha_fin', 'estado', 'dias_restantes_display']
    list_filter = ['estado', 'membresia__tipo', 'fecha_inicio']
    search_fields = [
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'membresia__nombre_plan'
    ]
    date_hierarchy = 'fecha_inicio'
    
    def cliente_nombre(self, obj):
        return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
    cliente_nombre.short_description = 'Cliente'
    
    def dias_restantes_display(self, obj):
        dias = obj.dias_restantes
        if dias > 30:
            color = 'green'
        elif dias > 7:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{} días</span>', color, dias)
    dias_restantes_display.short_description = 'Días Restantes'


@admin.register(ReservaClase)
class ReservaClaseAdmin(admin.ModelAdmin):
    list_display = [
        'cliente_nombre', 'actividad_info', 'fecha_sesion', 
        'entrenador_nombre', 'estado', 'fecha_reserva'
    ]
    list_filter = [
        'estado', 'sesion_clase__horario__tipo_actividad',
        'sesion_clase__fecha', 'sesion_clase__horario__espacio__sede'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'sesion_clase__horario__tipo_actividad__nombre'
    ]
    date_hierarchy = 'sesion_clase__fecha'
    
    def cliente_nombre(self, obj):
        return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
    cliente_nombre.short_description = 'Cliente'
    
    def actividad_info(self, obj):
        return obj.sesion_clase.horario.tipo_actividad.nombre
    actividad_info.short_description = 'Actividad'
    
    def fecha_sesion(self, obj):
        return obj.sesion_clase.fecha
    fecha_sesion.short_description = 'Fecha Sesión'
    
    def entrenador_nombre(self, obj):
        entrenador = obj.sesion_clase.entrenador_efectivo
        return f"{entrenador.empleado.persona.nombre} {entrenador.empleado.persona.apellido_paterno}"
    entrenador_nombre.short_description = 'Entrenador'


@admin.register(ReservaEquipo)
class ReservaEquipoAdmin(admin.ModelAdmin):
    list_display = [
        'cliente_nombre', 'equipo_info', 'fecha_reserva', 
        'horario_reserva', 'estado', 'duracion_display'
    ]
    list_filter = [
        'estado', 'fecha_reserva', 'activo__categoria',
        'activo__sede'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'activo__nombre', 'activo__codigo'
    ]
    date_hierarchy = 'fecha_reserva'
    
    def cliente_nombre(self, obj):
        return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
    cliente_nombre.short_description = 'Cliente'
    
    def equipo_info(self, obj):
        return f"{obj.activo.codigo} - {obj.activo.nombre}"
    equipo_info.short_description = 'Equipo'
    
    def horario_reserva(self, obj):
        return f"{obj.hora_inicio} - {obj.hora_fin}"
    horario_reserva.short_description = 'Horario'
    
    def duracion_display(self, obj):
        duracion = obj.duracion_programada
        horas = duracion.seconds // 3600
        minutos = (duracion.seconds % 3600) // 60
        return f"{horas}h {minutos}m"
    duracion_display.short_description = 'Duración'


@admin.register(ReservaEntrenador)
class ReservaEntrenadorAdmin(admin.ModelAdmin):
    list_display = [
        'cliente_nombre', 'entrenador_nombre', 'fecha_sesion',
        'horario_sesion', 'tipo_sesion', 'estado', 'precio'
    ]
    list_filter = [
        'estado', 'tipo_sesion', 'fecha_sesion',
        'entrenador__sede'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'entrenador__empleado__persona__nombre',
        'entrenador__empleado__persona__apellido_paterno'
    ]
    date_hierarchy = 'fecha_sesion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'entrenador', 'tipo_sesion', 'estado')
        }),
        ('Horario', {
            'fields': ('fecha_sesion', 'hora_inicio', 'hora_fin', 'espacio')
        }),
        ('Detalles de la Sesión', {
            'fields': ('objetivo', 'precio', 'clientes_adicionales')
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'notas_entrenador'),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_nombre(self, obj):
        return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
    cliente_nombre.short_description = 'Cliente'
    
    def entrenador_nombre(self, obj):
        return f"{obj.entrenador.empleado.persona.nombre} {obj.entrenador.empleado.persona.apellido_paterno}"
    entrenador_nombre.short_description = 'Entrenador'
    
    def horario_sesion(self, obj):
        return f"{obj.hora_inicio} - {obj.hora_fin}"
    horario_sesion.short_description = 'Horario'


# Configuración adicional del admin
admin.site.site_header = "Administración de Horarios y Reservas - Gimnasio"
admin.site.site_title = "Horarios Gimnasio"
admin.site.index_title = "Panel de Administración de Horarios y Reservas"