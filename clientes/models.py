from django.db import models
from authentication.models import Persona

# Create your models here.

class Cliente(models.Model):
    """
    Modelo para gestionar los clientes del gimnasio.
    Hereda la información de Persona y añade campos específicos de clientes.
    """
    NIVEL_EXPERIENCIA_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    persona = models.OneToOneField(
        Persona,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cliente'
    )
    objetivo_fitness = models.CharField(max_length=255, blank=True, null=True)
    nivel_experiencia = models.CharField(
        max_length=20,
        choices=NIVEL_EXPERIENCIA_CHOICES,
        default='principiante'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo'
    )
    fecha_registro = models.DateField(auto_now_add=True)

    # Nota: ContactoEmergencia ya está relacionado con Persona mediante OneToOne
    # No necesitamos duplicar los campos de contacto de emergencia aquí

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido_paterno} - {self.estado}"
