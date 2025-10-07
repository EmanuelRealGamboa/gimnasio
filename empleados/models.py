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