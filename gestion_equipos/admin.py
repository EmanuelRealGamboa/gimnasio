from django.contrib import admin
from .models import CategoriaActivo, ProveedorServicio, Activo, Mantenimiento, OrdenMantenimiento


@admin.register(CategoriaActivo)
class CategoriaActivoAdmin(admin.ModelAdmin):
    list_display = ['categoria_activo_id', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(ProveedorServicio)
class ProveedorServicioAdmin(admin.ModelAdmin):
    list_display = ['proveedor_id', 'nombre_empresa', 'nombre_contacto', 'telefono', 'email', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre_empresa', 'nombre_contacto', 'telefono', 'email']
    ordering = ['nombre_empresa']
    readonly_fields = ['fecha_registro']


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ['activo_id', 'codigo', 'nombre', 'categoria', 'estado', 'sede', 'valor', 'fecha_compra']
    list_filter = ['estado', 'categoria', 'sede', 'fecha_compra']
    search_fields = ['codigo', 'nombre', 'marca', 'modelo', 'numero_serie']
    ordering = ['-fecha_creacion']
    readonly_fields = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'en_mantenimiento']

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'categoria', 'estado')
        }),
        ('Información de Compra', {
            'fields': ('fecha_compra', 'valor')
        }),
        ('Ubicación', {
            'fields': ('sede', 'espacio', 'ubicacion')
        }),
        ('Detalles Técnicos', {
            'fields': ('marca', 'modelo', 'numero_serie', 'descripcion', 'imagen')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion', 'en_mantenimiento'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['mantenimiento_id', 'activo', 'tipo_mantenimiento', 'fecha_programada', 'fecha_ejecucion', 'estado', 'costo', 'get_responsable']
    list_filter = ['tipo_mantenimiento', 'estado', 'fecha_programada', 'fecha_ejecucion']
    search_fields = ['activo__codigo', 'activo__nombre', 'descripcion']
    ordering = ['-fecha_programada']
    readonly_fields = ['creado_por', 'fecha_creacion', 'fecha_actualizacion', 'dias_para_mantenimiento', 'requiere_atencion']

    fieldsets = (
        ('Información del Mantenimiento', {
            'fields': ('activo', 'tipo_mantenimiento', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_programada', 'fecha_ejecucion', 'dias_para_mantenimiento', 'requiere_atencion')
        }),
        ('Responsable', {
            'fields': ('proveedor_servicio', 'empleado_responsable')
        }),
        ('Detalles', {
            'fields': ('costo', 'descripcion', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def get_responsable(self, obj):
        if obj.proveedor_servicio:
            return f"Externo: {obj.proveedor_servicio.nombre_empresa}"
        elif obj.empleado_responsable:
            persona = obj.empleado_responsable.persona
            return f"Interno: {persona.nombre} {persona.apellido_paterno}"
        return "Sin asignar"
    get_responsable.short_description = 'Responsable'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrdenMantenimiento)
class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['orden_id', 'numero_orden', 'get_activo', 'prioridad', 'estado_orden', 'fecha_emision', 'tiempo_estimado']
    list_filter = ['prioridad', 'estado_orden', 'fecha_emision']
    search_fields = ['numero_orden', 'mantenimiento__activo__codigo', 'mantenimiento__activo__nombre']
    ordering = ['-fecha_emision']
    readonly_fields = ['numero_orden', 'fecha_emision', 'creado_por', 'fecha_actualizacion']

    fieldsets = (
        ('Información de la Orden', {
            'fields': ('numero_orden', 'mantenimiento', 'prioridad', 'estado_orden')
        }),
        ('Detalles de Ejecución', {
            'fields': ('tiempo_estimado', 'materiales_necesarios')
        }),
        ('Auditoría', {
            'fields': ('fecha_emision', 'creado_por', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def get_activo(self, obj):
        return f"{obj.mantenimiento.activo.codigo} - {obj.mantenimiento.activo.nombre}"
    get_activo.short_description = 'Activo'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
