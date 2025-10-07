from django.contrib.auth.models import AbstractUser, PermissionsMixin , BaseUserManager
from django.db import models
from django.utils import timezone


# Create your models here.


#Tabla que almacena datos para todas las personas (clientes y empleados)
class Persona(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno  = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"


# Modelo para contacto de emergencia asociado a una persona
class ContactoEmergencia(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='contacto_emergencia', null=True, blank=True)
    nombre_contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono_contacto = models.CharField(max_length=10, blank=True, null=True)
    parentesco = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_contacto} - {self.telefono_contacto} ({self.parentesco})"
    
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
class User(AbstractUser, PermissionsMixin):
    username = None  # Eliminar el campo username heredado
    email = models.EmailField(unique=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, null=True, blank=True, related_name='usuario')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email