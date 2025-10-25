from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from empleados.models import Entrenador
from instalaciones.models import Espacio, Sede
from datetime import datetime, time


class TipoActividad(models.Model):
    """
    Tipos de actividades que se pueden realizar (Yoga, CrossFit, Spinning, etc.)
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    duracion_default = models.DurationField(help_text="Duración por defecto en formato HH:MM:SS")
    color_hex = models.CharField(max_length=7, default="#3b82f6", help_text="Color para mostrar en calendario (#RRGGBB)")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Actividad"
        verbose_name_plural = "Tipos de Actividades"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Horario(models.Model):
    """
    Horario principal que define cuándo, dónde y quién imparte una actividad
    """
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    ESTADOS = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Relaciones principales
    entrenador = models.ForeignKey(
        Entrenador, 
        on_delete=models.CASCADE, 
        related_name='horarios',
        help_text="Entrenador asignado a este horario"
    )
    espacio = models.ForeignKey(
        Espacio, 
        on_delete=models.CASCADE, 
        related_name='horarios',
        help_text="Espacio donde se realizará la actividad"
    )
    tipo_actividad = models.ForeignKey(
        TipoActividad, 
        on_delete=models.CASCADE, 
        related_name='horarios',
        help_text="Tipo de actividad a realizar"
    )
    
    # Información temporal
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Fechas de vigencia
    fecha_inicio = models.DateField(
        help_text="Fecha desde la cual este horario está vigente"
    )
    fecha_fin = models.DateField(
        blank=True, 
        null=True,
        help_text="Fecha hasta la cual este horario está vigente (opcional)"
    )
    
    # Información adicional
    cupo_maximo = models.PositiveIntegerField(
        default=20,
        help_text="Número máximo de personas que pueden asistir"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia_semana', 'hora_inicio']
        # Evitar conflictos de horarios en el mismo espacio
        unique_together = ['espacio', 'dia_semana', 'hora_inicio', 'fecha_inicio']
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        if self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Validar que el entrenador esté asignado al espacio
        if self.entrenador and self.espacio:
            if not self.entrenador.espacio.filter(id=self.espacio.id).exists():
                raise ValidationError(
                    f"El entrenador {self.entrenador.empleado.persona.nombre} "
                    f"no está asignado al espacio {self.espacio.nombre}"
                )
        
        # Validar que el entrenador y el espacio estén en la misma sede
        if self.entrenador and self.espacio:
            if self.entrenador.sede != self.espacio.sede:
                raise ValidationError(
                    f"El entrenador y el espacio deben estar en la misma sede. "
                    f"Entrenador: {self.entrenador.sede.nombre}, "
                    f"Espacio: {self.espacio.sede.nombre}"
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return (f"{self.tipo_actividad.nombre} - {self.dia_semana.title()} "
                f"{self.hora_inicio.strftime('%H:%M')} - "
                f"{self.entrenador.empleado.persona.nombre} - {self.espacio.nombre}")
    
    @property
    def duracion(self):
        """Calcula la duración del horario"""
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        return fin - inicio
    
    @property
    def sede(self):
        """Retorna la sede del espacio"""
        return self.espacio.sede
    
    def esta_vigente(self, fecha=None):
        """Verifica si el horario está vigente en una fecha específica"""
        if fecha is None:
            fecha = timezone.now().date()
        
        if fecha < self.fecha_inicio:
            return False
        
        if self.fecha_fin and fecha > self.fecha_fin:
            return False
        
        return self.estado == 'activo'


class SesionClase(models.Model):
    """
    Instancia específica de una clase en una fecha determinada
    """
    ESTADOS_SESION = [
        ('programada', 'Programada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('suspendida', 'Suspendida'),
    ]
    
    horario = models.ForeignKey(
        Horario, 
        on_delete=models.CASCADE, 
        related_name='sesiones',
        help_text="Horario base del cual se genera esta sesión"
    )
    fecha = models.DateField(help_text="Fecha específica de la sesión")
    
    # Permitir override de datos del horario para casos especiales
    entrenador_override = models.ForeignKey(
        Entrenador,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='sesiones_sustitutas',
        help_text="Entrenador sustituto para esta sesión específica"
    )
    espacio_override = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='sesiones_override',
        help_text="Espacio alternativo para esta sesión específica"
    )
    hora_inicio_override = models.TimeField(
        blank=True,
        null=True,
        help_text="Hora de inicio alternativa para esta sesión"
    )
    hora_fin_override = models.TimeField(
        blank=True,
        null=True,
        help_text="Hora de fin alternativa para esta sesión"
    )
    cupo_override = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Cupo alternativo para esta sesión"
    )
    
    estado = models.CharField(max_length=20, choices=ESTADOS_SESION, default='programada')
    asistentes_registrados = models.PositiveIntegerField(default=0)
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sesión de Clase"
        verbose_name_plural = "Sesiones de Clases"
        ordering = ['fecha', 'horario__hora_inicio']
        unique_together = ['horario', 'fecha']
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.hora_inicio_override and self.hora_fin_override:
            if self.hora_inicio_override >= self.hora_fin_override:
                raise ValidationError("La hora de inicio override debe ser anterior a la hora de fin override")
        
        # Validar que la fecha corresponda al día de la semana del horario
        dias_mapping = {
            0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves',
            4: 'viernes', 5: 'sabado', 6: 'domingo'
        }
        dia_fecha = dias_mapping[self.fecha.weekday()]
        if dia_fecha != self.horario.dia_semana:
            raise ValidationError(
                f"La fecha {self.fecha} corresponde a {dia_fecha}, "
                f"pero el horario es para {self.horario.dia_semana}"
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def entrenador_efectivo(self):
        """Retorna el entrenador que impartirá la clase (original o sustituto)"""
        return self.entrenador_override or self.horario.entrenador
    
    @property
    def espacio_efectivo(self):
        """Retorna el espacio donde se impartirá la clase (original o alternativo)"""
        return self.espacio_override or self.horario.espacio
    
    @property
    def hora_inicio_efectiva(self):
        """Retorna la hora de inicio efectiva"""
        return self.hora_inicio_override or self.horario.hora_inicio
    
    @property
    def hora_fin_efectiva(self):
        """Retorna la hora de fin efectiva"""
        return self.hora_fin_override or self.horario.hora_fin
    
    @property
    def cupo_efectivo(self):
        """Retorna el cupo efectivo"""
        return self.cupo_override or self.horario.cupo_maximo
    
    @property
    def lugares_disponibles(self):
        """Calcula los lugares disponibles"""
        return max(0, self.cupo_efectivo - self.asistentes_registrados)
    
    @property
    def esta_llena(self):
        """Verifica si la sesión está llena"""
        return self.asistentes_registrados >= self.cupo_efectivo
    
    def __str__(self):
        entrenador = self.entrenador_efectivo.empleado.persona.nombre
        return (f"{self.horario.tipo_actividad.nombre} - {self.fecha} "
                f"{self.hora_inicio_efectiva.strftime('%H:%M')} - {entrenador}")


class BloqueoHorario(models.Model):
    """
    Permite bloquear horarios específicos por mantenimiento, eventos especiales, etc.
    """
    TIPOS_BLOQUEO = [
        ('mantenimiento', 'Mantenimiento'),
        ('evento_especial', 'Evento Especial'),
        ('vacaciones', 'Vacaciones del Entrenador'),
        ('reparacion', 'Reparación del Espacio'),
        ('otro', 'Otro'),
    ]
    
    # Puede bloquear por entrenador, espacio o ambos
    entrenador = models.ForeignKey(
        Entrenador,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='bloqueos',
        help_text="Entrenador bloqueado (opcional)"
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='bloqueos',
        help_text="Espacio bloqueado (opcional)"
    )
    
    tipo_bloqueo = models.CharField(max_length=20, choices=TIPOS_BLOQUEO)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Bloqueo de Horario"
        verbose_name_plural = "Bloqueos de Horarios"
        ordering = ['-fecha_inicio']
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if not self.entrenador and not self.espacio:
            raise ValidationError("Debe especificar al menos un entrenador o un espacio a bloquear")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.entrenador and self.espacio:
            return f"Bloqueo: {self.entrenador.empleado.persona.nombre} en {self.espacio.nombre} - {self.motivo}"
        elif self.entrenador:
            return f"Bloqueo: {self.entrenador.empleado.persona.nombre} - {self.motivo}"
        elif self.espacio:
            return f"Bloqueo: {self.espacio.nombre} - {self.motivo}"
        return f"Bloqueo: {self.motivo}"
    
    def afecta_horario(self, horario, fecha):
        """Verifica si este bloqueo afecta un horario específico en una fecha"""
        # Convertir fecha y horas del horario a datetime para comparar
        inicio_horario = datetime.combine(fecha, horario.hora_inicio)
        fin_horario = datetime.combine(fecha, horario.hora_fin)
        
        # Verificar si hay solapamiento temporal
        if fin_horario <= self.fecha_inicio or inicio_horario >= self.fecha_fin:
            return False
        
        # Verificar si afecta al entrenador o espacio
        if self.entrenador and self.entrenador == horario.entrenador:
            return True
        
        if self.espacio and self.espacio == horario.espacio:
            return True
        
        return False