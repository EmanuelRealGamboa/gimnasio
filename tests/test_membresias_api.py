"""
Tests adicionales de API de membresias para aumentar cobertura de views.

Cubre:
1. Listar membresías: 200, requiere auth
2. Filtrar membresías por tipo
3. Filtrar membresías activas (endpoint /activas/)
4. Crear membresía: solo Admin/Cajero
5. toggle_activo: activa/desactiva
6. Crear suscripción como Admin
7. Cancelar suscripción
8. Renovar suscripción
9. Listar suscripciones como Admin
10. Suscripción creada con membresía de otra sede es rechazada
"""
import decimal
import pytest
from datetime import timedelta
from django.utils import timezone

from membresias.models import Membresia, SuscripcionMembresia
from tests.factories import (
    SedeFactory,
    ClienteFactory,
    MembresiaFactory,
    MembresiaMultiSedeFactory,
    SuscripcionMembresiaFactory,
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
# 1 & 2. Listar y filtrar membresías
# =========================================================

class TestMembresiaListar:
    def test_listar_membresias_requiere_autenticacion(self, db):
        response = APIClient().get("/api/membresias/")
        assert response.status_code == 401

    def test_listar_membresias_como_admin_devuelve_200(self, db):
        MembresiaFactory.create_batch(3)
        user, _ = make_admin_user(email="memlist1@test.com")
        client = _auth_client(user)
        response = client.get("/api/membresias/")
        assert response.status_code == 200
        assert len(response.data) >= 3

    def test_filtrar_membresias_por_tipo(self, db):
        MembresiaFactory(tipo="mensual", nombre_plan="Plan Mensual Único")
        MembresiaFactory(tipo="anual", nombre_plan="Plan Anual Único")
        user, _ = make_admin_user(email="memlist2@test.com")
        client = _auth_client(user)
        response = client.get("/api/membresias/?tipo=mensual")
        assert response.status_code == 200
        for item in response.data:
            assert item["tipo"] == "mensual"

    def test_filtrar_membresias_activas(self, db):
        MembresiaFactory(activo=True, nombre_plan="Plan Activo Solo")
        MembresiaFactory(activo=False, nombre_plan="Plan Inactivo Solo")
        user, _ = make_admin_user(email="memlist3@test.com")
        client = _auth_client(user)
        response = client.get("/api/membresias/?activo=true")
        assert response.status_code == 200
        for item in response.data:
            assert item["activo"] is True

    def test_endpoint_activas_solo_devuelve_activas(self, db):
        MembresiaFactory(activo=True, nombre_plan="Activa Test")
        MembresiaFactory(activo=False, nombre_plan="Inactiva Test")
        user, _ = make_admin_user(email="memlist4@test.com")
        client = _auth_client(user)
        response = client.get("/api/membresias/activas/")
        assert response.status_code == 200
        for item in response.data:
            assert item["activo"] is True


# =========================================================
# 3. Crear membresía
# =========================================================

class TestMembresiaCrear:
    def _payload(self, sede):
        return {
            "nombre_plan": "Plan Nuevo Test API",
            "tipo": "mensual",
            "precio": "350.00",
            "duracion_dias": 30,
            "activo": True,
            "sede": sede.id,
            "permite_todas_sedes": False,
        }

    def test_crear_membresia_como_admin_devuelve_201(self, db):
        sede = SedeFactory()
        user, _ = make_admin_user(email="memcreate1@test.com")
        client = _auth_client(user)
        response = client.post("/api/membresias/", self._payload(sede), format="json")
        assert response.status_code == 201

    def test_crear_membresia_sin_autenticacion_devuelve_401(self, db):
        sede = SedeFactory()
        response = APIClient().post("/api/membresias/", self._payload(sede), format="json")
        assert response.status_code == 401

    def test_crear_membresia_como_cajero_devuelve_201(self, db):
        sede = SedeFactory()
        user, _ = make_cajero_user(sede=sede)
        client = _auth_client(user)
        payload = self._payload(sede)
        payload["nombre_plan"] = "Plan Cajero Test"
        response = client.post("/api/membresias/", payload, format="json")
        assert response.status_code == 201


# =========================================================
# 4. toggle_activo
# =========================================================

class TestMembresiaToggleActivo:
    def test_toggle_activo_desactiva_membresia_activa(self, db):
        membresia = MembresiaFactory(activo=True)
        user, _ = make_admin_user(email="toggle1@test.com")
        client = _auth_client(user)
        url = f"/api/membresias/{membresia.id}/toggle_activo/"
        response = client.post(url, format="json")
        assert response.status_code == 200
        membresia.refresh_from_db()
        assert membresia.activo is False

    def test_toggle_activo_activa_membresia_inactiva(self, db):
        membresia = MembresiaFactory(activo=False)
        user, _ = make_admin_user(email="toggle2@test.com")
        client = _auth_client(user)
        url = f"/api/membresias/{membresia.id}/toggle_activo/"
        response = client.post(url, format="json")
        assert response.status_code == 200
        membresia.refresh_from_db()
        assert membresia.activo is True


# =========================================================
# 5. Crear y listar suscripciones como Admin
# =========================================================

class TestSuscripcionCRUD:
    def test_listar_suscripciones_como_admin(self, db):
        SuscripcionMembresiaFactory.create_batch(2)
        user, _ = make_admin_user(email="suslist1@test.com")
        client = _auth_client(user)
        response = client.get("/api/suscripciones/")
        assert response.status_code == 200
        assert len(response.data) >= 2

    def test_cancelar_suscripcion(self, db):
        sede = SedeFactory()
        membresia = MembresiaFactory(sede=sede, duracion_dias=30)
        cliente = ClienteFactory(sede=sede)
        hoy = timezone.now().date()
        sus = SuscripcionMembresiaFactory(
            cliente=cliente,
            membresia=membresia,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado="activa",
        )
        user, _ = make_admin_user(email="suscancel1@test.com")
        client = _auth_client(user)
        response = client.post(f"/api/suscripciones/{sus.id}/cancelar/", format="json")
        assert response.status_code == 200
        sus.refresh_from_db()
        assert sus.estado == "cancelada"

    def test_cancelar_suscripcion_ya_cancelada_devuelve_400(self, db):
        sus = SuscripcionMembresiaFactory(estado="cancelada")
        user, _ = make_admin_user(email="suscancel2@test.com")
        client = _auth_client(user)
        response = client.post(f"/api/suscripciones/{sus.id}/cancelar/", format="json")
        assert response.status_code == 400

    def test_renovar_suscripcion(self, db):
        sede = SedeFactory()
        membresia = MembresiaFactory(sede=sede, duracion_dias=30)
        cliente = ClienteFactory(sede=sede)
        pasado = timezone.now().date() - timedelta(days=5)
        sus = SuscripcionMembresiaFactory(
            cliente=cliente,
            membresia=membresia,
            fecha_inicio=pasado - timedelta(days=30),
            fecha_fin=pasado,
            estado="vencida",
            sede_suscripcion=sede,
        )
        user, _ = make_admin_user(email="susrenov1@test.com")
        client = _auth_client(user)
        response = client.post(
            f"/api/suscripciones/{sus.id}/renovar/",
            {"metodo_pago": "efectivo"},
            format="json",
        )
        assert response.status_code == 201
        # Verificar que se creó una nueva suscripción
        assert SuscripcionMembresia.objects.filter(cliente=cliente).count() == 2

    def test_filtrar_suscripciones_por_estado(self, db):
        sede = SedeFactory()
        membresia = MembresiaFactory(sede=sede, duracion_dias=30)
        hoy = timezone.now().date()
        SuscripcionMembresiaFactory(
            membresia=membresia,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado="activa",
        )
        SuscripcionMembresiaFactory(
            membresia=membresia,
            fecha_inicio=hoy - timedelta(days=60),
            fecha_fin=hoy - timedelta(days=30),
            estado="vencida",
        )
        user, _ = make_admin_user(email="susfilter1@test.com")
        client = _auth_client(user)
        response = client.get("/api/suscripciones/?estado=activa")
        assert response.status_code == 200
        for item in response.data:
            assert item["estado"] == "activa"
