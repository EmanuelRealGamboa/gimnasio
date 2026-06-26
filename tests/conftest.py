"""
conftest.py — Fixtures reutilizables para toda la suite de tests.

Fixtures disponibles:
- api_client            APIClient sin autenticar
- admin_user            Usuario con rol Administrador + token JWT en header
- cajero_user           Usuario con rol Cajero
- sede                  Sede base
- cliente               Cliente base en la sede
"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import (
    SedeFactory,
    ClienteFactory,
    make_admin_user,
    make_cajero_user,
)


@pytest.fixture
def api_client():
    """APIClient de DRF sin autenticar."""
    return APIClient()


@pytest.fixture
def sede(db):
    """Sede base compartida en la sesión de test."""
    return SedeFactory(nombre="Sede Central")


@pytest.fixture
def admin_user(db):
    """
    Usuario con rol Administrador.
    Devuelve el objeto User ya autenticado en un APIClient.
    Accede a: fixture.user, fixture.client (autenticado), fixture.rol
    """
    user, rol = make_admin_user(email="admin@test.com")
    client = APIClient()
    # Autenticar con JWT
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    class _Context:
        pass

    ctx = _Context()
    ctx.user = user
    ctx.client = client
    ctx.rol = rol
    return ctx


@pytest.fixture
def cajero_user(db, sede):
    """
    Usuario con rol Cajero asociado a la sede base.
    Devuelve (user, cajero_obj, autenticado_client).
    """
    user, cajero = make_cajero_user(sede=sede)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    class _Context:
        pass

    ctx = _Context()
    ctx.user = user
    ctx.cajero = cajero
    ctx.client = client
    return ctx


@pytest.fixture
def cliente(db, sede):
    """Cliente base en la sede central."""
    return ClienteFactory(sede=sede)
