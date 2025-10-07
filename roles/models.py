from django.db import models
from authentication.models import Persona

# Create your models here.

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

    
class Permiso(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos')
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name='roles')

    class Meta:
        unique_together = ('rol', 'permiso')

   



class PersonaRol(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='personas')

    class Meta:
        unique_together = ('persona', 'rol')

   