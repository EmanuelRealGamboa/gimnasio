from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Membresia(models.Model):
    """
    Modelo para gestionar los planes de membresía del gimnasio.
    Define los diferentes tipos de membresías disponibles para los clientes.
    """

    TIPO_CHOICES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
        ('pase_dia', 'Pase del Día'),
        ('pase_semana', 'Pase Semanal'),
    ]

    nombre_plan = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    # Campos adicionales útiles
    duracion_dias = models.IntegerField(
        help_text="Duración de la membresía en días",
        null=True,
        blank=True
    )
    beneficios = models.TextField(blank=True, null=True, help_text="Lista de beneficios incluidos")
    activo = models.BooleanField(default=True, help_text="Si la membresía está disponible para venta")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # NUEVOS CAMPOS: Relación con Sede y Espacios
    sede = models.ForeignKey(
        'instalaciones.Sede',
        on_delete=models.CASCADE,
        related_name='membresias',
        null=True,
        blank=True,
        help_text="Sede a la que pertenece esta membresía. Si es null, es multi-sede"
    )
    espacios_incluidos = models.ManyToManyField(
        'instalaciones.Espacio',
        related_name='membresias',
        blank=True,
        help_text="Espacios a los que da acceso esta membresía"
    )
    permite_todas_sedes = models.BooleanField(
        default=False,
        help_text="Si es True, da acceso a todas las sedes (plan premium/corporativo)"
    )

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'
        ordering = ['tipo', 'precio']

    def __str__(self):
        if self.permite_todas_sedes:
            return f"{self.nombre_plan} - {self.get_tipo_display()} - TODAS LAS SEDES (${self.precio})"
        elif self.sede:
            return f"{self.nombre_plan} - {self.get_tipo_display()} - {self.sede.nombre} (${self.precio})"
        return f"{self.nombre_plan} - {self.get_tipo_display()} (${self.precio})"

    def get_espacios_disponibles(self):
        """Retorna los espacios disponibles según la configuración de la membresía"""
        if self.permite_todas_sedes:
            from instalaciones.models import Espacio
            return Espacio.objects.all()
        elif self.sede:
            return self.espacios_incluidos.filter(sede=self.sede)
        return self.espacios_incluidos.all()


class SuscripcionMembresia(models.Model):
    """
    Modelo para gestionar las suscripciones de los clientes a las membresías.
    Registra el historial completo de suscripciones y su estado.
    """

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    membresia = models.ForeignKey(
        Membresia,
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa'
    )
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES
    )
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionales sobre la suscripción")

    # NUEVO CAMPO: Sede donde se realizó la suscripción
    sede_suscripcion = models.ForeignKey(
        'instalaciones.Sede',
        on_delete=models.CASCADE,
        related_name='suscripciones',
        null=True,
        blank=True,
        help_text="Sede donde se realizó la suscripción (se hereda de la membresía)"
    )

    class Meta:
        db_table = 'suscripcion_membresia'
        verbose_name = 'Suscripción de Membresía'
        verbose_name_plural = 'Suscripciones de Membresías'
        ordering = ['-fecha_suscripcion']

    def __str__(self):
        sede_info = f" - {self.sede_suscripcion.nombre}" if self.sede_suscripcion else ""
        return f"{self.cliente.persona.nombre} - {self.membresia.nombre_plan}{sede_info} ({self.estado})"

    def save(self, *args, **kwargs):
        # Si no tiene fecha_inicio, usar hoy
        if not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()

        # Si no tiene fecha_fin, calcular según duracion_dias
        if not self.fecha_fin and self.membresia.duracion_dias:
            self.fecha_fin = self.fecha_inicio + timedelta(days=self.membresia.duracion_dias)

        # Heredar sede de la membresía si no está establecida
        if not self.sede_suscripcion and self.membresia.sede:
            self.sede_suscripcion = self.membresia.sede

        # Actualizar estado según fecha actual
        if self.fecha_fin < timezone.now().date() and self.estado == 'activa':
            self.estado = 'vencida'

        super().save(*args, **kwargs)

    @property
    def dias_restantes(self):
        """Calcula los días restantes de la suscripción"""
        if self.estado != 'activa':
            return 0
        delta = self.fecha_fin - timezone.now().date()
        return max(0, delta.days)

    @property
    def esta_activa(self):
        """Verifica si la suscripción está activa y vigente"""
        return self.estado == 'activa' and self.fecha_fin >= timezone.now().date()

    def tiene_acceso_a_espacio(self, espacio):
        """
        Verifica si el cliente tiene acceso a un espacio específico
        Args:
            espacio: Objeto Espacio a verificar
        Returns:
            bool: True si tiene acceso, False en caso contrario
        """
        if not self.esta_activa:
            return False

        # Si la membresía permite todas las sedes, tiene acceso
        if self.membresia.permite_todas_sedes:
            return True

        # Si el espacio pertenece a la sede de la suscripción
        if self.sede_suscripcion and espacio.sede == self.sede_suscripcion:
            # Verificar si el espacio está incluido en la membresía
            return self.membresia.espacios_incluidos.filter(id=espacio.id).exists()

        return False

    def get_espacios_disponibles(self):
        """
        Retorna los espacios a los que tiene acceso esta suscripción
        Returns:
            QuerySet: Espacios disponibles
        """
        if self.membresia.permite_todas_sedes:
            from instalaciones.models import Espacio
            return Espacio.objects.all()
        elif self.sede_suscripcion:
            return self.membresia.espacios_incluidos.filter(sede=self.sede_suscripcion)
        return self.membresia.espacios_incluidos.all()

    def get_sedes_disponibles(self):
        """
        Retorna las sedes a las que tiene acceso esta suscripción
        Returns:
            QuerySet: Sedes disponibles
        """
        if self.membresia.permite_todas_sedes:
            from instalaciones.models import Sede
            return Sede.objects.all()
        elif self.sede_suscripcion:
            from instalaciones.models import Sede
            return Sede.objects.filter(id=self.sede_suscripcion.id)
        return None
