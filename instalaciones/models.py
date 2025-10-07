from django.db import models

# Create your models here.

class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Espacio(models.Model):
    nombre     = models.CharField(max_length=100)
    descripcion= models.CharField(max_length=255, blank=True)
    capacidad  = models.IntegerField()
    sede       = models.ForeignKey(Sede, on_delete=models.CASCADE)
    imagen     = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"