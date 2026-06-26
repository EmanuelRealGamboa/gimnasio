"""
Tests de la app control_acceso.

Cubre:
1. RegistroAcceso.tiempo_permanencia — con y sin salida
2. Credencial — modelo y estados
3. Endpoint registrar_acceso: cliente sin membresía → acceso denegado
4. Endpoint registrar_acceso: cliente con membresía activa y misma sede → autorizado
5. Endpoint registrar_acceso: cliente con membresía activa pero otra sede → denegado
6. Endpoint registrar_acceso: cliente con membresía multi-sede → autorizado en cualquier sede
7. Endpoint registrar_acceso: requiere autenticación (401)
8. Endpoint registrar_acceso: sede no encontrada → 404
9. Endpoint validar_acceso: búsqueda por nombre
"""
import decimal
import pytest
from datetime import timedelta
from django.utils import timezone

from control_acceso.models import RegistroAcceso, Credencial
from membresias.models import SuscripcionMembresia
from tests.factories import (
    SedeFactory,
    ClienteFactory,
    RegistroAccesoFactory,
    CredencialFactory,
    PersonaFactory,
    SuscripcionMembresiaFactory,
    MembresiaFactory,
    MembresiaMultiSedeFactory,
    make_admin_user,
    make_cajero_user,
)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def _auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# =========================================================
# 1. RegistroAcceso.tiempo_permanencia
# =========================================================

class TestRegistroAccesoTiempoPermanencia:
    def test_tiempo_permanencia_calcula_minutos_correctamente(self, db):
        # Arrange
        entrada = timezone.now()
        salida = entrada + timedelta(hours=1, minutes=30)
        registro = RegistroAccesoFactory(
            fecha_hora_entrada=entrada,
            fecha_hora_salida=salida,
        )
        # Assert
        assert registro.tiempo_permanencia == 90  # 90 minutos

    def test_tiempo_permanencia_es_none_sin_salida(self, db):
        registro = RegistroAccesoFactory(fecha_hora_salida=None)
        assert registro.tiempo_permanencia is None

    def test_tiempo_permanencia_con_sesion_exacta_de_una_hora(self, db):
        entrada = timezone.now()
        salida = entrada + timedelta(hours=1)
        registro = RegistroAccesoFactory(fecha_hora_entrada=entrada, fecha_hora_salida=salida)
        assert registro.tiempo_permanencia == 60


# =========================================================
# 2. Credencial — modelo
# =========================================================

class TestCredencial:
    def test_crear_credencial_activa(self, db):
        persona = PersonaFactory()
        cred = Credencial.objects.create(
            persona=persona,
            tipo_credencial="Tarjeta",
            identificador="CARD-001",
            estado="activa",
        )
        assert cred.pk is not None
        assert cred.estado == "activa"

    def test_credencial_identificador_unico(self, db):
        from django.db import IntegrityError
        persona = PersonaFactory()
        Credencial.objects.create(
            persona=persona,
            tipo_credencial="QR",
            identificador="UNIQUE-001",
            estado="activa",
        )
        with pytest.raises(IntegrityError):
            Credencial.objects.create(
                persona=persona,
                tipo_credencial="QR",
                identificador="UNIQUE-001",  # duplicado
                estado="activa",
            )

    def test_str_credencial(self, db):
        persona = PersonaFactory(nombre="Juan", apellido_paterno="Perez")
        cred = CredencialFactory(persona=persona, identificador="ABC123")
        assert "ABC123" in str(cred)


# =========================================================
# 3–6. Endpoint registrar_acceso
# =========================================================

REGISTRAR_URL = "/api/accesos/registros/registrar_acceso/"


class TestRegistrarAcceso:
    def _payload(self, cliente, sede):
        return {"cliente_id": cliente.persona_id, "sede_id": sede.id}

    def test_cliente_sin_membresia_acceso_denegado(self, db):
        # Arrange
        sede = SedeFactory()
        cliente = ClienteFactory(sede=sede)
        user, _ = make_admin_user(email="acc1@test.com")
        client = _auth_client(user)
        # Act
        response = client.post(REGISTRAR_URL, self._payload(cliente, sede), format="json")
        # Assert
        assert response.status_code == 201
        registro = RegistroAcceso.objects.get(cliente=cliente)
        assert registro.autorizado is False
        assert "membresía" in registro.motivo_denegado.lower()

    def test_cliente_con_membresia_activa_misma_sede_autorizado(self, db):
        # Arrange
        sede = SedeFactory()
        membresia = MembresiaFactory(sede=sede, duracion_dias=30)
        cliente = ClienteFactory(sede=sede)
        hoy = timezone.now().date()
        SuscripcionMembresiaFactory(
            cliente=cliente,
            membresia=membresia,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado="activa",
            sede_suscripcion=sede,
        )
        user, _ = make_admin_user(email="acc2@test.com")
        client = _auth_client(user)
        # Act
        response = client.post(REGISTRAR_URL, self._payload(cliente, sede), format="json")
        # Assert
        assert response.status_code == 201
        registro = RegistroAcceso.objects.get(cliente=cliente)
        assert registro.autorizado is True

    def test_cliente_con_membresia_sede_diferente_denegado(self, db):
        # Arrange
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        membresia = MembresiaFactory(sede=sede_a, duracion_dias=30)
        cliente = ClienteFactory(sede=sede_a)
        hoy = timezone.now().date()
        SuscripcionMembresiaFactory(
            cliente=cliente,
            membresia=membresia,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado="activa",
            sede_suscripcion=sede_a,
        )
        user, _ = make_admin_user(email="acc3@test.com")
        client = _auth_client(user)
        # Act — intenta entrar a sede_b con membresía de sede_a
        payload = {"cliente_id": cliente.persona_id, "sede_id": sede_b.id}
        response = client.post(REGISTRAR_URL, payload, format="json")
        # Assert
        assert response.status_code == 201
        registro = RegistroAcceso.objects.get(cliente=cliente)
        assert registro.autorizado is False

    def test_cliente_con_membresia_multisede_autorizado_en_cualquier_sede(self, db):
        # Arrange
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        membresia = MembresiaMultiSedeFactory()
        cliente = ClienteFactory(sede=sede_a)
        hoy = timezone.now().date()
        SuscripcionMembresiaFactory(
            cliente=cliente,
            membresia=membresia,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=365),
            estado="activa",
            sede_suscripcion=None,
        )
        user, _ = make_admin_user(email="acc4@test.com")
        client = _auth_client(user)
        # Act — entra a sede_b (diferente de la del cliente)
        payload = {"cliente_id": cliente.persona_id, "sede_id": sede_b.id}
        response = client.post(REGISTRAR_URL, payload, format="json")
        # Assert
        assert response.status_code == 201
        registro = RegistroAcceso.objects.filter(cliente=cliente).first()
        assert registro.autorizado is True

    def test_registrar_acceso_requiere_autenticacion(self, db):
        sede = SedeFactory()
        cliente = ClienteFactory(sede=sede)
        response = APIClient().post(REGISTRAR_URL, {"cliente_id": cliente.persona_id, "sede_id": sede.id})
        assert response.status_code == 401

    def test_registrar_acceso_sede_inexistente_devuelve_404(self, db):
        sede = SedeFactory()
        cliente = ClienteFactory(sede=sede)
        user, _ = make_admin_user(email="acc5@test.com")
        client = _auth_client(user)
        response = client.post(
            REGISTRAR_URL,
            {"cliente_id": cliente.persona_id, "sede_id": 99999},
            format="json",
        )
        assert response.status_code == 404

    def test_registrar_acceso_cliente_inexistente_devuelve_404(self, db):
        sede = SedeFactory()
        user, _ = make_admin_user(email="acc6@test.com")
        client = _auth_client(user)
        response = client.post(
            REGISTRAR_URL,
            {"cliente_id": 99999, "sede_id": sede.id},
            format="json",
        )
        assert response.status_code == 404

    def test_registrar_acceso_con_cajero_autorizado(self, db):
        """Los cajeros también pueden registrar accesos."""
        sede = SedeFactory()
        cliente = ClienteFactory(sede=sede)
        user, cajero = make_cajero_user(sede=sede)
        client = _auth_client(user)
        response = client.post(REGISTRAR_URL, self._payload(cliente, sede), format="json")
        # Debe crear el registro (aunque el acceso pueda ser denegado por falta de membresía)
        assert response.status_code == 201


# =========================================================
# 7. Endpoint validar_acceso
# =========================================================

VALIDAR_URL = "/api/accesos/registros/validar_acceso/"


class TestValidarAcceso:
    def test_validar_acceso_por_nombre_encuentra_cliente(self, db):
        # Arrange
        sede = SedeFactory()
        persona = PersonaFactory(nombre="Carlos", apellido_paterno="Mendez")
        cliente = ClienteFactory(persona=persona, sede=sede)
        user, _ = make_admin_user(email="val1@test.com")
        client = _auth_client(user)
        # Act
        response = client.post(
            VALIDAR_URL,
            {"search_term": "Carlos", "sede_id": sede.id},
            format="json",
        )
        # Assert
        assert response.status_code == 200
        assert response.data["encontrado"] is True

    def test_validar_acceso_sin_autenticacion_devuelve_401(self, db):
        sede = SedeFactory()
        response = APIClient().post(
            VALIDAR_URL,
            {"search_term": "test", "sede_id": sede.id},
            format="json",
        )
        assert response.status_code == 401

    def test_validar_acceso_cliente_no_encontrado(self, db):
        sede = SedeFactory()
        user, _ = make_admin_user(email="val2@test.com")
        client = _auth_client(user)
        response = client.post(
            VALIDAR_URL,
            {"search_term": "NombreQueNoExiste999", "sede_id": sede.id},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["encontrado"] is False
