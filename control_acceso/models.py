from django.db import models
from authentication.models import Persona
from instalaciones.models import Espacio
# Create your models here.


class Credencial(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tipo_credencial = models.CharField(max_length=20)  # 'Tarjeta', 'RFID', 'QR', 'Móvil'
    identificador = models.CharField(max_length=100, unique=True)
    fecha_emision = models.DateField()
    fecha_expiracion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20)   # 'Activa', 'Revocada', 'Expirada'

class RegistroAcceso(models.Model):
    credencial  = models.ForeignKey(Credencial, on_delete=models.CASCADE)
    espacio  = models.ForeignKey(Espacio, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField()
    autorizado = models.BooleanField()
    motivo_denegado = models.CharField(max_length=255, blank=True)
