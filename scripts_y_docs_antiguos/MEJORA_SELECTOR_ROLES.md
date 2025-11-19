# Mejora: Selector de Roles con Nombres

## Problema
En el formulario de crear/editar empleado, solo aparecía un campo numérico para ingresar el `rol_id`, lo cual no era intuitivo para el usuario.

## Solución Implementada

### 1. Backend - Nuevo Endpoint para Roles

#### `roles/views.py` - Vista para listar roles
```python
class RolListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data)
```

#### `roles/urls.py` - Nueva ruta
```python
path('roles/', RolListView.as_view(), name='roles_list')
```

#### `gym/urls.py` - Incluir rutas de roles
```python
path('api/', include('roles.urls'))
```

**Endpoint disponible**: `GET /api/roles/`

**Respuesta**:
```json
[
  {
    "id": 1,
    "nombre": "Administrador",
    "descripcion": "Administrador del sistema"
  },
  {
    "id": 2,
    "nombre": "Empleado",
    "descripcion": "Empleado regular"
  }
]
```

### 2. Backend - Serializer Mejorado

#### `authentication/serializers.py` - Agregar nombre de rol al detalle
```python
class EmpleadoUserDetailSerializer(serializers.Serializer):
    # ... campos existentes ...
    rol_id = serializers.SerializerMethodField()
    rol_nombre = serializers.SerializerMethodField()  # ← NUEVO

    def get_rol_nombre(self, obj):
        persona_rol = PersonaRol.objects.filter(persona=obj.persona).first()
        return persona_rol.rol.nombre if persona_rol else None
```

### 3. Frontend - Servicio de Roles

#### `frontend/src/services/roleService.js`
```javascript
import api from './api';

class RoleService {
  getRoles() {
    return api.get('/roles/');
  }
}

export default new RoleService();
```

### 4. Frontend - Formulario con Dropdown

#### `frontend/src/components/EmployeeForm.js`

**Estado agregado**:
```javascript
const [roles, setRoles] = useState([]);
```

**Función para cargar roles**:
```javascript
const fetchRoles = async () => {
  try {
    const response = await roleService.getRoles();
    setRoles(response.data);
    if (!formData.rol_id && response.data.length > 0) {
      setFormData(prev => ({ ...prev, rol_id: response.data[0].id }));
    }
  } catch (err) {
    console.error('Error al cargar roles:', err);
  }
};
```

**Dropdown de roles**:
```jsx
<div className="form-group">
  <label htmlFor="rol_id">Rol *</label>
  <select
    id="rol_id"
    name="rol_id"
    value={formData.rol_id}
    onChange={handleChange}
    required
  >
    <option value="">Seleccionar rol</option>
    {roles.map((rol) => (
      <option key={rol.id} value={rol.id}>
        {rol.nombre}
      </option>
    ))}
  </select>
</div>
```

### 5. Frontend - Vista de Detalles Mejorada

#### `frontend/src/components/EmployeeDetail.js`

**Antes**:
```jsx
<label>Rol ID:</label>
<span>{employee.rol_id}</span>
```

**Ahora**:
```jsx
<label>Rol:</label>
<span>{employee.rol_nombre || 'No asignado'}</span>
```

## Resultado

### Formulario de Crear/Editar
- ✅ **Antes**: Campo numérico para ingresar `rol_id` manualmente
- ✅ **Ahora**: Dropdown con nombres de roles disponibles

### Vista de Detalles
- ✅ **Antes**: Solo mostraba el número del rol (ej: "2")
- ✅ **Ahora**: Muestra el nombre del rol (ej: "Empleado")

## Experiencia de Usuario

### Al crear un empleado:
1. El campo "Rol" muestra un dropdown
2. Se listan todos los roles con sus nombres descriptivos
3. El usuario selecciona el rol apropiado
4. No necesita memorizar IDs

### Al editar un empleado:
1. El dropdown muestra el rol actual seleccionado
2. Puede cambiar a otro rol de la lista
3. Los cambios se reflejan inmediatamente

### Al ver detalles:
1. Muestra el nombre del rol (ej: "Administrador")
2. Más fácil de entender que un número

## Archivos Modificados

### Backend
1. `roles/views.py` - Nueva vista para listar roles
2. `roles/urls.py` - Nueva ruta para roles
3. `gym/urls.py` - Incluir rutas de roles
4. `authentication/serializers.py` - Agregar campo `rol_nombre`

### Frontend
1. `frontend/src/services/roleService.js` - Nuevo servicio
2. `frontend/src/components/EmployeeForm.js` - Dropdown de roles
3. `frontend/src/components/EmployeeDetail.js` - Mostrar nombre del rol

## Pruebas

Para probar esta funcionalidad:

1. **Asegúrate de tener roles en la BD**:
```bash
python manage.py shell
```

```python
from roles.models import Rol

# Verificar roles existentes
roles = Rol.objects.all()
for rol in roles:
    print(f"{rol.id}: {rol.nombre}")

# Si no hay roles, crear algunos
if not roles:
    Rol.objects.create(nombre='Administrador', descripcion='Admin del sistema')
    Rol.objects.create(nombre='Empleado', descripcion='Empleado regular')
    print("Roles creados")
```

2. **Iniciar el backend**:
```bash
python manage.py runserver
```

3. **Iniciar el frontend**:
```bash
cd frontend
npm start
```

4. **Probar**:
   - Ir a "Nuevo Empleado"
   - Ver el dropdown de roles
   - Seleccionar un rol
   - Crear el empleado
   - Ver los detalles y confirmar que muestra el nombre del rol

## API Endpoints Actualizados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/roles/` | Listar todos los roles |
| GET | `/api/admin/empleados/<id>/detalle` | Ahora incluye `rol_nombre` |

## Compatibilidad

✅ Retrocompatible con código existente
✅ No requiere migración de base de datos
✅ El campo `rol_id` sigue funcionando como antes
✅ Se agrega información adicional sin romper nada
