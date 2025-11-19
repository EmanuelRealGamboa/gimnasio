from django.core.management.base import BaseCommand
from authentication.models import User, Persona
from empleados.models import Empleado, Entrenador, Cajero, PersonalLimpieza, SupervisorEspacio
from roles.models import PersonaRol


class Command(BaseCommand):
    help = 'Elimina todos los empleados excepto el administrador y limpia registros huérfanos'

    def handle(self, *args, **options):
        self.stdout.write("🗑️  Iniciando limpieza de empleados...")

        # Obtener todos los empleados
        empleados = Empleado.objects.select_related('persona').all()

        total_eliminados = 0

        for empleado in empleados:
            persona = empleado.persona

            # Verificar si es el usuario admin principal (por email)
            try:
                user = User.objects.get(persona=persona)
                if user.email == 'admin@gmail.com':
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Manteniendo administrador principal: {persona.nombre} ({user.email})"
                        )
                    )
                    continue
            except User.DoesNotExist:
                pass

            # Eliminar registros específicos de rol antes de eliminar el usuario
            try:
                if hasattr(empleado, 'entrenador'):
                    empleado.entrenador.delete()
                if hasattr(empleado, 'cajero'):
                    empleado.cajero.delete()
                if hasattr(empleado, 'personallimpieza'):
                    empleado.personallimpieza.delete()
                if hasattr(empleado, 'supervisorespacio'):
                    empleado.supervisorespacio.delete()
            except:
                pass

            # Eliminar el usuario (esto eliminará en cascada Persona, Empleado, etc.)
            try:
                user = User.objects.get(persona=persona)
                nombre_completo = f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
                user.delete()
                total_eliminados += 1
                self.stdout.write(f"🗑️  Eliminado: {nombre_completo}")
            except User.DoesNotExist:
                # Si no hay usuario, eliminar la persona directamente
                nombre_completo = f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
                persona.delete()
                total_eliminados += 1
                self.stdout.write(f"🗑️  Eliminada persona: {nombre_completo}")

        # Limpiar registros huérfanos (registros de roles específicos sin empleado)
        self.stdout.write("\n🧹 Limpiando registros huérfanos...")

        huerfanos_entrenador = Entrenador.objects.filter(empleado__isnull=True).count()
        Entrenador.objects.filter(empleado__isnull=True).delete()
        if huerfanos_entrenador > 0:
            self.stdout.write(f"🗑️  Eliminados {huerfanos_entrenador} entrenadores huérfanos")

        huerfanos_cajero = Cajero.objects.filter(empleado__isnull=True).count()
        Cajero.objects.filter(empleado__isnull=True).delete()
        if huerfanos_cajero > 0:
            self.stdout.write(f"🗑️  Eliminados {huerfanos_cajero} cajeros huérfanos")

        huerfanos_limpieza = PersonalLimpieza.objects.filter(empleado__isnull=True).count()
        PersonalLimpieza.objects.filter(empleado__isnull=True).delete()
        if huerfanos_limpieza > 0:
            self.stdout.write(f"🗑️  Eliminados {huerfanos_limpieza} personal de limpieza huérfanos")

        huerfanos_supervisor = SupervisorEspacio.objects.filter(empleado__isnull=True).count()
        SupervisorEspacio.objects.filter(empleado__isnull=True).delete()
        if huerfanos_supervisor > 0:
            self.stdout.write(f"🗑️  Eliminados {huerfanos_supervisor} supervisores huérfanos")

        self.stdout.write("\n")
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Limpieza completada: {total_eliminados} empleado(s) eliminado(s)"
            )
        )

        # Mostrar cuántos empleados quedan
        empleados_restantes = Empleado.objects.count()
        self.stdout.write(f"📊 Empleados restantes: {empleados_restantes}")

        # Verificar registros de roles específicos
        total_entrenadores = Entrenador.objects.count()
        total_cajeros = Cajero.objects.count()
        total_limpieza = PersonalLimpieza.objects.count()
        total_supervisores = SupervisorEspacio.objects.count()

        self.stdout.write(f"📊 Entrenadores: {total_entrenadores}")
        self.stdout.write(f"📊 Cajeros: {total_cajeros}")
        self.stdout.write(f"📊 Personal de Limpieza: {total_limpieza}")
        self.stdout.write(f"📊 Supervisores: {total_supervisores}")
