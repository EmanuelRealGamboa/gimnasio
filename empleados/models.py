from django.db import models
from authentication.models import Persona
from instalaciones.models import Sede, Espacio


# Create your models here.

class Empleado(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, primary_key=True)
    puesto  = models.CharField(max_length=50)
    departamento  = models.CharField(max_length=50, blank=True)
    fecha_contratacion = models.DateField()
    tipo_contrato = models.CharField(max_length=50)      # enum en tu DB
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)       # 'Activo', 'Inactivo', etc.
    rfc  = models.CharField(max_length=13, blank=True)
    curp = models.CharField(max_length=18, blank=True)
    nss = models.CharField(max_length=11, blank=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True)

    # Documentos del empleado
    identificacion = models.FileField(upload_to='documentos/identificaciones/', null=True, blank=True)
    comprobante_domicilio = models.FileField(upload_to='documentos/comprobantes/', null=True, blank=True)
    certificados = models.FileField(upload_to='documentos/certificados/', null=True, blank=True)



class Entrenador(models.Model):
    empleado   = models.OneToOneField(Empleado, on_delete=models.CASCADE, primary_key=True)
    especialidad  = models.CharField(max_length=100)
    certificaciones = models.CharField(max_length=255, blank=True)
    turno = models.CharField(max_length=50)
    espacio = models.ManyToManyField(Espacio)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

class Cajero(models.Model):
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, primary_key=True)
    turno  = models.CharField(max_length=50)
    espacio = models.ManyToManyField(Espacio)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

class PersonalLimpieza(models.Model):
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, primary_key=True)
    turno  = models.CharField(max_length=50)
    espacio = models.ManyToManyField(Espacio)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

class SupervisorEspacio(models.Model):
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, primary_key=True)
    turno = models.CharField(max_length=50)
    espacio = models.ManyToManyField(Espacio)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)


# ============================================
# MODELOS PARA GESTIÓN DE LIMPIEZA
# ============================================

class TareaLimpieza(models.Model):
    """
    Catálogo de tareas de limpieza disponibles.
    Define qué tipo de tareas pueden asignarse al personal.
    """
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    TIPO_ESPACIO_CHOICES = [
        ('bano', 'Baño'),
        ('vestidor', 'Vestidor'),
        ('gimnasio', 'Gimnasio'),
        ('alberca', 'Alberca'),
        ('recepcion', 'Recepción'),
        ('oficina', 'Oficina'),
        ('estacionamiento', 'Estacionamiento'),
        ('areas_comunes', 'Áreas Comunes'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo_espacio = models.CharField(max_length=50, choices=TIPO_ESPACIO_CHOICES)
    duracion_estimada = models.IntegerField(help_text="Duración estimada en minutos")
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tarea de Limpieza'
        verbose_name_plural = 'Tareas de Limpieza'
        ordering = ['-prioridad', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_espacio_display()})"


class HorarioLimpieza(models.Model):
    """
    Plantillas de horarios recurrentes para el personal de limpieza.
    Define cuándo debe trabajar cada persona en qué espacio.
    """
    DIA_SEMANA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    personal_limpieza = models.ForeignKey(PersonalLimpieza, on_delete=models.CASCADE, related_name='horarios')
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=20, choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Horario de Limpieza'
        verbose_name_plural = 'Horarios de Limpieza'
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.personal_limpieza.empleado.persona.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class AsignacionTarea(models.Model):
    """
    Tareas específicas asignadas al personal de limpieza.
    Representa una tarea concreta a realizar en una fecha y hora determinada.

    Flujo:
    1. Administrador asigna tarea a empleado de limpieza (estado: pendiente)
    2. Se guarda automáticamente la hora_inicio al crear la asignación
    3. Empleado confirma desde app móvil que completó la tarea
    4. Se guarda automáticamente hora_fin cuando el empleado confirma
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    personal_limpieza = models.ForeignKey(PersonalLimpieza, on_delete=models.CASCADE, related_name='asignaciones')
    tarea = models.ForeignKey(TareaLimpieza, on_delete=models.CASCADE)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha = models.DateField(help_text="Fecha cuando se asignó la tarea")

    # Hora de asignación (se guarda automáticamente al crear)
    hora_inicio = models.TimeField(null=True, blank=True, help_text="Hora cuando se asignó la tarea (automático)")
    # Hora de finalización (se guarda cuando empleado confirma desde app móvil)
    hora_fin = models.TimeField(null=True, blank=True, help_text="Hora cuando empleado completó la tarea (automático)")

    # Estado de la tarea
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_completada = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora exacta de completado")
    completada_por = models.ForeignKey(
        PersonalLimpieza,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_completadas'
    )

    # Observaciones
    notas = models.TextField(blank=True, help_text="Notas del administrador al asignar la tarea")
    observaciones_completado = models.TextField(blank=True, help_text="Observaciones del empleado al completar (desde app móvil)")

    # Auditoría
    asignado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asignaciones_limpieza_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Timestamp exacto de cuando se creó la asignación")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación de Tarea'
        verbose_name_plural = 'Asignaciones de Tareas'
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.tarea.nombre} - {self.personal_limpieza.empleado.persona.nombre} - {self.fecha}"


class ChecklistLimpieza(models.Model):
    """
    Checklist de verificación para asegurar la calidad de las tareas de limpieza.
    """
    asignacion = models.OneToOneField(AsignacionTarea, on_delete=models.CASCADE, related_name='checklist')

    # Items del checklist (JSON)
    # Formato: [{"item": "Sanitarios limpios", "completado": true}, ...]
    items = models.JSONField(default=list, blank=True)

    # Verificación
    verificado = models.BooleanField(default=False)
    verificado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verificaciones_limpieza'
    )
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    # Calificación
    calificacion = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calificación de 1 a 5 estrellas"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Checklist de Limpieza'
        verbose_name_plural = 'Checklists de Limpieza'

    def __str__(self):
        return f"Checklist - {self.asignacion}"