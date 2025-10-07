from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from authentication.models import User, Persona
from empleados.models import Empleado
from roles.models import Rol, Permiso, RolPermiso, PersonaRol
from datetime import date


class EmpleadoEndpointTests(APITestCase):
    """
    Tests completos para los endpoints de empleados.
    """

    def setUp(self):
        """
        Configuración inicial para cada test.
        Crea un usuario admin con permisos y datos necesarios.
        """
        self.client = APIClient()

        # Crear permiso 'gestionar_empleados'
        self.permiso_gestionar = Permiso.objects.create(
            nombre='gestionar_empleados',
            descripcion='Permiso para gestionar empleados'
        )

        # Crear rol 'Administrador'
        self.rol_admin = Rol.objects.create(
            nombre='Administrador',
            descripcion='Rol de administrador con todos los permisos'
        )

        # Asignar permiso al rol
        RolPermiso.objects.create(
            rol=self.rol_admin,
            permiso=self.permiso_gestionar
        )

        # Crear persona para el admin
        self.persona_admin = Persona.objects.create(
            nombre='Admin',
            apellido_paterno='Test',
            apellido_materno='User',
            telefono='1234567890'
        )

        # Crear usuario admin
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpassword123',
            persona=self.persona_admin
        )

        # Asignar rol al usuario admin
        PersonaRol.objects.create(
            persona=self.persona_admin,
            rol=self.rol_admin
        )

        # Crear rol para empleados de prueba
        self.rol_empleado = Rol.objects.create(
            nombre='Empleado',
            descripcion='Rol básico de empleado'
        )

        # Autenticar como admin
        self.client.force_authenticate(user=self.admin_user)

    def test_crear_empleado_exitoso(self):
        """
        Test: Crear un empleado nuevo con todos los datos válidos.
        """
        url = reverse('admin_crear_empleado')
        data = {
            'nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'apellido_materno': 'García',
            'fecha_nacimiento': '1990-05-15',
            'sexo': 'Masculino',
            'direccion': 'Calle Principal 123',
            'telefono': '5551234567',
            'email': 'juan.perez@test.com',
            'password': 'password123',
            'puesto': 'Entrenador',
            'departamento': 'Fitness',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Indefinido',
            'salario': '15000.00',
            'estado': 'Activo',
            'rfc': 'PEGJ900515XYZ',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)

        # Verificar que se crearon los registros en la BD
        self.assertTrue(User.objects.filter(email='juan.perez@test.com').exists())
        persona = Persona.objects.get(nombre='Juan', apellido_paterno='Pérez')
        self.assertTrue(Empleado.objects.filter(persona=persona).exists())

    def test_crear_empleado_sin_autenticacion(self):
        """
        Test: Intentar crear empleado sin autenticación debe fallar.
        """
        self.client.force_authenticate(user=None)

        url = reverse('admin_crear_empleado')
        data = {
            'nombre': 'Test',
            'apellido_paterno': 'User',
            'apellido_materno': 'NoAuth',
            'telefono': '5559999999',
            'email': 'noauth@test.com',
            'password': 'password123',
            'puesto': 'Cajero',
            'departamento': 'Ventas',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Temporal',
            'salario': '10000.00',
            'estado': 'Activo',
            'rfc': 'XXXX000000XXX',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_empleado_sin_permisos(self):
        """
        Test: Usuario sin permiso 'gestionar_empleados' no puede crear empleados.
        """
        # Crear usuario sin permisos
        persona_sin_permiso = Persona.objects.create(
            nombre='Usuario',
            apellido_paterno='Sin',
            apellido_materno='Permisos',
            telefono='5558888888'
        )

        user_sin_permiso = User.objects.create_user(
            email='sinpermisos@test.com',
            password='password123',
            persona=persona_sin_permiso
        )

        # Autenticar como usuario sin permisos
        self.client.force_authenticate(user=user_sin_permiso)

        url = reverse('admin_crear_empleado')
        data = {
            'nombre': 'Test',
            'apellido_paterno': 'Forbidden',
            'apellido_materno': 'User',
            'telefono': '5557777777',
            'email': 'forbidden@test.com',
            'password': 'password123',
            'puesto': 'Entrenador',
            'departamento': 'Fitness',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Indefinido',
            'salario': '15000.00',
            'estado': 'Activo',
            'rfc': 'XXXX000000XXX',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_empleados(self):
        """
        Test: Listar todos los empleados existentes.
        """
        # Crear algunos empleados de prueba
        for i in range(3):
            persona = Persona.objects.create(
                nombre=f'Empleado{i}',
                apellido_paterno=f'Apellido{i}',
                apellido_materno=f'Materno{i}',
                telefono=f'555000000{i}'
            )
            user = User.objects.create_user(
                email=f'empleado{i}@test.com',
                password='password123',
                persona=persona
            )

        url = reverse('admin_crear_empleado')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Al menos debería haber 4 usuarios (admin + 3 creados)
        self.assertGreaterEqual(len(response.data), 4)

    def test_obtener_detalle_empleado(self):
        """
        Test: Obtener detalles de un empleado específico.
        """
        # Crear un empleado completo
        persona = Persona.objects.create(
            nombre='Pedro',
            apellido_paterno='López',
            apellido_materno='Ramírez',
            fecha_nacimiento=date(1985, 3, 20),
            sexo='Masculino',
            direccion='Av. Prueba 456',
            telefono='5556667777'
        )

        user = User.objects.create_user(
            email='pedro.lopez@test.com',
            password='password123',
            persona=persona
        )

        empleado = Empleado.objects.create(
            persona=persona,
            puesto='Supervisor',
            departamento='Operaciones',
            fecha_contratacion=date(2023, 6, 1),
            tipo_contrato='Indefinido',
            salario=20000.00,
            estado='Activo',
            rfc='LOPR850320ABC'
        )

        PersonaRol.objects.create(persona=persona, rol=self.rol_empleado)

        url = reverse('admin_usuario_detalle', kwargs={'pk': user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Pedro')
        self.assertEqual(response.data['email'], 'pedro.lopez@test.com')
        self.assertEqual(response.data['puesto'], 'Supervisor')

    def test_actualizar_empleado_completo(self):
        """
        Test: Actualizar todos los datos de un empleado (PUT).
        """
        # Crear empleado
        persona = Persona.objects.create(
            nombre='María',
            apellido_paterno='González',
            apellido_materno='Torres',
            telefono='5554443333'
        )

        user = User.objects.create_user(
            email='maria.gonzalez@test.com',
            password='password123',
            persona=persona
        )

        empleado = Empleado.objects.create(
            persona=persona,
            puesto='Cajero',
            departamento='Ventas',
            fecha_contratacion=date(2024, 1, 1),
            tipo_contrato='Temporal',
            salario=12000.00,
            estado='Activo',
            rfc='GOTM900101XXX'
        )

        PersonaRol.objects.create(persona=persona, rol=self.rol_empleado)

        # Datos actualizados
        url = reverse('admin_usuario_operacion', kwargs={'pk': user.id})
        data = {
            'nombre': 'María',
            'apellido_paterno': 'González',
            'apellido_materno': 'Torres',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'Femenino',
            'direccion': 'Nueva Dirección 789',
            'telefono': '5554443333',
            'email': 'maria.gonzalez@test.com',
            'password': 'newpassword123',
            'puesto': 'Supervisor de Caja',
            'departamento': 'Ventas',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Indefinido',
            'salario': '18000.00',
            'estado': 'Activo',
            'rfc': 'GOTM900101XXX',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Verificar cambios en BD
        empleado.refresh_from_db()
        self.assertEqual(empleado.puesto, 'Supervisor de Caja')
        self.assertEqual(empleado.salario, 18000.00)

    def test_actualizar_empleado_sin_password(self):
        """
        Test: Actualizar empleado sin enviar password (debe mantener el password actual).
        """
        # Crear empleado
        persona = Persona.objects.create(
            nombre='TestPassword',
            apellido_paterno='Usuario',
            apellido_materno='Test',
            telefono='5559998887'
        )

        user = User.objects.create_user(
            email='testpassword@test.com',
            password='originalpassword',
            persona=persona
        )

        empleado = Empleado.objects.create(
            persona=persona,
            puesto='Cajero',
            departamento='Ventas',
            fecha_contratacion=date(2024, 1, 1),
            tipo_contrato='Temporal',
            salario=12000.00,
            estado='Activo',
            rfc='TPUT900101XXX'
        )

        PersonaRol.objects.create(persona=persona, rol=self.rol_empleado)

        # Guardar el hash del password original
        original_password_hash = user.password

        # Actualizar sin enviar password
        url = reverse('admin_usuario_operacion', kwargs={'pk': user.id})
        data = {
            'nombre': 'TestPassword',
            'apellido_paterno': 'Usuario',
            'apellido_materno': 'Test',
            'telefono': '5559998887',
            'email': 'testpassword@test.com',
            # No enviamos password
            'puesto': 'Supervisor',
            'departamento': 'Ventas',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Indefinido',
            'salario': '15000.00',
            'estado': 'Activo',
            'rfc': 'TPUT900101XXX',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Verificar que el password NO cambió
        user.refresh_from_db()
        self.assertEqual(user.password, original_password_hash)

        # Verificar que otros campos sí se actualizaron
        empleado.refresh_from_db()
        self.assertEqual(empleado.puesto, 'Supervisor')
        self.assertEqual(empleado.salario, 15000.00)

    def test_actualizar_empleado_parcial(self):
        """
        Test: Actualizar solo algunos campos de un empleado (PATCH).
        """
        # Crear empleado
        persona = Persona.objects.create(
            nombre='Carlos',
            apellido_paterno='Martínez',
            apellido_materno='Sánchez',
            telefono='5552221111'
        )

        user = User.objects.create_user(
            email='carlos.martinez@test.com',
            password='password123',
            persona=persona
        )

        empleado = Empleado.objects.create(
            persona=persona,
            puesto='Entrenador',
            departamento='Fitness',
            fecha_contratacion=date(2023, 1, 1),
            tipo_contrato='Indefinido',
            salario=15000.00,
            estado='Activo',
            rfc='MASC900101XXX'
        )

        PersonaRol.objects.create(persona=persona, rol=self.rol_empleado)

        # Actualizar solo salario y estado
        url = reverse('admin_usuario_operacion', kwargs={'pk': user.id})
        data = {
            'salario': '17000.00',
            'estado': 'Activo'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Verificar que solo cambió el salario
        empleado.refresh_from_db()
        self.assertEqual(empleado.salario, 17000.00)
        self.assertEqual(empleado.puesto, 'Entrenador')  # No cambió

    def test_eliminar_empleado(self):
        """
        Test: Eliminar un empleado existente.
        """
        # Crear empleado
        persona = Persona.objects.create(
            nombre='Eliminado',
            apellido_paterno='Prueba',
            apellido_materno='Test',
            telefono='5559998888'
        )

        user = User.objects.create_user(
            email='eliminar@test.com',
            password='password123',
            persona=persona
        )

        url = reverse('admin_usuario_operacion', kwargs={'pk': user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(response.data['success'])

        # Verificar que se eliminó
        self.assertFalse(User.objects.filter(email='eliminar@test.com').exists())

    def test_obtener_empleado_inexistente(self):
        """
        Test: Intentar obtener un empleado que no existe.
        """
        url = reverse('admin_usuario_detalle', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_crear_empleado_con_email_duplicado(self):
        """
        Test: No se puede crear empleado con email ya existente.
        """
        # Crear primer empleado
        persona1 = Persona.objects.create(
            nombre='Primero',
            apellido_paterno='Usuario',
            apellido_materno='Test',
            telefono='5551111111'
        )

        User.objects.create_user(
            email='duplicado@test.com',
            password='password123',
            persona=persona1
        )

        # Intentar crear segundo con mismo email
        url = reverse('admin_crear_empleado')
        data = {
            'nombre': 'Segundo',
            'apellido_paterno': 'Usuario',
            'apellido_materno': 'Test',
            'telefono': '5552222222',
            'email': 'duplicado@test.com',  # Email duplicado
            'password': 'password123',
            'puesto': 'Cajero',
            'departamento': 'Ventas',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Temporal',
            'salario': '10000.00',
            'estado': 'Activo',
            'rfc': 'XXXX000000XXX',
            'rol_id': self.rol_empleado.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_empleado_con_rol_invalido(self):
        """
        Test: No se puede crear empleado con un rol_id que no existe.
        """
        url = reverse('admin_crear_empleado')
        data = {
            'nombre': 'Test',
            'apellido_paterno': 'RolInvalido',
            'apellido_materno': 'User',
            'telefono': '5553333333',
            'email': 'rolinvalido@test.com',
            'password': 'password123',
            'puesto': 'Entrenador',
            'departamento': 'Fitness',
            'fecha_contratacion': '2024-01-01',
            'tipo_contrato': 'Indefinido',
            'salario': '15000.00',
            'estado': 'Activo',
            'rfc': 'XXXX000000XXX',
            'rol_id': 99999  # Rol inexistente
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
