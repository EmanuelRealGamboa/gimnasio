from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from instalaciones.models import Sede, Espacio
from empleados.models import Empleado
from authentication.models import User


class CategoriaActivo(models.Model):
    """
    Categorías para clasificar los activos del gimnasio.
    Ejemplos: Máquinas cardiovasculares, Máquinas de fuerza, Mobiliario, Sistemas electrónicos
    """
    categoria_activo_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'categoria_activo'
        verbose_name = 'Categoría de Activo'
        verbose_name_plural = 'Categorías de Activos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProveedorServicio(models.Model):
    """
    Proveedores externos de servicios de mantenimiento
    """
    proveedor_id = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=150)
    nombre_contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    servicios_ofrecidos = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción de los servicios que ofrece el proveedor'
    )
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'proveedor_servicio'
        verbose_name = 'Proveedor de Servicio'
        verbose_name_plural = 'Proveedores de Servicios'
        ordering = ['nombre_empresa']

    def __str__(self):
        return self.nombre_empresa


class Activo(models.Model):
    """
    Representa bienes físicos del gimnasio (máquinas, equipamiento, mobiliario)
    con información como código, nombre, categoría, fecha de compra, valor, estado y ubicación
    """
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('baja', 'Dado de Baja'),
        ('inactivo', 'Inactivo'),
    ]

    activo_id = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text='Código único del activo (ej: MAQ-001, MOB-015)'
    )
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        CategoriaActivo,
        on_delete=models.PROTECT,
        related_name='activos'
    )

    # Información de compra
    fecha_compra = models.DateField()
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Precio de compra del activo'
    )

    # Estado y ubicación
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Descripción específica de la ubicación dentro del espacio'
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name='activos'
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos',
        help_text='Espacio específico donde se encuentra el activo'
    )

    # Detalles técnicos
    descripcion = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True)
    imagen = models.ImageField(
        upload_to='activos/',
        blank=True,
        null=True,
        help_text='Imagen del activo'
    )

    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activos_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activo'
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['estado']),
            models.Index(fields=['sede']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def en_mantenimiento(self):
        """Verifica si el activo está actualmente en mantenimiento"""
        return self.mantenimientos.filter(
            estado__in=['pendiente', 'en_proceso']
        ).exists()


class Mantenimiento(models.Model):
    """
    Registra las tareas de mantenimiento (preventivo o correctivo) realizadas a un activo.
    Incluye fechas programadas y ejecutadas, proveedor, costo, descripción y estado.
    """
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    mantenimiento_id = models.AutoField(primary_key=True)
    activo = models.ForeignKey(
        Activo,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)

    # Fechas
    fecha_programada = models.DateField()
    fecha_ejecucion = models.DateField(null=True, blank=True)

    # Responsable del mantenimiento (interno o externo)
    proveedor_servicio = models.ForeignKey(
        ProveedorServicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos',
        help_text='Proveedor externo (si aplica)'
    )
    empleado_responsable = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_asignados',
        help_text='Empleado responsable del mantenimiento interno'
    )

    # Detalles
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    descripcion = models.TextField(help_text='Descripción del trabajo a realizar')
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones adicionales o hallazgos durante el mantenimiento'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mantenimiento'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_programada']
        indexes = [
            models.Index(fields=['activo', 'estado']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['tipo_mantenimiento']),
        ]

    def __str__(self):
        return f"{self.get_tipo_mantenimiento_display()} - {self.activo.nombre} ({self.fecha_programada})"

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError

        # Validar que la fecha de ejecución no sea menor a la programada
        if self.fecha_ejecucion and self.fecha_ejecucion < self.fecha_programada:
            raise ValidationError({
                'fecha_ejecucion': 'La fecha de ejecución no puede ser anterior a la fecha programada.'
            })

        # Validar que tenga al menos un responsable (proveedor o empleado)
        if not self.proveedor_servicio and not self.empleado_responsable:
            raise ValidationError(
                'Debe asignar un proveedor externo o un empleado responsable.'
            )

    def save(self, *args, **kwargs):
        """Override save para actualizar estado del activo automáticamente"""
        # Si el mantenimiento está en proceso, cambiar estado del activo
        if self.estado == 'en_proceso' and self.activo.estado != 'mantenimiento':
            self.activo.estado = 'mantenimiento'
            self.activo.save()

        # Si el mantenimiento se completó, volver el activo a estado activo
        if self.estado == 'completado' and self.activo.estado == 'mantenimiento':
            # Verificar que no haya otros mantenimientos en proceso
            query = Mantenimiento.objects.filter(
                activo=self.activo,
                estado__in=['pendiente', 'en_proceso']
            )
            # Excluir el actual si ya existe en la BD
            if self.pk:
                query = query.exclude(pk=self.pk)

            otros_en_proceso = query.exists()

            if not otros_en_proceso:
                self.activo.estado = 'activo'
                self.activo.save()

        super().save(*args, **kwargs)

    @property
    def dias_para_mantenimiento(self):
        """Calcula cuántos días faltan para el mantenimiento programado"""
        if self.estado in ['completado', 'cancelado']:
            return None
        delta = self.fecha_programada - timezone.now().date()
        return delta.days

    @property
    def requiere_atencion(self):
        """Indica si el mantenimiento requiere atención urgente (próximos 15 días)"""
        dias = self.dias_para_mantenimiento
        return dias is not None and 0 <= dias <= 15


class OrdenMantenimiento(models.Model):
    """
    Orden de trabajo para un mantenimiento específico.
    Incluye número de orden, prioridad, tiempo estimado y materiales necesarios.
    """
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    ESTADO_ORDEN_CHOICES = [
        ('creada', 'Creada'),
        ('aprobada', 'Aprobada'),
        ('en_ejecucion', 'En Ejecución'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    orden_id = models.AutoField(primary_key=True)
    mantenimiento = models.OneToOneField(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='orden'
    )
    numero_orden = models.CharField(
        max_length=20,
        unique=True,
        help_text='Número único de orden (ej: OM-2025-001)'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    tiempo_estimado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Tiempo estimado en horas',
        null=True,
        blank=True
    )
    materiales_necesarios = models.TextField(
        blank=True,
        null=True,
        help_text='Lista de materiales o repuestos necesarios'
    )
    estado_orden = models.CharField(
        max_length=20,
        choices=ESTADO_ORDEN_CHOICES,
        default='creada'
    )

    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes_creadas'
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orden_mantenimiento'
        verbose_name = 'Orden de Mantenimiento'
        verbose_name_plural = 'Órdenes de Mantenimiento'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.numero_orden} - {self.mantenimiento.activo.nombre}"

    def save(self, *args, **kwargs):
        """Generar número de orden automáticamente si no existe"""
        if not self.numero_orden:
            # Obtener el año actual
            año_actual = timezone.now().year
            # Contar órdenes del año actual
            count = OrdenMantenimiento.objects.filter(
                numero_orden__startswith=f'OM-{año_actual}'
            ).count() + 1
            # Generar número de orden
            self.numero_orden = f'OM-{año_actual}-{count:04d}'

        super().save(*args, **kwargs)
