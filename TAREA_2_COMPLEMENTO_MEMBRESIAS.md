# ✅ COMPLEMENTO TAREA 2: Permisos y Filtrado de Membresías para Clientes

## 🎯 Objetivo
Permitir que clientes autenticados puedan ver las membresías disponibles en su sede y suscribirse a ellas.

## 🐛 Problema Encontrado

### Error Original:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Causa**: El endpoint `/api/membresias/activas/` requería permisos de `EsAdministradorOCajero`, pero los clientes no tienen ese rol.

**Impacto**: Los clientes no podían ver las membresías disponibles para suscribirse desde la app móvil.

---

## ✅ Solución Implementada

### Cambios en `membresias/views.py` - `MembresiaViewSet`

#### 1. Permisos Personalizados (líneas 27-35)

**ANTES**:
```python
permission_classes = [EsAdministradorOCajero]
```

**DESPUÉS**:
```python
def get_permissions(self):
    """
    Permisos personalizados:
    - Clientes autenticados pueden ver membresías (list, retrieve, activas)
    - Solo admin/cajero pueden crear, actualizar, eliminar
    """
    if self.action in ['list', 'retrieve', 'activas']:
        return [IsAuthenticated()]
    return [EsAdministradorOCajero()]
```

**Ventajas**:
- ✅ Clientes autenticados pueden **ver** membresías disponibles
- ✅ Clientes autenticados pueden **ver detalles** de una membresía
- ✅ Clientes autenticados pueden ver **membresías activas**
- ✅ Solo admins/cajeros pueden **crear, actualizar, eliminar** membresías

---

#### 2. Filtrado Automático por Sede (líneas 45-61)

**ANTES**:
```python
def get_queryset(self):
    queryset = Membresia.objects.select_related('sede').prefetch_related('espacios_incluidos').all()
    # Filtros por parámetros...
```

**DESPUÉS**:
```python
def get_queryset(self):
    """
    Si el usuario es un cliente, solo muestra membresías de su sede
    o membresías que permiten todas las sedes.
    """
    queryset = Membresia.objects.select_related('sede').prefetch_related('espacios_incluidos').all()

    # Si el usuario es un cliente, filtrar por su sede
    if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
        cliente = self.request.user.persona.cliente
        # Mostrar membresías de la sede del cliente o que permiten todas las sedes
        queryset = queryset.filter(
            Q(sede_id=cliente.sede_id) | Q(permite_todas_sedes=True)
        )

    # Resto de filtros...
```

**Ventajas**:
- ✅ Clientes solo ven membresías de **su sede**
- ✅ Clientes también ven membresías **multi-sede** (`permite_todas_sedes=True`)
- ✅ Admins/cajeros ven **todas las membresías** (sin filtro)

---

#### 3. Endpoint `activas` con Filtrado (líneas 179-192)

**ANTES**:
```python
@action(detail=False, methods=['get'])
def activas(self, request):
    membresias = Membresia.objects.filter(activo=True)
    serializer = MembresiaListSerializer(membresias, many=True)
    return Response(serializer.data)
```

**DESPUÉS**:
```python
@action(detail=False, methods=['get'])
def activas(self, request):
    """
    Si el usuario es un cliente, solo muestra membresías activas
    de su sede o que permiten todas las sedes.
    """
    # Usar get_queryset() para que aplique el filtro de sede del cliente
    queryset = self.get_queryset()
    membresias = queryset.filter(activo=True)
    serializer = MembresiaListSerializer(membresias, many=True)
    return Response(serializer.data)
```

**Ventajas**:
- ✅ Usa `get_queryset()` que ya filtra por sede del cliente
- ✅ Solo muestra membresías **activas**
- ✅ Respeta el filtro multi-sede

---

## 🧪 Cómo Probar

### Prerequisitos
1. Backend Django corriendo en `http://192.168.100.7:8000`
2. Cliente registrado con token de autenticación
3. Membresías creadas en diferentes sedes

### Prueba 1: Ver Membresías Activas (Cliente)

```bash
# 1. Login como cliente
curl -X POST http://192.168.100.7:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "123456"}'

# 2. Obtener membresías activas
curl -X GET http://192.168.100.7:8000/api/membresias/activas/ \
  -H "Authorization: Bearer <TOKEN>"
```

**Respuesta esperada**: Solo membresías activas de la sede del cliente o multi-sede

```json
[
  {
    "id": 1,
    "nombre_plan": "Plan Mensual - Sede Central",
    "descripcion": "Acceso completo mensual",
    "tipo": "mensual",
    "precio": "500.00",
    "activo": true,
    "sede": 1,
    "sede_nombre": "Sede Central",
    "permite_todas_sedes": false
  },
  {
    "id": 5,
    "nombre_plan": "Plan Premium Multi-Sede",
    "descripcion": "Acceso a todas las sedes",
    "tipo": "mensual",
    "precio": "1000.00",
    "activo": true,
    "sede": 1,
    "sede_nombre": "Sede Central",
    "permite_todas_sedes": true
  }
]
```

---

### Prueba 2: Verificar Filtrado Multi-Sede

**Escenario**:
- Cliente registrado en **Sede Central (ID: 1)**
- Existen membresías en **Sede Norte (ID: 2)**
- Existe membresía **multi-sede**

**Resultado esperado**:
- ✅ Cliente ve membresías de **Sede Central**
- ✅ Cliente ve membresías **multi-sede**
- ❌ Cliente **NO ve** membresías exclusivas de **Sede Norte**

---

### Prueba 3: Intentar Crear Membresía (Cliente)

```bash
curl -X POST http://192.168.100.7:8000/api/membresias/ \
  -H "Authorization: Bearer <TOKEN_CLIENTE>" \
  -H "Content-Type: application/json" \
  -d '{"nombre_plan": "Plan Test", "precio": 500}'
```

**Respuesta esperada**:
```json
{
  "detail": "You do not have permission to perform this action."
}
```
✅ Correcto: Los clientes no pueden crear membresías

---

### Prueba 4: Admin Puede Crear Membresía

```bash
curl -X POST http://192.168.100.7:8000/api/membresias/ \
  -H "Authorization: Bearer <TOKEN_ADMIN>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Respuesta esperada**: Status 201 Created
✅ Correcto: Los admins sí pueden crear membresías

---

## 📝 Endpoints Modificados

### GET /api/membresias/ (MODIFICADO)

**Descripción**: Lista de todas las membresías (filtradas por sede del cliente)

**Autenticación**: Requerida

**Permisos**:
- Clientes: ✅ Ver membresías de su sede
- Admins: ✅ Ver todas las membresías

**Response** (Cliente en Sede Central):
```json
[
  {
    "id": 1,
    "nombre_plan": "Plan Mensual",
    "sede_id": 1,
    "sede_nombre": "Sede Central",
    "activo": true
  },
  {
    "id": 5,
    "nombre_plan": "Plan Multi-Sede",
    "sede_id": 1,
    "permite_todas_sedes": true,
    "activo": true
  }
]
```

---

### GET /api/membresias/activas/ (MODIFICADO)

**Descripción**: Lista de membresías activas (filtradas por sede del cliente)

**Autenticación**: Requerida

**Permisos**:
- Clientes: ✅ Ver membresías activas de su sede
- Admins: ✅ Ver todas las membresías activas

**Response** (Cliente en Sede Central):
```json
[
  {
    "id": 1,
    "nombre_plan": "Plan Mensual",
    "tipo": "mensual",
    "precio": "500.00",
    "activo": true,
    "sede_id": 1
  }
]
```

---

### GET /api/membresias/{id}/ (MODIFICADO)

**Descripción**: Detalle de una membresía

**Autenticación**: Requerida

**Permisos**:
- Clientes: ✅ Ver detalle si la membresía está en su sede
- Admins: ✅ Ver detalle de cualquier membresía

---

### POST /api/membresias/ (SIN CAMBIOS)

**Descripción**: Crear nueva membresía

**Permisos**: Solo `EsAdministradorOCajero`

**Autenticación**: Requerida

---

## 🎯 Flujo Completo: Cliente Suscribe a Membresía

### Paso 1: Login
```javascript
POST /api/login/
{
  "email": "cliente@test.com",
  "password": "123456"
}
```

### Paso 2: Ver Membresías Disponibles
```javascript
GET /api/membresias/activas/
Headers: { Authorization: "Bearer <TOKEN>" }
```

### Paso 3: Ver Detalle de Membresía
```javascript
GET /api/membresias/1/
Headers: { Authorization: "Bearer <TOKEN>" }
```

### Paso 4: Suscribirse a Membresía
```javascript
POST /api/suscripciones/
Headers: { Authorization: "Bearer <TOKEN>" }
Body: {
  "membresia": 1,
  "metodo_pago": "efectivo",
  "notas": "Suscripción desde app móvil"
}
```

### Paso 5: Ver Mis Suscripciones
```javascript
GET /api/suscripciones/
Headers: { Authorization: "Bearer <TOKEN>" }
```

---

## 📊 Comparación: Antes vs Ahora

### Antes
- ❌ Clientes no podían ver membresías (403 Forbidden)
- ❌ Solo admins/cajeros podían acceder a `/api/membresias/`
- ❌ Clientes veían membresías de todas las sedes (si tuvieran acceso)

### Ahora
- ✅ Clientes pueden ver membresías disponibles
- ✅ Clientes solo ven membresías de su sede o multi-sede
- ✅ Clientes pueden suscribirse a membresías
- ✅ Admins mantienen todos los permisos

---

## 🔒 Seguridad

### Validaciones Implementadas:

1. **Autenticación Requerida**: Todos los endpoints requieren token JWT
2. **Filtrado Automático**: Los clientes no pueden ver membresías de otras sedes
3. **Permisos de Escritura**: Solo admins/cajeros pueden crear/modificar membresías
4. **Validación en Suscripción**: Al crear suscripción, se valida que la membresía esté disponible en la sede del cliente

---

## ✅ Checklist de Pruebas

- [ ] Cliente puede hacer login
- [ ] Cliente puede ver membresías activas con `GET /api/membresias/activas/`
- [ ] Cliente solo ve membresías de su sede o multi-sede
- [ ] Cliente NO ve membresías de otras sedes
- [ ] Cliente puede ver detalle de membresía con `GET /api/membresias/{id}/`
- [ ] Cliente puede crear suscripción con `POST /api/suscripciones/`
- [ ] Cliente NO puede crear membresías (403 Forbidden)
- [ ] Admin puede crear membresías
- [ ] Admin puede ver todas las membresías

---

## 🔜 Siguiente Paso

Ahora que el backend está listo, el siguiente paso es **verificar que la app móvil funciona correctamente** con estos cambios.

La app móvil debería:
1. ✅ Cargar membresías activas con `GET /api/membresias/activas/`
2. ✅ Mostrar solo membresías de la sede del cliente
3. ✅ Permitir suscribirse enviando solo `membresia` y `metodo_pago`

**Prueba desde el celular** y confirma que ahora carga las membresías correctamente.
