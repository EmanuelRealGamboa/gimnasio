from rest_framework import serializers
from .models import (
    PersonalLimpieza,
    TareaLimpieza,
    HorarioLimpieza,
    AsignacionTarea,
    ChecklistLimpieza,
    Empleado
)
from instalaciones.models import Sede, Espacio


class TareaLimpiezaSerializer(serializers.ModelSerializer):
    """
    Serializer para el catálogo de tareas de limpieza.
    """
    tipo_espacio_display = serializers.CharField(source='get_tipo_espacio_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)

    class Meta:
        model = TareaLimpieza
        fields = [
            'id',
            'nombre',
            'descripcion',
            'tipo_espacio',
            'tipo_espacio_display',
            'duracion_estimada',
            'prioridad',
            'prioridad_display',
            'activo',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']


class PersonalLimpiezaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar personal de limpieza con información básica.
    """
    empleado_id = serializers.IntegerField(source='empleado.persona_id', read_only=True)
    empleado_nombre = serializers.SerializerMethodField()
    sede_id = serializers.IntegerField(source='sede.id', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    espacios_asignados = serializers.SerializerMethodField()
    tareas_pendientes_count = serializers.SerializerMethodField()
    email = serializers.CharField(source='empleado.persona.usuario.email', read_only=True)
    telefono = serializers.CharField(source='empleado.persona.telefono', read_only=True)

    class Meta:
        model = PersonalLimpieza
        fields = [
            'empleado_id',
            'empleado_nombre',
            'email',
            'telefono',
            'turno',
            'sede_id',
            'sede_nombre',
            'espacios_asignados',
            'tareas_pendientes_count',
        ]

    def get_empleado_nombre(self, obj):
        persona = obj.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}".strip()

    def get_espacios_asignados(self, obj):
        return [
            {
                'id': espacio.id,
                'nombre': espacio.nombre,
                'sede': espacio.sede.nombre
            }
            for espacio in obj.espacio.all()
        ]

    def get_tareas_pendientes_count(self, obj):
        from datetime import date
        return obj.asignaciones.filter(
            fecha=date.today(),
            estado__in=['pendiente', 'en_progreso']
        ).count()


class HorarioLimpiezaSerializer(serializers.ModelSerializer):
    """
    Serializer para horarios de limpieza.
    """
    personal_nombre = serializers.SerializerMethodField()
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='espacio.sede.nombre', read_only=True)
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = HorarioLimpieza
        fields = [
            'id',
            'personal_limpieza',
            'personal_nombre',
            'espacio',
            'espacio_nombre',
            'sede_nombre',
            'dia_semana',
            'dia_semana_display',
            'hora_inicio',
            'hora_fin',
            'activo',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_personal_nombre(self, obj):
        persona = obj.personal_limpieza.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno}"


class ChecklistLimpiezaSerializer(serializers.ModelSerializer):
    """
    Serializer para checklist de limpieza.
    """
    verificado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistLimpieza
        fields = [
            'id',
            'asignacion',
            'items',
            'verificado',
            'verificado_por',
            'verificado_por_nombre',
            'fecha_verificacion',
            'observaciones',
            'calificacion',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_verificado_por_nombre(self, obj):
        if obj.verificado_por:
            persona = obj.verificado_por.persona
            return f"{persona.nombre} {persona.apellido_paterno}"
        return None


class AsignacionTareaSerializer(serializers.ModelSerializer):
    """
    Serializer para asignaciones de tareas de limpieza.
    """
    personal_nombre = serializers.SerializerMethodField()
    tarea_nombre = serializers.CharField(source='tarea.nombre', read_only=True)
    tarea_duracion = serializers.IntegerField(source='tarea.duracion_estimada', read_only=True)
    tarea_prioridad = serializers.CharField(source='tarea.prioridad', read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='espacio.sede.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    completada_por_nombre = serializers.SerializerMethodField()
    asignado_por_nombre = serializers.SerializerMethodField()
    checklist = ChecklistLimpiezaSerializer(read_only=True)

    class Meta:
        model = AsignacionTarea
        fields = [
            'id',
            'personal_limpieza',
            'personal_nombre',
            'tarea',
            'tarea_nombre',
            'tarea_duracion',
            'tarea_prioridad',
            'espacio',
            'espacio_nombre',
            'sede_nombre',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'estado_display',
            'fecha_completada',
            'completada_por',
            'completada_por_nombre',
            'notas',
            'observaciones_completado',
            'asignado_por',
            'asignado_por_nombre',
            'fecha_creacion',
            'fecha_actualizacion',
            'checklist',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_personal_nombre(self, obj):
        persona = obj.personal_limpieza.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno}"

    def get_completada_por_nombre(self, obj):
        if obj.completada_por:
            persona = obj.completada_por.empleado.persona
            return f"{persona.nombre} {persona.apellido_paterno}"
        return None

    def get_asignado_por_nombre(self, obj):
        if obj.asignado_por:
            persona = obj.asignado_por.persona
            return f"{persona.nombre} {persona.apellido_paterno}"
        return None


class AsignacionTareaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear asignaciones de tareas.

    Flujo:
    - Administrador selecciona: sede -> empleado -> espacio -> tarea -> fecha -> notas
    - hora_inicio se guarda automáticamente al crear (hora actual)
    - hora_fin se guardará cuando empleado confirme desde app móvil
    """
    class Meta:
        model = AsignacionTarea
        fields = [
            'personal_limpieza',
            'tarea',
            'espacio',
            'fecha',
            'notas',
        ]

    def create(self, validated_data):
        from datetime import datetime
        # Guardar hora_inicio automáticamente al crear la asignación
        validated_data['hora_inicio'] = datetime.now().time()
        return super().create(validated_data)


class EstadisticasLimpiezaSerializer(serializers.Serializer):
    """
    Serializer para estadísticas del módulo de limpieza.
    """
    tareas_completadas = serializers.IntegerField()
    tareas_pendientes = serializers.IntegerField()
    tareas_en_progreso = serializers.IntegerField()
    tareas_canceladas = serializers.IntegerField()
    tasa_cumplimiento = serializers.FloatField()
    calificacion_promedio = serializers.FloatField()
    total_personal = serializers.IntegerField()
    espacios_limpios_hoy = serializers.IntegerField()
