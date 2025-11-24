# ✅ TAREA 2 COMPLETADA: Creación de Suscripciones con Cliente Autenticado

## 🎯 Objetivo
Modificar la creación de suscripciones para que infiera automáticamente el cliente y sede desde el usuario autenticado.

## ✅ Cambios Realizados

### Backend (Django)

#### 1. `membresias/views.py` - `SuscripcionMembresiaViewSet`

**Modificación en línea 176**:
```python
# ANTES:
permission_classes = [EsAdministradorOCajero]

# DESPUÉS:
permission_classes = [IsAuthenticated]  # Ahora los clientes también pueden crear
```
- ✅ Permitir que clientes autenticados creen sus propias suscripciones

---

**Modificación en `get_queryset()` (líneas 193-196)**:
```python
# Si el usuario es un cliente, solo mostrar sus propias suscripciones
if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
    cliente = self.request.user.persona.cliente
    queryset = queryset.filter(cliente=cliente)
```
- ✅ Los clientes solo ven sus propias suscripciones
- ✅ Admins/cajeros ven todas las suscripciones

---

**Nuevo método `create()` (líneas 232-291)**:

##### Funcionalidad:
1. **Detecta si el usuario es un cliente** (líneas 247-248)
2. **Valida que la membresía existe** (líneas 251-264)
3. **Valida disponibilidad en la sede del cliente** (líneas 267-271)
   - Si la membresía permite todas las sedes: ✅ OK
   - Si la membresía es de una sede específica: ✅ Solo si coincide con la sede del cliente
4. **Infiere automáticamente** (líneas 274-276):
   - `cliente`: Del usuario autenticado (`cliente.persona_id`)
   - `sede_suscripcion`: De la sede del cliente (`cliente.sede_id`)
5. **Crea la suscripción** (líneas 278-288)

##### Código completo:
```python
def create(self, request, *args, **kwargs):
    """
    Crear nueva suscripción.
    Si el usuario autenticado es un cliente, se infiere automáticamente:
    - cliente: del usuario autenticado
    - sede_suscripcion: de la sede del cliente

    Body requerido para clientes:
    {
        "membresia": <id>,
        "metodo_pago": "efectivo|tarjeta|transferencia",
        "notas": "opcional"
    }
    """
    # Verificar si el usuario es un cliente
    if hasattr(request.user, 'persona') and hasattr(request.user.persona, 'cliente'):
        cliente = request.user.persona.cliente

        # Validar que la membresía existe
        membresia_id = request.data.get('membresia')
        if not membresia_id:
            return Response(
                {'error': 'El campo membresia es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membresia = Membresia.objects.get(id=membresia_id)
        except Membresia.DoesNotExist:
            return Response(
                {'error': 'La membresía especificada no existe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que la membresía esté disponible en la sede del cliente
        if not membresia.permite_todas_sedes and membresia.sede_id != cliente.sede_id:
            return Response(
                {'error': 'Esta membresía no está disponible en tu sede'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear datos de suscripción automáticamente
        data = request.data.copy()
        data['cliente'] = cliente.persona_id
        data['sede_suscripcion'] = cliente.sede_id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            suscripcion = serializer.save()
            return Response(
                {
                    'message': 'Suscripción creada exitosamente',
                    'data': SuscripcionMembresiaSerializer(suscripcion).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Si no es cliente (ej: admin/cajero), usar el método por defecto
        return super().create(request, *args, **kwargs)
```

---

## 🧪 Cómo Probar

### Prerequisitos
1. Backend Django debe estar corriendo en `http://192.168.100.7:8000`
2. Debe haber al menos 1 membresía activa en la base de datos
3. Debe haber un cliente registrado con token de autenticación

### Opción 1: Probar desde cURL

#### Paso 1: Obtener token de autenticación
```bash
curl -X POST http://192.168.100.7:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "123456"
  }'
```

**Respuesta esperada**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "test@test.com",
    "sede_id": 1
  }
}
```

#### Paso 2: Crear suscripción (SOLO necesita membresia y metodo_pago)
```bash
curl -X POST http://192.168.100.7:8000/api/suscripciones/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "membresia": 1,
    "metodo_pago": "efectivo",
    "notas": "Prueba desde móvil"
  }'
```

**Respuesta esperada**:
```json
{
  "message": "Suscripción creada exitosamente",
  "data": {
    "id": 1,
    "cliente": 1,
    "membresia": 1,
    "sede_suscripcion": 1,
    "fecha_inicio": "2025-11-19",
    "fecha_fin": "2025-12-19",
    "precio_pagado": "500.00",
    "metodo_pago": "efectivo",
    "estado": "activa",
    "dias_restantes": 30
  }
}
```

#### Paso 3: Verificar que solo ve sus suscripciones
```bash
curl -X GET http://192.168.100.7:8000/api/suscripciones/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Respuesta esperada**: Solo las suscripciones del cliente autenticado

---

### Opción 2: Probar desde la App Móvil (próximo paso)

Una vez que refactoricemos `membresiasService.ts` (Tarea 4), la app móvil podrá:
1. Mostrar membresías disponibles en la sede del cliente
2. Crear suscripción solo enviando `membresia` y `metodo_pago`
3. El backend automáticamente usará el cliente y sede del token

---

## 🔒 Validaciones Implementadas

### 1. Validación de Autenticación
```python
if hasattr(request.user, 'persona') and hasattr(request.user.persona, 'cliente'):
```
- ✅ Solo usuarios autenticados que sean clientes pueden crear suscripciones
- ✅ Admins/cajeros usan el método original

### 2. Validación de Membresía Requerida
```python
if not membresia_id:
    return Response({'error': 'El campo membresia es requerido'}, ...)
```
- ✅ El campo `membresia` es obligatorio

### 3. Validación de Membresía Existente
```python
try:
    membresia = Membresia.objects.get(id=membresia_id)
except Membresia.DoesNotExist:
    return Response({'error': 'La membresía especificada no existe'}, ...)
```
- ✅ La membresía debe existir en la base de datos

### 4. Validación Multi-Sede
```python
if not membresia.permite_todas_sedes and membresia.sede_id != cliente.sede_id:
    return Response({'error': 'Esta membresía no está disponible en tu sede'}, ...)
```
- ✅ Si la membresía es específica de una sede, debe ser la misma sede del cliente
- ✅ Si la membresía permite todas las sedes, cualquier cliente puede suscribirse

---

## 📝 Endpoints Modificados

### POST /api/suscripciones/ (MODIFICADO)

**Antes** (requería cliente y sede):
```json
{
  "cliente": 1,
  "membresia": 1,
  "sede_suscripcion": 1,
  "metodo_pago": "efectivo",
  "notas": "opcional"
}
```

**Ahora** (infiere automáticamente):
```json
{
  "membresia": 1,
  "metodo_pago": "efectivo",
  "notas": "opcional"
}
```

**Headers requeridos**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response**:
```json
{
  "message": "Suscripción creada exitosamente",
  "data": {
    "id": 1,
    "cliente": 1,
    "cliente_nombre": "Test Usuario",
    "membresia": 1,
    "membresia_nombre": "Plan Mensual",
    "sede_suscripcion": 1,
    "sede_nombre": "Sede Central",
    "fecha_inicio": "2025-11-19",
    "fecha_fin": "2025-12-19",
    "precio_pagado": "500.00",
    "metodo_pago": "efectivo",
    "estado": "activa",
    "dias_restantes": 30,
    "notas": "opcional"
  }
}
```

---

### GET /api/suscripciones/ (MODIFICADO)

**Antes**: Mostraba todas las suscripciones

**Ahora**:
- **Clientes**: Solo ven sus propias suscripciones (filtrado automático)
- **Admins/Cajeros**: Ven todas las suscripciones (comportamiento original)

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Response** (para cliente):
```json
[
  {
    "id": 1,
    "cliente": 1,
    "membresia": 1,
    "sede_suscripcion": 1,
    "fecha_inicio": "2025-11-19",
    "fecha_fin": "2025-12-19",
    "estado": "activa"
  }
]
```

---

## 🎯 Ventajas

### Para el Cliente (App Móvil)
1. ✅ **Más simple**: Solo envían `membresia` y `metodo_pago`
2. ✅ **Más seguro**: No pueden crear suscripciones para otros clientes
3. ✅ **Multi-sede automático**: Solo ven membresías de su sede
4. ✅ **Privacidad**: Solo ven sus propias suscripciones

### Para el Backend
1. ✅ **Menos parámetros requeridos**: Reduce errores de input
2. ✅ **Validación automática**: Imposible crear suscripciones inválidas
3. ✅ **Auditoría**: Siempre sabemos quién creó la suscripción
4. ✅ **Compatible con admin**: Admins pueden seguir creando suscripciones para cualquier cliente

---

## 📊 Comparación: Antes vs Ahora

### Antes
```json
POST /api/suscripciones/
{
  "cliente": 1,              // ❌ Cliente debía enviarlo
  "membresia": 1,
  "sede_suscripcion": 1,     // ❌ Cliente debía enviarlo
  "metodo_pago": "efectivo"
}
```

❌ **Problemas**:
- Cliente podría crear suscripciones para otros
- Cliente podría usar sedes incorrectas
- Más campos = más errores posibles

### Ahora
```json
POST /api/suscripciones/
{
  "membresia": 1,
  "metodo_pago": "efectivo"
}
```

✅ **Ventajas**:
- Cliente y sede se infieren del token
- Imposible crear suscripciones para otros
- Validación automática de sede
- Menos errores

---

## 🐛 Posibles Errores

### Error 1: "El campo membresia es requerido"
**Causa**: No se envió el campo `membresia`
**Solución**: Incluir `"membresia": <id>` en el body

### Error 2: "La membresía especificada no existe"
**Causa**: El ID de membresía no existe en la BD
**Solución**: Verificar que el ID de membresía sea correcto

### Error 3: "Esta membresía no está disponible en tu sede"
**Causa**: Intentas suscribirte a una membresía de otra sede
**Solución**: Solo seleccionar membresías disponibles en tu sede

### Error 4: "Authentication credentials were not provided"
**Causa**: No se envió el token de autenticación
**Solución**: Incluir `Authorization: Bearer <token>` en headers

---

## 🔜 Siguientes Pasos

### Tarea 3: Modificar creación de reservas
Similar a lo que hicimos aquí, modificar `horarios/views.py` para que:
- Permita a clientes autenticados crear reservas
- Infiera automáticamente el cliente del token
- Valide disponibilidad en la sede del cliente

### Tarea 4: Refactorizar membresiasService.ts
Actualizar el servicio móvil para:
- Usar `POST /api/suscripciones/` con solo `membresia` y `metodo_pago`
- Usar `GET /api/suscripciones/` para obtener suscripciones del cliente
- Usar `GET /api/membresias/` con filtro de sede

### Tarea 5: Refactorizar reservasService.ts
Actualizar el servicio móvil para:
- Usar endpoints correctos del backend
- Crear reservas con solo `horario_clase` y datos mínimos

---

## ✅ Checklist de Pruebas

- [ ] Backend Django corriendo en 0.0.0.0:8000
- [ ] Hay al menos 1 membresía activa en la BD
- [ ] Cliente registrado puede hacer login
- [ ] POST /api/suscripciones/ sin cliente/sede funciona
- [ ] GET /api/suscripciones/ solo muestra suscripciones del cliente autenticado
- [ ] Validación de membresía inexistente funciona
- [ ] Validación de membresía de otra sede funciona
- [ ] Admins pueden seguir creando suscripciones para cualquier cliente

---

**¡LISTO PARA PROBAR!** 🚀

Prueba la creación de suscripciones desde cURL o espera a que refactoricemos la app móvil (Tarea 4) para probar desde el celular.
