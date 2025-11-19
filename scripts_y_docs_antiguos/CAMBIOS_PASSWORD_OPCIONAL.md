# Cambios: Password Opcional en Actualizaciones

## Problema
Al actualizar un empleado, el sistema solicitaba obligatoriamente la contraseña, incluso si no se deseaba cambiarla.

## Solución Implementada

### 1. Backend (Django)

#### Cambios en `authentication/serializers.py`:

**Línea 47**: Campo password ahora es opcional
```python
password = serializers.CharField(write_only=True, required=False, allow_blank=True)
```

**Líneas 76-83**: Validación personalizada
```python
def validate(self, data):
    """Validación general: password es requerido solo al crear"""
    if not self.instance:  # Modo creación
        if not data.get('password'):
            raise serializers.ValidationError({
                'password': 'La contraseña es requerida al crear un empleado.'
            })
    return data
```

**Líneas 129-131**: Actualización condicional del password
```python
# Solo actualizar password si se proporciona y no está vacío
if 'password' in validated_data and validated_data['password']:
    instance.set_password(validated_data['password'])
```

### 2. Frontend (React)

#### En `frontend/src/components/EmployeeForm.js`:

**Líneas 87-92**: Eliminar password vacío antes de enviar
```javascript
if (isEditMode) {
  // En modo edición, no enviar password si está vacío
  const dataToSend = { ...formData };
  if (!dataToSend.password) {
    delete dataToSend.password;
  }
  await employeeService.updateEmployee(id, dataToSend);
}
```

**Línea 234**: Campo password muestra hint de opcional
```javascript
<label htmlFor="password">
  Contraseña {isEditMode ? '(dejar vacío para no cambiar)' : '*'}
</label>
```

**Línea 241**: Campo no es requerido en modo edición
```javascript
required={!isEditMode}
```

### 3. Tests

#### Nuevo test en `authentication/tests.py`:

**Líneas 308-373**: Test que verifica actualización sin password
```python
def test_actualizar_empleado_sin_password(self):
    """
    Test: Actualizar empleado sin enviar password (debe mantener el password actual).
    """
    # ... código que verifica que:
    # 1. Se puede actualizar sin enviar password
    # 2. El password original no cambia
    # 3. Los demás campos sí se actualizan
```

## Comportamiento Actual

### Al CREAR un empleado:
- ✅ Password es **requerido**
- ❌ No se puede crear sin password

### Al ACTUALIZAR un empleado:
- ✅ Password es **opcional**
- ✅ Si se deja vacío, mantiene el password actual
- ✅ Si se proporciona, actualiza el password
- ✅ Todos los demás campos se actualizan normalmente

## Tests Ejecutados

```bash
python manage.py test authentication.tests.EmpleadoEndpointTests
```

**Resultado**: 12 tests pasaron exitosamente ✅
- 11 tests originales
- 1 test nuevo: `test_actualizar_empleado_sin_password`

## Ejemplos de Uso

### Crear empleado (password requerido):
```json
POST /api/admin/empleados/
{
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "telefono": "5551234567",
  "email": "juan@test.com",
  "password": "password123",  // ← REQUERIDO
  "puesto": "Entrenador",
  "departamento": "Fitness",
  "fecha_contratacion": "2024-01-01",
  "tipo_contrato": "Indefinido",
  "salario": "15000.00",
  "estado": "Activo",
  "rfc": "PEGJ900515XYZ",
  "rol_id": 2
}
```

### Actualizar empleado SIN cambiar password:
```json
PUT /api/admin/empleados/1/
{
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "telefono": "5551234567",
  "email": "juan@test.com",
  // password NO se envía ← Mantiene el password actual
  "puesto": "Supervisor",  // ← Solo cambian estos campos
  "departamento": "Fitness",
  "fecha_contratacion": "2024-01-01",
  "tipo_contrato": "Indefinido",
  "salario": "18000.00",  // ← Nuevo salario
  "estado": "Activo",
  "rfc": "PEGJ900515XYZ",
  "rol_id": 2
}
```

### Actualizar empleado Y cambiar password:
```json
PUT /api/admin/empleados/1/
{
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "telefono": "5551234567",
  "email": "juan@test.com",
  "password": "nuevopassword456",  // ← Se actualiza el password
  "puesto": "Supervisor",
  "departamento": "Fitness",
  "fecha_contratacion": "2024-01-01",
  "tipo_contrato": "Indefinido",
  "salario": "18000.00",
  "estado": "Activo",
  "rfc": "PEGJ900515XYZ",
  "rol_id": 2
}
```

## Compatibilidad

✅ Retrocompatible con código existente
✅ No requiere migración de base de datos
✅ Frontend actualizado automáticamente
✅ Todos los tests pasan

## Archivos Modificados

1. `authentication/serializers.py` - Lógica de validación
2. `frontend/src/components/EmployeeForm.js` - UI y envío de datos
3. `authentication/tests.py` - Nuevo test de verificación
