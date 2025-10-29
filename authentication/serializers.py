from rest_framework import serializers
from .models import Persona, User
from empleados.models import Empleado
from roles.models import Rol, PersonaRol

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'

class UserListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    nombre = serializers.SerializerMethodField()
    apellido_paterno = serializers.SerializerMethodField()
    apellido_materno = serializers.SerializerMethodField()
    rol_id = serializers.SerializerMethodField()
    rol_nombre = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    sede_id = serializers.SerializerMethodField()
    sede_nombre = serializers.SerializerMethodField()
    espacios_nombres = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return obj.persona.nombre if obj.persona else None

    def get_apellido_paterno(self, obj):
        return obj.persona.apellido_paterno if obj.persona else None

    def get_apellido_materno(self, obj):
        return obj.persona.apellido_materno if obj.persona else None

    def get_rol_id(self, obj):
        try:
            persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
            return persona_rol.rol.id if persona_rol else None
        except Exception:
            return None

    def get_rol_nombre(self, obj):
        try:
            persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
            return persona_rol.rol.nombre if persona_rol else None
        except Exception:
            return None

    def get_estado(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            return empleado.estado
        except Empleado.DoesNotExist:
            return "Sin estado"
        except Exception:
            return "Sin estado"

    def get_sede_id(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            return empleado.sede.id if empleado.sede else None
        except Empleado.DoesNotExist:
            return None
        except Exception:
            return None

    def get_sede_nombre(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            return empleado.sede.nombre if empleado.sede else None
        except Empleado.DoesNotExist:
            return None
        except Exception:
            return None

    def get_espacios_nombres(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            # Buscar en los modelos especificos (Entrenador, Cajero, etc.)
            espacios = []

            if hasattr(empleado, 'entrenador'):
                espacios = list(empleado.entrenador.espacio.values_list('nombre', flat=True))
            elif hasattr(empleado, 'cajero'):
                espacios = list(empleado.cajero.espacio.values_list('nombre', flat=True))
            elif hasattr(empleado, 'personallimpieza'):
                espacios = list(empleado.personallimpieza.espacio.values_list('nombre', flat=True))
            elif hasattr(empleado, 'supervisorespacio'):
                espacios = list(empleado.supervisorespacio.espacio.values_list('nombre', flat=True))

            return espacios
        except Empleado.DoesNotExist:
            return []
        except Exception:
            return []

class UserDetailSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    empleado = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_empleado(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            return EmpleadoSerializer(empleado).data
        except Empleado.DoesNotExist:
            return None

class EmpleadoUserCreateSerializer(serializers.Serializer):
    # Datos personales
    nombre = serializers.CharField(max_length=50)
    apellido_paterno = serializers.CharField(max_length=50)
    apellido_materno = serializers.CharField(max_length=50)
    fecha_nacimiento = serializers.DateField(required=False)
    sexo = serializers.CharField(max_length=10, required=False)
    direccion = serializers.CharField(max_length=255, required=False)
    telefono = serializers.CharField(max_length=10)
    # Datos de usuario
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Datos de empleado
    puesto = serializers.CharField(max_length=50)
    departamento = serializers.CharField(max_length=50)
    fecha_contratacion = serializers.DateField()
    tipo_contrato = serializers.CharField(max_length=50)
    salario = serializers.DecimalField(max_digits=10, decimal_places=2)
    estado = serializers.CharField(max_length=20)
    rfc = serializers.CharField(max_length=13)
    # Rol
    rol_id = serializers.IntegerField()
    # Documentos (archivos)
    identificacion = serializers.FileField(required=False, allow_null=True)
    comprobante = serializers.FileField(required=False, allow_null=True)

    def validate_email(self, value):
        """Validar que el email no exista ya en la BD"""
        # Permitir el mismo email en actualizaciones
        if self.instance:
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email.")
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_rol_id(self, value):
        """Validar que el rol_id exista en la BD"""
        if not Rol.objects.filter(pk=value).exists():
            raise serializers.ValidationError("El rol especificado no existe.")
        return value

    def validate(self, data):
        """Validación general: password es requerido solo al crear"""
        if not self.instance:  # Modo creación
            if not data.get('password'):
                raise serializers.ValidationError({
                    'password': 'La contraseña es requerida al crear un empleado.'
                })
        return data

    def create(self, validated_data):
        # Extraer archivos antes de crear los objetos
        identificacion = validated_data.pop('identificacion', None)
        comprobante = validated_data.pop('comprobante', None)

        # 1. Crear Persona
        persona = Persona.objects.create(
            nombre=validated_data['nombre'],
            apellido_paterno=validated_data['apellido_paterno'],
            apellido_materno=validated_data['apellido_materno'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            sexo=validated_data.get('sexo'),
            direccion=validated_data.get('direccion'),
            telefono=validated_data['telefono'],
        )
        # 2. Crear User
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            persona=persona
        )
        # 3. Crear Empleado con archivos
        empleado = Empleado.objects.create(
            persona=persona,
            puesto=validated_data['puesto'],
            departamento=validated_data['departamento'],
            fecha_contratacion=validated_data['fecha_contratacion'],
            tipo_contrato=validated_data['tipo_contrato'],
            salario=validated_data['salario'],
            estado=validated_data['estado'],
            rfc=validated_data['rfc'],
            identificacion=identificacion,
            comprobante_domicilio=comprobante,
        )
        # 4. Asignar Rol
        rol = Rol.objects.get(pk=validated_data['rol_id'])
        PersonaRol.objects.create(persona=persona, rol=rol)
        return user

    def update(self, instance, validated_data):
        # Extraer archivos
        identificacion = validated_data.pop('identificacion', None)
        comprobante = validated_data.pop('comprobante', None)

        # Actualiza Persona
        persona = instance.persona
        for field in ['nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 'sexo', 'direccion', 'telefono']:
            if field in validated_data:
                setattr(persona, field, validated_data[field])
        persona.save()

        # Actualiza User
        if 'email' in validated_data:
            instance.email = validated_data['email']
        # Solo actualizar password si se proporciona y no está vacío
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        instance.save()

        # Actualiza Empleado
        empleado = Empleado.objects.get(persona=persona)
        for field in ['puesto', 'departamento', 'fecha_contratacion', 'tipo_contrato', 'salario', 'estado', 'rfc']:
            if field in validated_data:
                setattr(empleado, field, validated_data[field])

        # Actualizar archivos si se enviaron nuevos
        if identificacion:
            empleado.identificacion = identificacion
        if comprobante:
            empleado.comprobante_domicilio = comprobante

        empleado.save()

        # Actualiza Rol si se envía
        rol_id = validated_data.get('rol_id', None)
        if rol_id:
            rol = Rol.objects.get(pk=rol_id)
            PersonaRol.objects.update_or_create(persona=persona, defaults={'rol': rol})

        return instance

class EmpleadoRegistroSerializer(EmpleadoUserCreateSerializer):
    """
    Puedes heredar de EmpleadoUserCreateSerializer si el registro es igual.
    Si necesitas campos extra, agrégalos aquí.
    """
    pass

class EmpleadoUserDetailSerializer(serializers.Serializer):
    nombre = serializers.CharField(source='persona.nombre')
    apellido_paterno = serializers.CharField(source='persona.apellido_paterno')
    apellido_materno = serializers.CharField(source='persona.apellido_materno')
    fecha_nacimiento = serializers.DateField(source='persona.fecha_nacimiento')
    sexo = serializers.CharField(source='persona.sexo')
    direccion = serializers.CharField(source='persona.direccion')
    telefono = serializers.CharField(source='persona.telefono')
    email = serializers.EmailField()
    puesto = serializers.CharField(source='persona.empleado.puesto')
    departamento = serializers.CharField(source='persona.empleado.departamento')
    fecha_contratacion = serializers.DateField(source='persona.empleado.fecha_contratacion')
    tipo_contrato = serializers.CharField(source='persona.empleado.tipo_contrato')
    salario = serializers.DecimalField(source='persona.empleado.salario', max_digits=10, decimal_places=2)
    estado = serializers.CharField(source='persona.empleado.estado')
    rfc = serializers.CharField(source='persona.empleado.rfc')
    rol_id = serializers.SerializerMethodField()
    rol_nombre = serializers.SerializerMethodField()
    # Documentos
    identificacion_url = serializers.SerializerMethodField()
    comprobante_url = serializers.SerializerMethodField()
    certificados_url = serializers.SerializerMethodField()

    def get_rol_id(self, obj):
        persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
        return persona_rol.rol.id if persona_rol else None

    def get_rol_nombre(self, obj):
        persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
        return persona_rol.rol.nombre if persona_rol else None

    def get_identificacion_url(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            if empleado.identificacion:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(empleado.identificacion.url)
                return empleado.identificacion.url
        except Empleado.DoesNotExist:
            pass
        return None

    def get_comprobante_url(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            if empleado.comprobante_domicilio:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(empleado.comprobante_domicilio.url)
                return empleado.comprobante_domicilio.url
        except Empleado.DoesNotExist:
            pass
        return None

    def get_certificados_url(self, obj):
        try:
            empleado = Empleado.objects.get(persona=obj.persona)
            if empleado.certificados:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(empleado.certificados.url)
                return empleado.certificados.url
        except Empleado.DoesNotExist:
            pass
        return None
