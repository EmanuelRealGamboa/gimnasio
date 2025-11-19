from django.db import models
from django.utils import timezone
from authentication.models import Persona
from instalaciones.models import Sede
from clientes.models import Cliente
# Create your models here.


class Credencial(models.Model):
    """
    Modelo para gestionar credenciales físicas o digitales de acceso.
    Útil para implementaciones futuras con tarjetas RFID, QR codes, etc.
    """
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='credenciales')
    tipo_credencial = models.CharField(max_length=20)  # 'Tarjeta', 'RFID', 'QR', 'Móvil'
    identificador = models.CharField(max_length=100, unique=True)
    fecha_emision = models.DateField(default=timezone.now)
    fecha_expiracion = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activa', 'Activa'),
            ('revocada', 'Revocada'),
            ('expirada', 'Expirada'),
            ('suspendida', 'Suspendida')
        ],
        default='activa'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Credencial'
        verbose_name_plural = 'Credenciales'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.persona} - {self.tipo_credencial} ({self.identificador})"


class RegistroAcceso(models.Model):
    """
    Modelo para registrar cada acceso de un cliente al gimnasio.
    Valida membresía activa y registra entrada/salida.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='accesos', null=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='accesos', null=True)
    fecha_hora_entrada = models.DateTimeField(default=timezone.now)
    fecha_hora_salida = models.DateTimeField(null=True, blank=True)

    autorizado = models.BooleanField(default=False)
    motivo_denegado = models.CharField(max_length=255, blank=True, null=True)

    # Información de la membresía al momento del acceso
    membresia_nombre = models.CharField(max_length=200, blank=True, null=True)
    membresia_estado = models.CharField(max_length=50, blank=True, null=True)

    # Información adicional
    notas = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accesos_registrados'
    )

    class Meta:
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Accesos'
        ordering = ['-fecha_hora_entrada']
        indexes = [
            models.Index(fields=['cliente', 'fecha_hora_entrada']),
            models.Index(fields=['sede', 'fecha_hora_entrada']),
            models.Index(fields=['autorizado', 'fecha_hora_entrada']),
        ]

    def __str__(self):
        estado = "✓ Autorizado" if self.autorizado else "✗ Denegado"
        return f"{self.cliente.persona.nombre} - {self.fecha_hora_entrada.strftime('%d/%m/%Y %H:%M')} - {estado}"

    @property
    def tiempo_permanencia(self):
        """Calcula el tiempo de permanencia en minutos"""
        if self.fecha_hora_salida:
            delta = self.fecha_hora_salida - self.fecha_hora_entrada
            return int(delta.total_seconds() / 60)
        return None
