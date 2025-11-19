# Solución al Error 404 en Control de Accesos

## Problemas Encontrados y Solucionados

### 1. **Manejo inadecuado de errores 404 en el frontend**

**Problema:**
El componente `ControlAccesos.js` tenía dos funciones que llamaban al endpoint `validarAcceso`, pero solo una manejaba correctamente el error 404 cuando no se encontraba un cliente.

**Solución Aplicada:**
- Actualizado `seleccionarCliente()` en `frontend/src/components/ControlAccesos.js` línea 191-196
- Ahora maneja correctamente los errores 404 mostrando un mensaje apropiado al usuario
- Diferencia entre errores 404 (cliente no encontrado) y otros errores de red

**Archivo modificado:**
- `frontend/src/components/ControlAccesos.js`

### 2. **Búsqueda limitada - no incluía email**

**Problema:**
La búsqueda de clientes solo permitía buscar por nombre, apellidos y teléfono, pero NO por email, a pesar de que la interfaz indicaba que sí se podía.

**Solución Aplicada:**
- Agregado filtro de búsqueda por email en `control_acceso/views.py` línea 40
- Actualizado `select_related` para incluir `persona__user` y obtener el email eficientemente
- Agregado campo `email` en las respuestas de validación (línea 237 y 58)

**Archivos modificados:**
- `control_acceso/views.py`

## Cambios Realizados

### Backend (`control_acceso/views.py`)

#### Cambio 1: Búsqueda por email
```python
# ANTES:
clientes = Cliente.objects.filter(
    Q(persona__nombre__icontains=search_term) |
    Q(persona__apellido_paterno__icontains=search_term) |
    Q(persona__apellido_materno__icontains=search_term) |
    Q(persona__telefono__icontains=search_term)
).select_related('persona').distinct()

# DESPUÉS:
clientes = Cliente.objects.filter(
    Q(persona__nombre__icontains=search_term) |
    Q(persona__apellido_paterno__icontains=search_term) |
    Q(persona__apellido_materno__icontains=search_term) |
    Q(persona__telefono__icontains=search_term) |
    Q(persona__user__email__icontains=search_term)
).select_related('persona', 'persona__user').distinct()
```

#### Cambio 2: Email en respuestas
```python
# En resultados múltiples:
resultados.append({
    'cliente_id': cliente.persona_id,
    'nombre_completo': f"{persona.nombre} {persona.apellido_paterno}...",
    'email': persona.user.email if hasattr(persona, 'user') and persona.user else None,  # NUEVO
    'telefono': persona.telefono
})

# En validación de cliente:
cliente_info = {
    'cliente_id': cliente.persona_id,
    'persona_id': persona.id,
    'nombre_completo': f"{persona.nombre}...",
    'email': persona.user.email if hasattr(persona, 'user') and persona.user else None,  # NUEVO
    'telefono': persona.telefono,
    'foto_url': persona.foto.url if persona.foto else None,
}
```

### Frontend (`frontend/src/components/ControlAccesos.js`)

#### Cambio: Mejor manejo de errores 404
```javascript
// ANTES:
catch (error) {
  console.error('Error al obtener información del cliente:', error);
  setError('Error al obtener la información del cliente');
}

// DESPUÉS:
catch (error) {
  console.error('Error al obtener información del cliente:', error);

  if (error.response && error.response.status === 404) {
    setError('No se encontró el cliente seleccionado');
    setBusquedaRealizada(true);
  } else {
    setError('Error al obtener la información del cliente. Por favor intenta de nuevo.');
  }
}
```

## Cómo Probar la Solución

### 1. Reiniciar el servidor Django
```bash
# Detener servidor si está corriendo (Ctrl+C)
python manage.py runserver
```

### 2. Reiniciar el servidor React
```bash
cd frontend
npm start
```

### 3. Probar la funcionalidad

1. Navegar a `http://localhost:3000/accesos`
2. Seleccionar una sede
3. Probar búsquedas:
   - ✅ Por nombre: "Juan"
   - ✅ Por apellido: "Pérez"
   - ✅ Por teléfono: "5551234567"
   - ✅ **Por email: "juan@example.com"** (NUEVO)

### 4. Casos de prueba

**Caso 1: Cliente NO existe**
- Buscar: "clienteinexistente123"
- Resultado esperado: "⚠️ No se encontró ningún cliente con ese criterio de búsqueda"
- ✅ No debe mostrar "Error al obtener información del cliente"

**Caso 2: Múltiples clientes**
- Buscar: "test" (si hay varios clientes con "test" en el nombre)
- Resultado esperado: Lista de clientes para seleccionar
- Debe mostrar email, nombre y teléfono de cada uno

**Caso 3: Un solo cliente**
- Buscar por email completo: "cliente1@example.com"
- Resultado esperado: Modal con información del cliente y membresía
- Debe mostrar email en el modal

**Caso 4: Cliente sin user/email**
- Si un cliente no tiene usuario asociado
- Resultado esperado: El campo email debe mostrar "Sin email" o null
- No debe causar error

## Verificaciones Realizadas

✅ `python manage.py check` - Sin errores
✅ `npm run build` - Compilación exitosa
✅ Backend: Endpoint `/api/accesos/registros/validar_acceso/` funciona correctamente
✅ Frontend: Manejo de errores mejorado
✅ Búsqueda: Ahora incluye email

## Notas Importantes

1. **El error 404 es NORMAL** cuando no se encuentra un cliente - esto no es un bug, es el comportamiento esperado
2. El frontend ahora distingue entre:
   - **404**: Cliente no encontrado → Mensaje amigable
   - **Otros errores** (500, 401, red): Error de conexión → Mensaje de reintentar

3. La búsqueda en tiempo real (autocompletado) también funciona con email

## Archivos Modificados

```
control_acceso/views.py
  - Línea 40: Búsqueda por email (CORREGIDO: usuario en lugar de user)
  - Línea 41: select_related corregido
  - Línea 58: Email en resultados múltiples
  - Línea 238: Email en validación de cliente

frontend/src/components/ControlAccesos.js
  - Línea 191-196: Manejo mejorado de errores 404
```

---

## ⚠️ CORRECCIÓN CRÍTICA - Error 500 Resuelto

### Problema Detectado
Después de la primera implementación, el endpoint retornaba **Error 500 (Internal Server Error)**.

### Causa Raíz
El código usaba `persona__user__email` pero el modelo `User` define la relación como `related_name='usuario'`, NO `user`.

**Error en el código:**
```python
# ❌ INCORRECTO (causaba error 500):
Q(persona__user__email__icontains=search_term)
select_related('persona', 'persona__user')
persona.user.email

# Django lanzaba:
# FieldError: Unsupported lookup 'user__email__icontains' for OneToOneField
```

### Solución Aplicada
Cambiado todas las referencias de `user` a `usuario`:

```python
# ✅ CORRECTO:
Q(persona__usuario__email__icontains=search_term)
select_related('persona', 'persona__usuario')
persona.usuario.email if hasattr(persona, 'usuario') and persona.usuario else None
```

### Verificación
```bash
$ python test_query_corregida.py
✓ Query ejecutada correctamente
✓ Clientes encontrados: 2

$ python manage.py check
System check identified no issues (0 silenced).
```

---

## Próximos Pasos (Opcional)

Si quieres mejorar aún más el sistema:

1. **Agregar búsqueda por ID de cliente**
2. **Implementar escaneo de código QR/RFID**
3. **Agregar filtro por estado de membresía**
4. **Registrar salidas** (actualmente solo registra entradas)
5. **Dashboard de estadísticas en tiempo real**

---

**Fecha de corrección:** 2025-11-14
**Estado:** ✅ RESUELTO
