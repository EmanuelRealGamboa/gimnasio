from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from empleados.models import Entrenador
from instalaciones.models import Espacio, Sede
from clientes.models import Cliente
from gestion_equipos.models import Activo
from membresias.models import Membresia
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


class EquipoActividad(models.Model):
    """
    Define qué equipos/activos son necesarios para cada tipo de actividad
    """
    tipo_actividad = models.ForeignKey(
        TipoActividad, 
        on_delete=models.CASCADE, 
        related_name='equipos_necesarios'
    )
    activo = models.ForeignKey(
        Activo, 
        on_delete=models.CASCADE, 
        related_name='actividades_relacionadas'
    )
    cantidad_necesaria = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de este equipo necesaria para la actividad"
    )
    obligatorio = models.BooleanField(
        default=True,
        help_text="Si es obligatorio tener este equipo para realizar la actividad"
    )
    
    class Meta:
        verbose_name = "Equipo por Actividad"
        verbose_name_plural = "Equipos por Actividad"
        unique_together = ['tipo_actividad', 'activo']
    
    def __str__(self):
        return f"{self.tipo_actividad.nombre} - {self.activo.nombre} (x{self.cantidad_necesaria})"


class ClienteMembresia(models.Model):
    """
    Relación entre cliente y membresía activa
    """
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('suspendida', 'Suspendida'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='membresias'
    )
    membresia = models.ForeignKey(
        Membresia, 
        on_delete=models.CASCADE, 
        related_name='clientes_suscritos'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Membresía de Cliente"
        verbose_name_plural = "Membresías de Clientes"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.cliente.persona.nombre} - {self.membresia.nombre_plan} ({self.estado})"
    
    @property
    def esta_activa(self):
        """Verifica si la membresía está activa y vigente"""
        hoy = timezone.now().date()
        return (self.estado == 'activa' and 
                self.fecha_inicio <= hoy <= self.fecha_fin)
    
    @property
    def dias_restantes(self):
        """Calcula días restantes de la membresía"""
        if not self.esta_activa:
            return 0
        return (self.fecha_fin - timezone.now().date()).days


class ReservaClase(models.Model):
    """
    Reserva de un cliente para una sesión de clase específica
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('asistio', 'Asistió'),
        ('no_asistio', 'No Asistió'),
        ('no_show', 'No Show'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='reservas'
    )
    sesion_clase = models.ForeignKey(
        SesionClase, 
        on_delete=models.CASCADE, 
        related_name='reservas'
    )
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='confirmada')
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    motivo_cancelacion = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Reserva de Clase"
        verbose_name_plural = "Reservas de Clases"
        ordering = ['-fecha_reserva']
        unique_together = ['cliente', 'sesion_clase']  # Un cliente no puede reservar la misma sesión dos veces
    
    def clean(self):
        """Validaciones personalizadas"""
        # Verificar que el cliente tenga membresía activa
        if not self.cliente.membresias.filter(
            estado='activa',
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).exists():
            raise ValidationError("El cliente no tiene una membresía activa")
        
        # Verificar que la sesión no esté llena
        if self.sesion_clase.esta_llena and self.estado == 'confirmada':
            raise ValidationError("La sesión ya está llena")
        
        # Verificar que la sesión esté en el futuro
        fecha_sesion = self.sesion_clase.fecha
        if fecha_sesion < timezone.now().date():
            raise ValidationError("No se pueden hacer reservas para sesiones pasadas")
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Actualizar contador de asistentes en la sesión
        if self.pk:  # Si ya existe, verificar cambios de estado
            old_reserva = ReservaClase.objects.get(pk=self.pk)
            if old_reserva.estado != self.estado:
                self._actualizar_contador_sesion(old_reserva.estado, self.estado)
        else:  # Nueva reserva
            if self.estado == 'confirmada':
                self.sesion_clase.asistentes_registrados += 1
                self.sesion_clase.save()
        
        super().save(*args, **kwargs)
    
    def _actualizar_contador_sesion(self, estado_anterior, estado_nuevo):
        """Actualiza el contador de asistentes según el cambio de estado"""
        # Estados que cuentan como ocupando lugar
        estados_ocupan = ['confirmada', 'asistio']
        
        if estado_anterior in estados_ocupan and estado_nuevo not in estados_ocupan:
            # Liberar lugar
            self.sesion_clase.asistentes_registrados -= 1
        elif estado_anterior not in estados_ocupan and estado_nuevo in estados_ocupan:
            # Ocupar lugar
            self.sesion_clase.asistentes_registrados += 1
        
        self.sesion_clase.save()
    
    def cancelar(self, motivo=None):
        """Método para cancelar una reserva"""
        if self.estado in ['cancelada', 'asistio']:
            raise ValidationError("No se puede cancelar una reserva ya cancelada o completada")
        
        self.estado = 'cancelada'
        self.fecha_cancelacion = timezone.now()
        self.motivo_cancelacion = motivo
        self.save()
    
    def __str__(self):
        return (f"{self.cliente.persona.nombre} - "
                f"{self.sesion_clase.horario.tipo_actividad.nombre} - "
                f"{self.sesion_clase.fecha} ({self.estado})")


class ReservaEquipo(models.Model):
    """
    Reserva específica de equipos/máquinas por parte de los clientes
    """
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('en_uso', 'En Uso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_show', 'No Show'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='reservas_equipos'
    )
    activo = models.ForeignKey(
        Activo, 
        on_delete=models.CASCADE, 
        related_name='reservas'
    )
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    
    # Información adicional
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    tiempo_uso_real = models.DurationField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Reserva de Equipo"
        verbose_name_plural = "Reservas de Equipos"
        ordering = ['fecha_reserva', 'hora_inicio']
    
    def clean(self):
        """Validaciones personalizadas"""
        # Verificar que las horas sean válidas
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        # Verificar que el equipo esté disponible
        if self.activo.estado != 'activo':
            raise ValidationError(f"El equipo {self.activo.nombre} no está disponible")
        
        # Verificar que no haya conflictos de horario
        conflictos = ReservaEquipo.objects.filter(
            activo=self.activo,
            fecha_reserva=self.fecha_reserva,
            estado__in=['activa', 'en_uso']
        ).exclude(pk=self.pk if self.pk else None)
        
        for reserva in conflictos:
            if (self.hora_inicio < reserva.hora_fin and 
                self.hora_fin > reserva.hora_inicio):
                raise ValidationError(
                    f"Conflicto de horario con reserva existente "
                    f"({reserva.hora_inicio} - {reserva.hora_fin})"
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duracion_programada(self):
        """Calcula la duración programada de la reserva"""
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        return fin - inicio
    
    def iniciar_uso(self):
        """Marca el inicio del uso del equipo"""
        if self.estado != 'activa':
            raise ValidationError("Solo se puede iniciar el uso de reservas activas")
        self.estado = 'en_uso'
        self.save()
    
    def finalizar_uso(self, tiempo_real=None):
        """Marca el fin del uso del equipo"""
        if self.estado != 'en_uso':
            raise ValidationError("Solo se puede finalizar el uso de reservas en uso")
        self.estado = 'completada'
        if tiempo_real:
            self.tiempo_uso_real = tiempo_real
        self.save()
    
    def __str__(self):
        return (f"{self.cliente.persona.nombre} - {self.activo.nombre} - "
                f"{self.fecha_reserva} {self.hora_inicio}-{self.hora_fin}")


class ReservaEntrenador(models.Model):
    """
    Reserva de sesiones personalizadas con entrenadores
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente Aprobación'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_show', 'No Show'),
    ]
    
    TIPO_SESION_CHOICES = [
        ('individual', 'Sesión Individual'),
        ('pareja', 'Sesión en Pareja'),
        ('grupal_pequeno', 'Grupo Pequeño (3-5 personas)'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='sesiones_entrenador'
    )
    entrenador = models.ForeignKey(
        Entrenador, 
        on_delete=models.CASCADE, 
        related_name='sesiones_personalizadas'
    )
    fecha_sesion = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_sesion = models.CharField(max_length=20, choices=TIPO_SESION_CHOICES, default='individual')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Información de la sesión
    objetivo = models.TextField(help_text="Objetivo específico de la sesión")
    espacio = models.ForeignKey(
        Espacio, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Espacio donde se realizará la sesión"
    )
    precio = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Precio de la sesión personalizada"
    )
    
    # Clientes adicionales para sesiones grupales
    clientes_adicionales = models.ManyToManyField(
        Cliente,
        blank=True,
        related_name='sesiones_grupales',
        help_text="Clientes adicionales para sesiones en pareja o grupales"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    notas_entrenador = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Reserva de Entrenador"
        verbose_name_plural = "Reservas de Entrenadores"
        ordering = ['fecha_sesion', 'hora_inicio']
    
    def clean(self):
        """Validaciones personalizadas"""
        # Verificar horarios
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        # Verificar disponibilidad del entrenador
        conflictos = ReservaEntrenador.objects.filter(
            entrenador=self.entrenador,
            fecha_sesion=self.fecha_sesion,
            estado__in=['confirmada', 'en_curso']
        ).exclude(pk=self.pk if self.pk else None)
        
        for reserva in conflictos:
            if (self.hora_inicio < reserva.hora_fin and 
                self.hora_fin > reserva.hora_inicio):
                raise ValidationError(
                    f"El entrenador no está disponible en ese horario. "
                    f"Conflicto con sesión {reserva.hora_inicio}-{reserva.hora_fin}"
                )
        
        # Verificar que el espacio esté en la misma sede del entrenador
        if self.espacio and self.espacio.sede != self.entrenador.sede:
            raise ValidationError("El espacio debe estar en la misma sede del entrenador")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def aprobar(self):
        """Aprobar la sesión personalizada"""
        if self.estado != 'pendiente':
            raise ValidationError("Solo se pueden aprobar sesiones pendientes")
        self.estado = 'confirmada'
        self.save()
    
    def iniciar_sesion(self):
        """Iniciar la sesión"""
        if self.estado != 'confirmada':
            raise ValidationError("Solo se pueden iniciar sesiones confirmadas")
        self.estado = 'en_curso'
        self.save()
    
    def completar_sesion(self, notas=None):
        """Completar la sesión"""
        if self.estado != 'en_curso':
            raise ValidationError("Solo se pueden completar sesiones en curso")
        self.estado = 'completada'
        if notas:
            self.notas_entrenador = notas
        self.save()
    
    @property
    def duracion(self):
        """Calcula la duración de la sesión"""
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        return fin - inicio
    
    @property
    def total_clientes(self):
        """Número total de clientes en la sesión"""
        return 1 + self.clientes_adicionales.count()
    
    def __str__(self):
        return (f"{self.cliente.persona.nombre} con {self.entrenador.empleado.persona.nombre} - "
                f"{self.fecha_sesion} {self.hora_inicio}-{self.hora_fin} ({self.estado})")