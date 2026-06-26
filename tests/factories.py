"""
Factories de factory_boy para el proyecto gimnasio.

Cubren la cadena completa de objetos:
Persona → User / Cliente / Empleado → Sede → Membresia →
SuscripcionMembresia → Factura → Pago → VentaProducto → RegistroAcceso
"""
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import date, timedelta
import decimal

from authentication.models import Persona, User
from clientes.models import Cliente
from empleados.models import Empleado, Cajero, Entrenador
from instalaciones.models import Sede, Espacio
from membresias.models import Membresia, SuscripcionMembresia
from inventario.models import CategoriaProducto, Producto, Inventario
from facturacion.models import Factura, DetalleFactura, Pago, EstadoPago, MetodoPago
from ventas.models import VentaProducto, DetalleVentaProducto
from control_acceso.models import RegistroAcceso, Credencial
from roles.models import Rol, Permiso, RolPermiso, PersonaRol


# =====================================================================
# INFRAESTRUCTURA / INSTALACIONES
# =====================================================================

class SedeFactory(DjangoModelFactory):
    class Meta:
        model = Sede

    nombre = factory.Sequence(lambda n: f"Sede {n}")
    direccion = factory.Sequence(lambda n: f"Calle {n} #100")
    telefono = factory.Sequence(lambda n: f"555{n:07d}")


class EspacioFactory(DjangoModelFactory):
    class Meta:
        model = Espacio

    nombre = factory.Sequence(lambda n: f"Espacio {n}")
    descripcion = "Espacio de prueba"
    capacidad = 20
    sede = factory.SubFactory(SedeFactory)


# =====================================================================
# PERSONAS Y USUARIOS
# =====================================================================

class PersonaFactory(DjangoModelFactory):
    class Meta:
        model = Persona

    nombre = factory.Sequence(lambda n: f"Nombre{n}")
    apellido_paterno = factory.Sequence(lambda n: f"Apellido{n}")
    apellido_materno = "Test"
    fecha_nacimiento = date(1990, 1, 15)
    sexo = "Masculino"
    direccion = "Calle de prueba 123"
    telefono = factory.Sequence(lambda n: f"555{n:07d}")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    persona = factory.SubFactory(PersonaFactory)
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault("password", "testpass123")
        return model_class.objects.create_user(*args, **kwargs)


# =====================================================================
# ROLES Y PERMISOS
# =====================================================================

class RolFactory(DjangoModelFactory):
    class Meta:
        model = Rol
        django_get_or_create = ("nombre",)

    nombre = factory.Sequence(lambda n: f"Rol{n}")
    descripcion = "Rol de prueba"


class PermisoFactory(DjangoModelFactory):
    class Meta:
        model = Permiso
        django_get_or_create = ("nombre",)

    nombre = factory.Sequence(lambda n: f"permiso_{n}")
    descripcion = "Permiso de prueba"


class PersonaRolFactory(DjangoModelFactory):
    class Meta:
        model = PersonaRol
        django_get_or_create = ("persona", "rol")

    persona = factory.SubFactory(PersonaFactory)
    rol = factory.SubFactory(RolFactory)


# =====================================================================
# CLIENTES
# =====================================================================

class ClienteFactory(DjangoModelFactory):
    class Meta:
        model = Cliente

    persona = factory.SubFactory(PersonaFactory)
    sede = factory.SubFactory(SedeFactory)
    objetivo_fitness = "Perder peso"
    nivel_experiencia = "principiante"
    estado = "activo"


# =====================================================================
# EMPLEADOS
# =====================================================================

class EmpleadoFactory(DjangoModelFactory):
    class Meta:
        model = Empleado

    persona = factory.SubFactory(PersonaFactory)
    puesto = "Recepcionista"
    departamento = "Administración"
    fecha_contratacion = date(2023, 1, 1)
    tipo_contrato = "Indefinido"
    salario = decimal.Decimal("12000.00")
    estado = "Activo"
    rfc = factory.Sequence(lambda n: f"RFC{n:010d}")
    sede = factory.SubFactory(SedeFactory)


class CajeroFactory(DjangoModelFactory):
    class Meta:
        model = Cajero

    empleado = factory.SubFactory(EmpleadoFactory)
    turno = "Matutino"
    sede = factory.LazyAttribute(lambda o: o.empleado.sede)


# =====================================================================
# MEMBRESIAS
# =====================================================================

class MembresiaFactory(DjangoModelFactory):
    class Meta:
        model = Membresia

    nombre_plan = factory.Sequence(lambda n: f"Plan Básico {n}")
    tipo = "mensual"
    precio = decimal.Decimal("500.00")
    descripcion = "Membresía mensual básica"
    duracion_dias = 30
    activo = True
    sede = factory.SubFactory(SedeFactory)
    permite_todas_sedes = False


class MembresiaMultiSedeFactory(DjangoModelFactory):
    class Meta:
        model = Membresia

    nombre_plan = factory.Sequence(lambda n: f"Plan Premium {n}")
    tipo = "anual"
    precio = decimal.Decimal("4800.00")
    descripcion = "Membresía anual multisede"
    duracion_dias = 365
    activo = True
    sede = None
    permite_todas_sedes = True


class SuscripcionMembresiaFactory(DjangoModelFactory):
    class Meta:
        model = SuscripcionMembresia

    cliente = factory.SubFactory(ClienteFactory)
    membresia = factory.SubFactory(MembresiaFactory)
    fecha_inicio = factory.LazyFunction(lambda: timezone.now().date())
    fecha_fin = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=30))
    estado = "activa"
    precio_pagado = decimal.Decimal("500.00")
    metodo_pago = "efectivo"
    sede_suscripcion = factory.LazyAttribute(lambda o: o.membresia.sede)


# =====================================================================
# INVENTARIO Y PRODUCTOS
# =====================================================================

class CategoriaProductoFactory(DjangoModelFactory):
    class Meta:
        model = CategoriaProducto

    nombre = factory.Sequence(lambda n: f"Categoría {n}")


class ProductoFactory(DjangoModelFactory):
    class Meta:
        model = Producto

    # Dejamos codigo vacío para que el modelo genere uno automáticamente
    codigo = ""
    nombre = factory.Sequence(lambda n: f"Producto {n}")
    categoria = factory.SubFactory(CategoriaProductoFactory)
    precio_unitario = decimal.Decimal("100.00")
    descripcion = "Producto de prueba"
    activo = True


class InventarioFactory(DjangoModelFactory):
    class Meta:
        model = Inventario

    producto = factory.SubFactory(ProductoFactory)
    sede = factory.SubFactory(SedeFactory)
    cantidad_actual = 50
    cantidad_minima = 5
    cantidad_maxima = 200


# =====================================================================
# FACTURACION
# =====================================================================

class FacturaFactory(DjangoModelFactory):
    class Meta:
        model = Factura

    cliente = factory.SubFactory(ClienteFactory)
    total = decimal.Decimal("0.00")
    estado_pago = EstadoPago.PENDIENTE


class DetalleFacturaFactory(DjangoModelFactory):
    class Meta:
        model = DetalleFactura

    factura = factory.SubFactory(FacturaFactory)
    producto = factory.SubFactory(ProductoFactory)
    cantidad = 2
    precio_unitario = decimal.Decimal("100.00")


class PagoFactory(DjangoModelFactory):
    class Meta:
        model = Pago

    factura = factory.SubFactory(FacturaFactory)
    monto = decimal.Decimal("200.00")
    metodo_pago = MetodoPago.EFECTIVO


# =====================================================================
# VENTAS
# =====================================================================

class VentaProductoFactory(DjangoModelFactory):
    class Meta:
        model = VentaProducto

    cliente = factory.SubFactory(ClienteFactory)
    empleado = factory.SubFactory(UserFactory)
    sede = factory.SubFactory(SedeFactory)
    subtotal = decimal.Decimal("200.00")
    descuento_global = decimal.Decimal("0.00")
    iva = decimal.Decimal("0.00")
    total = decimal.Decimal("200.00")
    metodo_pago = "efectivo"
    estado = "completada"


class DetalleVentaProductoFactory(DjangoModelFactory):
    class Meta:
        model = DetalleVentaProducto

    venta = factory.SubFactory(VentaProductoFactory)
    producto = factory.SubFactory(ProductoFactory)
    cantidad = 2
    precio_unitario = decimal.Decimal("100.00")
    descuento = decimal.Decimal("0.00")
    subtotal = decimal.Decimal("200.00")
    total = decimal.Decimal("200.00")


# =====================================================================
# CONTROL DE ACCESO
# =====================================================================

class RegistroAccesoFactory(DjangoModelFactory):
    class Meta:
        model = RegistroAcceso

    cliente = factory.SubFactory(ClienteFactory)
    sede = factory.SubFactory(SedeFactory)
    fecha_hora_entrada = factory.LazyFunction(timezone.now)
    autorizado = True


class CredencialFactory(DjangoModelFactory):
    class Meta:
        model = Credencial

    persona = factory.SubFactory(PersonaFactory)
    tipo_credencial = "Tarjeta"
    identificador = factory.Sequence(lambda n: f"CRED-{n:06d}")
    estado = "activa"


# =====================================================================
# HELPERS DE COMPOSICIÓN
# =====================================================================

def make_admin_user(nombre="Admin", email=None):
    """
    Crea usuario con rol Administrador, incluyendo Persona asociada.
    Devuelve (user, rol_admin).
    """
    rol_admin, _ = Rol.objects.get_or_create(
        nombre="Administrador",
        defaults={"descripcion": "Rol administrador"}
    )
    persona = PersonaFactory(nombre=nombre)
    kwargs = {"persona": persona}
    if email:
        kwargs["email"] = email
    user = UserFactory(**kwargs)
    PersonaRolFactory(persona=persona, rol=rol_admin)
    return user, rol_admin


def make_cajero_user(sede=None):
    """
    Crea usuario con rol Cajero con Empleado y Cajero asociado.
    Devuelve (user, cajero_obj).
    """
    rol_cajero, _ = Rol.objects.get_or_create(
        nombre="Cajero",
        defaults={"descripcion": "Rol cajero"}
    )
    if sede is None:
        sede = SedeFactory()
    persona = PersonaFactory()
    user = UserFactory(persona=persona)
    empleado = EmpleadoFactory(persona=persona, sede=sede)
    cajero = CajeroFactory(empleado=empleado, sede=sede)
    PersonaRolFactory(persona=persona, rol=rol_cajero)
    return user, cajero
