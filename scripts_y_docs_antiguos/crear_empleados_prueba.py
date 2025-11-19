import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from empleados.models import Empleado, Entrenador, Cajero, PersonalLimpieza, SupervisorEspacio
from authentication.models import Persona, User
from roles.models import Rol, PersonaRol
from instalaciones.models import Sede, Espacio

def generar_rfc():
    """Genera un RFC aleatorio"""
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numeros = '0123456789'
    return ''.join(random.choices(letras, k=4)) + ''.join(random.choices(numeros, k=6)) + ''.join(random.choices(letras + numeros, k=3))

def generar_curp():
    """Genera un CURP aleatorio"""
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numeros = '0123456789'
    return ''.join(random.choices(letras, k=4)) + ''.join(random.choices(numeros, k=6)) + ''.join(random.choices(letras, k=6)) + ''.join(random.choices(numeros, k=2))

def generar_nss():
    """Genera un NSS aleatorio"""
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def generar_telefono():
    """Genera un telefono aleatorio de 10 digitos"""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def crear_empleados():
    print("Iniciando creacion de empleados de prueba...")

    # Obtener roles
    roles = list(Rol.objects.all())
    if not roles:
        print("ERROR: No hay roles en la base de datos.")
        return

    print(f"OK: Roles encontrados: {len(roles)}")
    for rol in roles:
        print(f"   - {rol.nombre}")

    # Obtener sedes
    sedes = list(Sede.objects.all())
    if not sedes:
        print("ERROR: No hay sedes en la base de datos.")
        return

    print(f"OK: Sedes encontradas: {len(sedes)}")
    for sede in sedes:
        print(f"   - {sede.nombre}")

    # Obtener espacios
    espacios = list(Espacio.objects.all())
    print(f"OK: Espacios encontrados: {len(espacios)}")

    # Listas de nombres y apellidos
    nombres_masculinos = [
        'Juan', 'Pedro', 'Luis', 'Carlos', 'Jose', 'Miguel', 'Antonio', 'Francisco',
        'Jorge', 'Roberto', 'Fernando', 'Ricardo', 'Alberto', 'Alejandro', 'Eduardo',
        'Raul', 'Sergio', 'Javier', 'Daniel', 'Andres', 'Oscar', 'Mario', 'Rafael',
        'Enrique', 'Arturo', 'Hector', 'Manuel'
    ]

    nombres_femeninos = [
        'Maria', 'Ana', 'Sofia', 'Laura', 'Carmen', 'Isabel', 'Patricia', 'Rosa',
        'Lucia', 'Gabriela', 'Valentina', 'Daniela', 'Andrea', 'Fernanda', 'Paola',
        'Claudia', 'Natalia', 'Diana', 'Mariana', 'Carolina', 'Elena', 'Veronica',
        'Alejandra', 'Monica', 'Teresa'
    ]

    apellidos = [
        'Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Hernandez', 'Perez',
        'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Rivera', 'Gomez', 'Diaz', 'Cruz',
        'Morales', 'Reyes', 'Gutierrez', 'Ortiz', 'Jimenez', 'Vargas', 'Castillo',
        'Romero', 'Alvarez', 'Medina', 'Ruiz', 'Silva', 'Castro', 'Guerrero', 'Mendoza'
    ]

    # Roles que necesitan modelos específicos
    roles_con_turno = ['Entrenador', 'Cajero', 'Personal de Limpieza', 'Supervisor de Instalaciones']
    turnos = ['Matutino', 'Vespertino', 'Nocturno']
    tipos_contrato = ['Indefinido', 'Temporal', 'Por Proyecto']

    # Rangos de salario por rol
    salarios_base = {
        'Administrador': (15000, 25000),
        'Entrenador': (8000, 15000),
        'Recepcionista': (6000, 9000),
        'Cajero': (6000, 10000),
        'Supervisor de Instalaciones': (8000, 12000),
        'Personal de Limpieza': (5000, 7000)
    }

    empleados_creados = 0
    empleados_por_sede = {sede.id: 0 for sede in sedes}

    print("\nCreando 60 empleados...")

    for i in range(60):
        try:
            # Alternar entre masculino y femenino
            sexo = 'Masculino' if i % 2 == 0 else 'Femenino'

            if sexo == 'Masculino':
                nombre = random.choice(nombres_masculinos)
            else:
                nombre = random.choice(nombres_femeninos)

            apellido_paterno = random.choice(apellidos)
            apellido_materno = random.choice(apellidos)

            # Seleccionar rol aleatorio (excluir Cliente)
            rol = random.choice([r for r in roles if r.nombre != 'Cliente'])

            # Seleccionar sede (distribuir equitativamente)
            sede = sedes[i % len(sedes)]
            empleados_por_sede[sede.id] += 1

            # Filtrar espacios de esta sede
            espacios_sede = [e for e in espacios if e.sede_id == sede.id]

            # Generar fecha de nacimiento (entre 20 y 50 años)
            edad = random.randint(20, 50)
            fecha_nacimiento = datetime.now().date() - timedelta(days=edad*365)

            # Generar fecha de contratacion (ultimo año)
            dias_contratacion = random.randint(30, 365)
            fecha_contratacion = datetime.now().date() - timedelta(days=dias_contratacion)

            # Generar salario
            rango_salario = salarios_base.get(rol.nombre, (6000, 10000))
            salario = random.randint(rango_salario[0], rango_salario[1])

            # Crear email unico
            email = f"{nombre.lower()}.{apellido_paterno.lower()}{i+1}@gmail.com"

            # Crear Persona
            persona = Persona.objects.create(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                direccion=f"Calle {random.randint(1, 100)} #{random.randint(1, 500)}, Col. Centro",
                telefono=generar_telefono()
            )

            # Crear User (necesario para el frontend)
            user = User.objects.create_user(
                email=email,
                password='password123',
                persona=persona
            )

            # Crear relacion Persona-Rol
            PersonaRol.objects.create(
                persona=persona,
                rol=rol
            )

            # Crear Empleado
            empleado = Empleado.objects.create(
                persona=persona,
                puesto=rol.nombre,
                departamento=rol.nombre,
                fecha_contratacion=fecha_contratacion,
                tipo_contrato=random.choice(tipos_contrato),
                salario=salario,
                estado='Activo' if random.random() > 0.1 else 'Inactivo',
                rfc=generar_rfc(),
                curp=generar_curp(),
                nss=generar_nss(),
                sede=sede
            )

            # Crear modelo especifico segun el rol
            if rol.nombre in roles_con_turno and espacios_sede:
                turno = random.choice(turnos)
                num_espacios = random.randint(1, min(3, len(espacios_sede)))
                espacios_asignados = random.sample(espacios_sede, num_espacios)

                if rol.nombre == 'Entrenador':
                    modelo_especifico = Entrenador.objects.create(
                        empleado=empleado,
                        especialidad='Fitness' if random.random() > 0.5 else 'Crossfit',
                        certificaciones='Certificacion Nacional de Fitness',
                        turno=turno,
                        sede=sede
                    )
                    modelo_especifico.espacio.set(espacios_asignados)

                elif rol.nombre == 'Cajero':
                    modelo_especifico = Cajero.objects.create(
                        empleado=empleado,
                        turno=turno,
                        sede=sede
                    )
                    modelo_especifico.espacio.set(espacios_asignados)

                elif rol.nombre == 'Personal de Limpieza':
                    modelo_especifico = PersonalLimpieza.objects.create(
                        empleado=empleado,
                        turno=turno,
                        sede=sede
                    )
                    modelo_especifico.espacio.set(espacios_asignados)

                elif rol.nombre == 'Supervisor de Instalaciones':
                    modelo_especifico = SupervisorEspacio.objects.create(
                        empleado=empleado,
                        turno=turno,
                        sede=sede
                    )
                    modelo_especifico.espacio.set(espacios_asignados)

            empleados_creados += 1
            print(f"[OK] Empleado {empleados_creados}/60: {nombre} {apellido_paterno} - {rol.nombre} - {sede.nombre}")

        except Exception as e:
            print(f"[ERROR] Error al crear empleado {i+1}: {str(e)}")

    print(f"\nProceso completado!")
    print(f"Total de empleados creados: {empleados_creados}")
    print(f"\nDistribucion por sede:")
    for sede in sedes:
        count = Empleado.objects.filter(sede=sede).count()
        print(f"   - {sede.nombre}: {count} empleados")

    # Mostrar estadisticas por rol
    print(f"\nDistribucion por rol:")
    for rol in roles:
        count = Empleado.objects.filter(puesto=rol.nombre).count()
        if count > 0:
            print(f"   - {rol.nombre}: {count} empleados")

if __name__ == '__main__':
    crear_empleados()
