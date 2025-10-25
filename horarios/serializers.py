from rest_framework import serializers
from django.utils import timezone
from .models import TipoActividad, Horario, SesionClase, BloqueoHorario
from empleados.models import Entrenador
from instalaciones.models import Espacio


class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = '__all__'


class EntrenadorBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para entrenador en horarios"""
    nombre_completo = serializers.SerializerMethodField()
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    
    class Meta:
        model = Entrenador
        fields = ['empleado', 'nombre_completo', 'especialidad', 'sede_nombre']
    
    def get_nombre_completo(self, obj):
        persona = obj.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"


class EspacioBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para espacio en horarios"""
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    
    class Meta:
        model = Espacio
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'sede_nombre']


class HorarioSerializer(serializers.ModelSerializer):
    tipo_actividad_detalle = TipoActividadSerializer(source='tipo_actividad', read_only=True)
    entrenador_detalle = EntrenadorBasicSerializer(source='entrenador', read_only=True)
    espacio_detalle = EspacioBasicSerializer(source='espacio', read_only=True)
    duracion = serializers.ReadOnlyField()
    sede_nombre = serializers.CharField(source='espacio.sede.nombre', read_only=True)
    
    class Meta:
        model = Horario
        fields = [
            'id', 'tipo_actividad', 'entrenador', 'espacio',
            'dia_semana', 'hora_inicio', 'hora_fin',
            'fecha_inicio', 'fecha_fin', 'cupo_maximo', 'estado',
            'observaciones', 'fecha_creacion', 'fecha_modificacion',
            # Campos calculados y relacionados
            'tipo_actividad_detalle', 'entrenador_detalle', 'espacio_detalle',
            'duracion', 'sede_nombre'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que el entrenador esté asignado al espacio
        if 'entrenador' in data and 'espacio' in data:
            entrenador = data['entrenador']
            espacio = data['espacio']
            
            if not entrenador.espacio.filter(id=espacio.id).exists():
                raise serializers.ValidationError(
                    f"El entrenador {entrenador.empleado.persona.nombre} "
                    f"no está asignado al espacio {espacio.nombre}"
                )
            
            # Validar que estén en la misma sede
            if entrenador.sede != espacio.sede:
                raise serializers.ValidationError(
                    f"El entrenador y el espacio deben estar en la misma sede"
                )
        
        return data


class HorarioCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear horarios"""
    
    class Meta:
        model = Horario
        fields = [
            'tipo_actividad', 'entrenador', 'espacio',
            'dia_semana', 'hora_inicio', 'hora_fin',
            'fecha_inicio', 'fecha_fin', 'cupo_maximo',
            'observaciones'
        ]
    
    def validate(self, data):
        """Validaciones para creación"""
        # Reutilizar validaciones del serializer principal
        return HorarioSerializer().validate(data)


class SesionClaseSerializer(serializers.ModelSerializer):
    horario_detalle = HorarioSerializer(source='horario', read_only=True)
    entrenador_efectivo_detalle = EntrenadorBasicSerializer(source='entrenador_efectivo', read_only=True)
    espacio_efectivo_detalle = EspacioBasicSerializer(source='espacio_efectivo', read_only=True)
    
    # Campos calculados
    hora_inicio_efectiva = serializers.ReadOnlyField()
    hora_fin_efectiva = serializers.ReadOnlyField()
    cupo_efectivo = serializers.ReadOnlyField()
    lugares_disponibles = serializers.ReadOnlyField()
    esta_llena = serializers.ReadOnlyField()
    
    class Meta:
        model = SesionClase
        fields = [
            'id', 'horario', 'fecha', 'estado',
            'entrenador_override', 'espacio_override',
            'hora_inicio_override', 'hora_fin_override', 'cupo_override',
            'asistentes_registrados', 'observaciones',
            'fecha_creacion', 'fecha_modificacion',
            # Campos relacionados y calculados
            'horario_detalle', 'entrenador_efectivo_detalle', 'espacio_efectivo_detalle',
            'hora_inicio_efectiva', 'hora_fin_efectiva', 'cupo_efectivo',
            'lugares_disponibles', 'esta_llena'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']


class SesionClaseCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear sesiones de clase"""
    
    class Meta:
        model = SesionClase
        fields = [
            'horario', 'fecha', 'entrenador_override', 'espacio_override',
            'hora_inicio_override', 'hora_fin_override', 'cupo_override',
            'observaciones'
        ]
    
    def validate_fecha(self, value):
        """Validar que la fecha no sea en el pasado"""
        if value < timezone.now().date():
            raise serializers.ValidationError("No se pueden crear sesiones en fechas pasadas")
        return value


class BloqueoHorarioSerializer(serializers.ModelSerializer):
    entrenador_detalle = EntrenadorBasicSerializer(source='entrenador', read_only=True)
    espacio_detalle = EspacioBasicSerializer(source='espacio', read_only=True)
    duracion_horas = serializers.SerializerMethodField()
    
    class Meta:
        model = BloqueoHorario
        fields = [
            'id', 'entrenador', 'espacio', 'tipo_bloqueo',
            'fecha_inicio', 'fecha_fin', 'motivo', 'descripcion',
            'fecha_creacion', 'creado_por',
            # Campos relacionados y calculados
            'entrenador_detalle', 'espacio_detalle', 'duracion_horas'
        ]
        read_only_fields = ['fecha_creacion']
    
    def get_duracion_horas(self, obj):
        """Calcular duración en horas"""
        duracion = obj.fecha_fin - obj.fecha_inicio
        return round(duracion.total_seconds() / 3600, 2)
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if not data.get('entrenador') and not data.get('espacio'):
            raise serializers.ValidationError(
                "Debe especificar al menos un entrenador o un espacio a bloquear"
            )
        return data


class HorarioCalendarioSerializer(serializers.ModelSerializer):
    """Serializer optimizado para vista de calendario"""
    titulo = serializers.SerializerMethodField()
    color = serializers.CharField(source='tipo_actividad.color_hex', read_only=True)
    entrenador_nombre = serializers.SerializerMethodField()
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    
    class Meta:
        model = Horario
        fields = [
            'id', 'dia_semana', 'hora_inicio', 'hora_fin',
            'cupo_maximo', 'estado', 'titulo', 'color',
            'entrenador_nombre', 'espacio_nombre'
        ]
    
    def get_titulo(self, obj):
        return obj.tipo_actividad.nombre
    
    def get_entrenador_nombre(self, obj):
        persona = obj.entrenador.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno}"


class SesionCalendarioSerializer(serializers.ModelSerializer):
    """Serializer optimizado para sesiones en calendario"""
    titulo = serializers.CharField(source='horario.tipo_actividad.nombre', read_only=True)
    color = serializers.CharField(source='horario.tipo_actividad.color_hex', read_only=True)
    entrenador_nombre = serializers.SerializerMethodField()
    espacio_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionClase
        fields = [
            'id', 'fecha', 'estado', 'asistentes_registrados',
            'hora_inicio_efectiva', 'hora_fin_efectiva', 'cupo_efectivo',
            'titulo', 'color', 'entrenador_nombre', 'espacio_nombre'
        ]
    
    def get_entrenador_nombre(self, obj):
        entrenador = obj.entrenador_efectivo
        persona = entrenador.empleado.persona
        return f"{persona.nombre} {persona.apellido_paterno}"
    
    def get_espacio_nombre(self, obj):
        return obj.espacio_efectivo.nombre


class HorarioDisponibilidadSerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad de horarios"""
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    sede_id = serializers.IntegerField(required=False)
    entrenador_id = serializers.IntegerField(required=False)
    espacio_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        return data
