from rest_framework import serializers
from .models import Cliente
from authentication.models import Persona, User, ContactoEmergencia
from roles.models import Rol, PersonaRol


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer básico para el modelo Cliente"""
    class Meta:
        model = Cliente
        fields = '__all__'


class ClienteListSerializer(serializers.Serializer):
    """Serializer para listar clientes con información resumida"""
    id = serializers.IntegerField(source='persona.id')
    nombre = serializers.CharField(source='persona.nombre')
    apellido_paterno = serializers.CharField(source='persona.apellido_paterno')
    apellido_materno = serializers.CharField(source='persona.apellido_materno')
    telefono = serializers.CharField(source='persona.telefono')
    email = serializers.SerializerMethodField()
    nivel_experiencia = serializers.CharField()
    estado = serializers.CharField()
    fecha_registro = serializers.DateField()
    objetivo_fitness = serializers.CharField()

    def get_email(self, obj):
        try:
            user = User.objects.get(persona=obj.persona)
            return user.email
        except User.DoesNotExist:
            return None


class ClienteCreateSerializer(serializers.Serializer):
    """Serializer para crear un nuevo cliente"""
    # Datos personales (Persona)
    nombre = serializers.CharField(max_length=50)
    apellido_paterno = serializers.CharField(max_length=50)
    apellido_materno = serializers.CharField(max_length=50)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    sexo = serializers.CharField(max_length=10, required=False, allow_blank=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=10)

    # Datos de usuario (User)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6, required=False, allow_blank=True)

    # Datos de cliente (Cliente)
    objetivo_fitness = serializers.CharField(max_length=255, required=False, allow_blank=True)
    nivel_experiencia = serializers.ChoiceField(
        choices=Cliente.NIVEL_EXPERIENCIA_CHOICES,
        default='principiante'
    )
    estado = serializers.ChoiceField(
        choices=Cliente.ESTADO_CHOICES,
        default='activo'
    )

    # Datos de contacto de emergencia (ContactoEmergencia)
    nombre_contacto = serializers.CharField(max_length=100, required=False, allow_blank=True)
    telefono_contacto = serializers.CharField(max_length=10, required=False, allow_blank=True)
    parentesco = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_email(self, value):
        """Validar que el email no exista en la BD"""
        if self.instance:
            if User.objects.filter(email=value).exclude(persona=self.instance.persona).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email.")
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate(self, data):
        """Validar que password sea obligatorio al crear, pero opcional al actualizar"""
        if not self.instance:  # Modo creación
            if not data.get('password'):
                raise serializers.ValidationError({'password': 'La contraseña es requerida al crear un cliente.'})
        return data

    def create(self, validated_data):
        # Extraer datos de contacto de emergencia
        nombre_contacto = validated_data.pop('nombre_contacto', None)
        telefono_contacto = validated_data.pop('telefono_contacto', None)
        parentesco = validated_data.pop('parentesco', None)

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

        # 2. Crear User con contraseña obligatoria
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            persona=persona
        )

        # 3. Crear Cliente
        cliente = Cliente.objects.create(
            persona=persona,
            objetivo_fitness=validated_data.get('objetivo_fitness', ''),
            nivel_experiencia=validated_data.get('nivel_experiencia', 'principiante'),
            estado=validated_data.get('estado', 'activo'),
        )

        # 4. Asignar rol de Cliente automáticamente
        try:
            rol_cliente = Rol.objects.get(nombre='Cliente')
            PersonaRol.objects.create(persona=persona, rol=rol_cliente)
        except Rol.DoesNotExist:
            # Si no existe el rol Cliente, lo creamos
            rol_cliente = Rol.objects.create(nombre='Cliente', descripcion='Cliente del gimnasio')
            PersonaRol.objects.create(persona=persona, rol=rol_cliente)

        # 5. Crear ContactoEmergencia si se proporcionaron datos
        if nombre_contacto or telefono_contacto:
            ContactoEmergencia.objects.create(
                persona=persona,
                nombre_contacto=nombre_contacto,
                telefono_contacto=telefono_contacto,
                parentesco=parentesco
            )

        return cliente

    def update(self, instance, validated_data):
        # Extraer datos de contacto de emergencia
        nombre_contacto = validated_data.pop('nombre_contacto', None)
        telefono_contacto = validated_data.pop('telefono_contacto', None)
        parentesco = validated_data.pop('parentesco', None)

        # Actualizar Persona
        persona = instance.persona
        for field in ['nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 'sexo', 'direccion', 'telefono']:
            if field in validated_data:
                setattr(persona, field, validated_data[field])
        persona.save()

        # Actualizar User
        try:
            user = User.objects.get(persona=persona)
            if 'email' in validated_data:
                user.email = validated_data['email']
            if 'password' in validated_data and validated_data['password']:
                user.set_password(validated_data['password'])
            user.save()
        except User.DoesNotExist:
            pass

        # Actualizar Cliente
        for field in ['objetivo_fitness', 'nivel_experiencia', 'estado']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        # Actualizar ContactoEmergencia
        if nombre_contacto is not None or telefono_contacto is not None:
            contacto, created = ContactoEmergencia.objects.get_or_create(persona=persona)
            if nombre_contacto is not None:
                contacto.nombre_contacto = nombre_contacto
            if telefono_contacto is not None:
                contacto.telefono_contacto = telefono_contacto
            if parentesco is not None:
                contacto.parentesco = parentesco
            contacto.save()

        return instance


class ClienteDetailSerializer(serializers.Serializer):
    """Serializer para mostrar el detalle completo de un cliente"""
    # Datos de Persona
    id = serializers.IntegerField(source='persona.id')
    nombre = serializers.CharField(source='persona.nombre')
    apellido_paterno = serializers.CharField(source='persona.apellido_paterno')
    apellido_materno = serializers.CharField(source='persona.apellido_materno')
    fecha_nacimiento = serializers.DateField(source='persona.fecha_nacimiento')
    sexo = serializers.CharField(source='persona.sexo')
    direccion = serializers.CharField(source='persona.direccion')
    telefono = serializers.CharField(source='persona.telefono')

    # Datos de User
    email = serializers.SerializerMethodField()

    # Datos de Cliente
    objetivo_fitness = serializers.CharField()
    nivel_experiencia = serializers.CharField()
    estado = serializers.CharField()
    fecha_registro = serializers.DateField()

    # Datos de ContactoEmergencia
    nombre_contacto = serializers.SerializerMethodField()
    telefono_contacto = serializers.SerializerMethodField()
    parentesco = serializers.SerializerMethodField()

    # Rol
    rol_nombre = serializers.SerializerMethodField()

    def get_email(self, obj):
        try:
            user = User.objects.get(persona=obj.persona)
            return user.email
        except User.DoesNotExist:
            return None

    def get_nombre_contacto(self, obj):
        try:
            contacto = ContactoEmergencia.objects.get(persona=obj.persona)
            return contacto.nombre_contacto
        except ContactoEmergencia.DoesNotExist:
            return None

    def get_telefono_contacto(self, obj):
        try:
            contacto = ContactoEmergencia.objects.get(persona=obj.persona)
            return contacto.telefono_contacto
        except ContactoEmergencia.DoesNotExist:
            return None

    def get_parentesco(self, obj):
        try:
            contacto = ContactoEmergencia.objects.get(persona=obj.persona)
            return contacto.parentesco
        except ContactoEmergencia.DoesNotExist:
            return None

    def get_rol_nombre(self, obj):
        try:
            persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
            return persona_rol.rol.nombre if persona_rol else None
        except Exception:
            return None
