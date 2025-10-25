from django.db import models

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

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'
        ordering = ['tipo', 'precio']

    def __str__(self):
        return f"{self.nombre_plan} - {self.get_tipo_display()} (${self.precio})"
