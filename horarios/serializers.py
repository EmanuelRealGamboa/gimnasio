from rest_framework import serializers
from django.utils import timezone
from .models import (
    TipoActividad, Horario, SesionClase, BloqueoHorario,
    EquipoActividad, ClienteMembresia, ReservaClase,
    ReservaEquipo, ReservaEntrenador
)
from empleados.models import Entrenador
from instalaciones.models import Espacio
from clientes.models import Cliente
from gestion_equipos.models import Activo
from membresias.models import SuscripcionMembresia


class TipoActividadSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True, allow_null=True)
    duracion_horas = serializers.ReadOnlyField()
    duracion_texto = serializers.ReadOnlyField()

    class Meta:
        model = TipoActividad
        fields = ['id', 'nombre', 'descripcion', 'duracion_default', 'color_hex', 'activo', 'sede', 'sede_nombre', 'duracion_horas', 'duracion_texto']


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
    
    # Campos simples para el frontend
    tipo_actividad_nombre = serializers.CharField(source='tipo_actividad.nombre', read_only=True)
    entrenador_nombre = serializers.SerializerMethodField()
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    
    class Meta:
        model = Horario
        fields = [
            'id', 'tipo_actividad', 'entrenador', 'espacio',
            'dia_semana', 'hora_inicio', 'hora_fin',
            'fecha_inicio', 'fecha_fin', 'cupo_maximo', 'estado',
            'observaciones', 'fecha_creacion', 'fecha_modificacion',
            # Campos calculados y relacionados
            'tipo_actividad_detalle', 'entrenador_detalle', 'espacio_detalle',
            'duracion', 'sede_nombre',
            # Campos simples para tablas
            'tipo_actividad_nombre', 'entrenador_nombre', 'espacio_nombre'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_entrenador_nombre(self, obj):
        if obj.entrenador and obj.entrenador.empleado and obj.entrenador.empleado.persona:
            persona = obj.entrenador.empleado.persona
            return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
        return ""
    
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


class SesionDisponibleSerializer(serializers.ModelSerializer):
    """Serializer completo para sesiones disponibles para reservar"""
    actividad = serializers.SerializerMethodField()
    entrenador = serializers.SerializerMethodField()
    espacio = serializers.SerializerMethodField()
    sede = serializers.SerializerMethodField()
    hora_inicio = serializers.TimeField(source='hora_inicio_efectiva', read_only=True)
    hora_fin = serializers.TimeField(source='hora_fin_efectiva', read_only=True)
    cupo_total = serializers.IntegerField(source='cupo_efectivo', read_only=True)
    lugares_disponibles = serializers.SerializerMethodField()
    puede_reservar = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()

    class Meta:
        model = SesionClase
        fields = [
            'id', 'fecha', 'estado', 'actividad', 'entrenador', 'espacio', 'sede',
            'hora_inicio', 'hora_fin', 'cupo_total', 'lugares_disponibles',
            'puede_reservar', 'categoria'
        ]

    def get_actividad(self, obj):
        tipo = obj.horario.tipo_actividad
        return {
            'id': tipo.id,
            'nombre': tipo.nombre,
            'descripcion': tipo.descripcion,
            'color': tipo.color_hex,
            'duracion': str(tipo.duracion_default) if tipo.duracion_default else None
        }

    def get_entrenador(self, obj):
        entrenador = obj.entrenador_efectivo
        persona = entrenador.empleado.persona
        return {
            'id': entrenador.empleado_id,
            'nombre': f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}",
            'especialidad': entrenador.especialidad
        }

    def get_espacio(self, obj):
        espacio = obj.espacio_efectivo
        return {
            'id': espacio.id,
            'nombre': espacio.nombre,
            'capacidad': espacio.capacidad
        }

    def get_sede(self, obj):
        sede = obj.horario.espacio.sede
        return {
            'id': sede.id,
            'nombre': sede.nombre
        }

    def get_lugares_disponibles(self, obj):
        return obj.cupo_efectivo - obj.asistentes_registrados

    def get_puede_reservar(self, obj):
        return obj.estado == 'programada' and obj.asistentes_registrados < obj.cupo_efectivo

    def get_categoria(self, obj):
        # Por defecto todas las sesiones son "basico", podríamos agregar lógica aquí
        return 'basico'


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


class ClienteBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para cliente"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = ['persona', 'nombre_completo', 'objetivo_fitness', 'nivel_experiencia', 'estado']
    
    def get_nombre_completo(self, obj):
        persona = obj.persona
        return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"


class ActivoBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para activo"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    
    class Meta:
        model = Activo
        fields = ['activo_id', 'codigo', 'nombre', 'categoria_nombre', 'estado', 'sede_nombre']


class EquipoActividadSerializer(serializers.ModelSerializer):
    tipo_actividad_detalle = TipoActividadSerializer(source='tipo_actividad', read_only=True)
    activo_detalle = ActivoBasicSerializer(source='activo', read_only=True)
    
    class Meta:
        model = EquipoActividad
        fields = [
            'id', 'tipo_actividad', 'activo', 'cantidad_necesaria', 'obligatorio',
            'tipo_actividad_detalle', 'activo_detalle'
        ]


class ClienteMembresiaSerializer(serializers.ModelSerializer):
    cliente_detalle = ClienteBasicSerializer(source='cliente', read_only=True)
    membresia_nombre = serializers.CharField(source='membresia.nombre_plan', read_only=True)
    esta_activa = serializers.ReadOnlyField()
    dias_restantes = serializers.ReadOnlyField()
    
    class Meta:
        model = ClienteMembresia
        fields = [
            'id', 'cliente', 'membresia', 'fecha_inicio', 'fecha_fin', 'estado',
            'fecha_creacion', 'fecha_modificacion',
            'cliente_detalle', 'membresia_nombre', 'esta_activa', 'dias_restantes'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']


class ReservaClaseSerializer(serializers.ModelSerializer):
    cliente_detalle = ClienteBasicSerializer(source='cliente', read_only=True)
    sesion_detalle = SesionClaseSerializer(source='sesion_clase', read_only=True)

    # Campos simples para frontend (cards)
    codigo_reserva = serializers.ReadOnlyField()
    cliente_nombre = serializers.SerializerMethodField()
    sesion_actividad = serializers.CharField(source='sesion_clase.horario.tipo_actividad.nombre', read_only=True)
    sesion_fecha = serializers.DateField(source='sesion_clase.fecha', read_only=True)
    sesion_hora_inicio = serializers.TimeField(source='sesion_clase.hora_inicio_efectiva', read_only=True)
    sesion_hora_fin = serializers.TimeField(source='sesion_clase.hora_fin_efectiva', read_only=True)
    sesion_entrenador = serializers.SerializerMethodField()
    sesion_espacio = serializers.CharField(source='sesion_clase.espacio_efectivo.nombre', read_only=True)
    sesion_sede = serializers.CharField(source='sesion_clase.espacio_efectivo.sede.nombre', read_only=True)

    class Meta:
        model = ReservaClase
        fields = [
            'id', 'cliente', 'sesion_clase', 'fecha_reserva', 'estado',
            'observaciones', 'fecha_cancelacion', 'motivo_cancelacion',
            'cliente_detalle', 'sesion_detalle',
            # Campos simples para cards
            'codigo_reserva', 'cliente_nombre', 'sesion_actividad', 'sesion_fecha',
            'sesion_hora_inicio', 'sesion_hora_fin', 'sesion_entrenador',
            'sesion_espacio', 'sesion_sede'
        ]
        read_only_fields = ['fecha_reserva', 'fecha_cancelacion']

    def get_cliente_nombre(self, obj):
        if obj.cliente and obj.cliente.persona:
            persona = obj.cliente.persona
            return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
        return ""

    def get_sesion_entrenador(self, obj):
        if obj.sesion_clase:
            entrenador = obj.sesion_clase.entrenador_efectivo
            if entrenador and entrenador.empleado and entrenador.empleado.persona:
                persona = entrenador.empleado.persona
                return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
        return ""

    def validate(self, data):
        """Validaciones personalizadas"""
        cliente = data.get('cliente')
        sesion_clase = data.get('sesion_clase')

        if cliente and sesion_clase:
            # Verificar membresía activa - buscar en el modelo correcto (SuscripcionMembresia)
            tiene_membresia_activa = SuscripcionMembresia.objects.filter(
                cliente=cliente,
                estado='activa',
                fecha_inicio__lte=timezone.now().date(),
                fecha_fin__gte=timezone.now().date()
            ).exists()

            if not tiene_membresia_activa:
                raise serializers.ValidationError("El cliente no tiene una membresía activa")

            # Verificar cupo disponible
            if sesion_clase.esta_llena:
                raise serializers.ValidationError("La sesión ya está llena")

        return data


class ReservaClaseCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas de clase"""
    
    class Meta:
        model = ReservaClase
        fields = ['cliente', 'sesion_clase', 'observaciones']
    
    def validate(self, data):
        return ReservaClaseSerializer().validate(data)


class ReservaEquipoSerializer(serializers.ModelSerializer):
    cliente_detalle = ClienteBasicSerializer(source='cliente', read_only=True)
    activo_detalle = ActivoBasicSerializer(source='activo', read_only=True)
    duracion_programada = serializers.ReadOnlyField()
    
    class Meta:
        model = ReservaEquipo
        fields = [
            'id', 'cliente', 'activo', 'fecha_reserva', 'hora_inicio', 'hora_fin',
            'estado', 'fecha_creacion', 'observaciones', 'tiempo_uso_real',
            'cliente_detalle', 'activo_detalle', 'duracion_programada'
        ]
        read_only_fields = ['fecha_creacion']

    def validate(self, data):
        """Validaciones personalizadas"""
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        # Verificar disponibilidad del equipo
        activo = data.get('activo')
        if activo and activo.estado != 'activo':
            raise serializers.ValidationError(f"El equipo {activo.nombre} no está disponible")
        
        return data


class ReservaEquipoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas de equipo"""
    
    class Meta:
        model = ReservaEquipo
        fields = [
            'cliente', 'activo', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'observaciones'
        ]
    
    def validate(self, data):
        return ReservaEquipoSerializer().validate(data)


class ReservaEntrenadorSerializer(serializers.ModelSerializer):
    cliente_detalle = ClienteBasicSerializer(source='cliente', read_only=True)
    entrenador_detalle = EntrenadorBasicSerializer(source='entrenador', read_only=True)
    espacio_detalle = EspacioBasicSerializer(source='espacio', read_only=True)
    clientes_adicionales_detalle = ClienteBasicSerializer(source='clientes_adicionales', many=True, read_only=True)
    duracion = serializers.ReadOnlyField()
    total_clientes = serializers.ReadOnlyField()
    
    class Meta:
        model = ReservaEntrenador
        fields = [
            'id', 'cliente', 'entrenador', 'fecha_sesion', 'hora_inicio', 'hora_fin',
            'tipo_sesion', 'estado', 'objetivo', 'espacio', 'precio',
            'clientes_adicionales', 'fecha_creacion', 'observaciones', 'notas_entrenador',
            'cliente_detalle', 'entrenador_detalle', 'espacio_detalle',
            'clientes_adicionales_detalle', 'duracion', 'total_clientes'
        ]
        read_only_fields = ['fecha_creacion']

    def validate(self, data):
        """Validaciones personalizadas"""
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        # Verificar que el espacio esté en la misma sede del entrenador
        entrenador = data.get('entrenador')
        espacio = data.get('espacio')
        if entrenador and espacio and espacio.sede != entrenador.sede:
            raise serializers.ValidationError("El espacio debe estar en la misma sede del entrenador")
        
        return data


class ReservaEntrenadorCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas de entrenador"""
    
    class Meta:
        model = ReservaEntrenador
        fields = [
            'cliente', 'entrenador', 'fecha_sesion', 'hora_inicio', 'hora_fin',
            'tipo_sesion', 'objetivo', 'espacio', 'precio', 'clientes_adicionales',
            'observaciones'
        ]
    
    def validate(self, data):
        return ReservaEntrenadorSerializer().validate(data)


class DisponibilidadEquipoSerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad de equipos"""
    activo_id = serializers.IntegerField()
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField(required=False)
    hora_fin = serializers.TimeField(required=False)
    
    def validate(self, data):
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        return data


class EstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas de horarios"""
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    sede_id = serializers.IntegerField(required=False)
    tipo_actividad_id = serializers.IntegerField(required=False)
