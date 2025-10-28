# API Endpoints - Gestión de Equipos y Mantenimiento

Base URL: `http://localhost:8000/api/gestion-equipos/`

## 📦 CATEGORÍAS DE ACTIVOS

### Endpoints básicos
- `GET /categorias-activo/` - Listar todas las categorías
- `POST /categorias-activo/` - Crear nueva categoría
- `GET /categorias-activo/{id}/` - Obtener detalle de categoría
- `PUT /categorias-activo/{id}/` - Actualizar categoría
- `PATCH /categorias-activo/{id}/` - Actualizar parcialmente categoría
- `DELETE /categorias-activo/{id}/` - Eliminar categoría

### Endpoints personalizados
- `GET /categorias-activo/activas/` - Obtener solo categorías activas
- `POST /categorias-activo/{id}/toggle_activo/` - Activar/desactivar categoría

### Filtros disponibles
- `?activo=true` - Filtrar por estado activo
- `?search=cardiovascular` - Búsqueda por nombre o descripción

---

## 🏢 PROVEEDORES DE SERVICIO

### Endpoints básicos
- `GET /proveedores/` - Listar todos los proveedores
- `POST /proveedores/` - Crear nuevo proveedor
- `GET /proveedores/{id}/` - Obtener detalle de proveedor
- `PUT /proveedores/{id}/` - Actualizar proveedor
- `PATCH /proveedores/{id}/` - Actualizar parcialmente proveedor
- `DELETE /proveedores/{id}/` - Eliminar proveedor

### Endpoints personalizados
- `GET /proveedores/activos/` - Obtener solo proveedores activos
- `POST /proveedores/{id}/toggle_activo/` - Activar/desactivar proveedor
- `GET /proveedores/{id}/mantenimientos/` - Mantenimientos del proveedor
- `GET /proveedores/estadisticas/` - Estadísticas de proveedores

### Filtros disponibles
- `?activo=true` - Filtrar por estado activo
- `?search=technogym` - Búsqueda por nombre, contacto, teléfono o email

---

## 🏋️ ACTIVOS

### Endpoints básicos
- `GET /activos/` - Listar todos los activos
- `POST /activos/` - Crear nuevo activo
- `GET /activos/{id}/` - Obtener detalle de activo
- `PUT /activos/{id}/` - Actualizar activo
- `PATCH /activos/{id}/` - Actualizar parcialmente activo
- `DELETE /activos/{id}/` - Eliminar activo

### Endpoints personalizados
- `GET /activos/por_estado/?estado=activo` - Activos por estado
- `GET /activos/por_sede/?sede_id=1` - Activos de una sede
- `POST /activos/{id}/cambiar_estado/` - Cambiar estado del activo
  - Body: `{"estado": "mantenimiento"}`
- `GET /activos/{id}/historial_mantenimiento/` - Historial de mantenimientos
- `GET /activos/proximos_mantenimientos/` - Activos con mantenimientos próximos (15 días)
- `GET /activos/estadisticas/` - Estadísticas generales de activos

### Filtros disponibles
- `?categoria=1` - Filtrar por categoría
- `?estado=activo` - Filtrar por estado (activo, mantenimiento, baja, inactivo)
- `?sede=1` - Filtrar por sede
- `?espacio=1` - Filtrar por espacio
- `?search=caminadora` - Búsqueda por código, nombre, marca, modelo o número de serie

### Respuesta de estadísticas
```json
{
  "total_activos": 10,
  "por_estado": {
    "activo": 9,
    "mantenimiento": 1
  },
  "por_categoria": {
    "Máquinas Cardiovasculares": 3,
    "Máquinas de Fuerza": 3
  },
  "valor_total": 615499.00,
  "valor_promedio": 61549.90,
  "alertas_mantenimiento": 2
}
```

---

## 🔧 MANTENIMIENTOS

### Endpoints básicos
- `GET /mantenimientos/` - Listar todos los mantenimientos
- `POST /mantenimientos/` - Crear nuevo mantenimiento
- `GET /mantenimientos/{id}/` - Obtener detalle de mantenimiento
- `PUT /mantenimientos/{id}/` - Actualizar mantenimiento
- `PATCH /mantenimientos/{id}/` - Actualizar parcialmente
- `DELETE /mantenimientos/{id}/` - Eliminar mantenimiento

### Endpoints personalizados
- `GET /mantenimientos/pendientes/` - Mantenimientos pendientes
- `GET /mantenimientos/en_proceso/` - Mantenimientos en proceso
- `GET /mantenimientos/alertas/` - Mantenimientos que requieren atención (próximos 15 días)
- `GET /mantenimientos/vencidos/` - Mantenimientos vencidos (fecha pasada y aún pendientes)
- `POST /mantenimientos/{id}/iniciar/` - Cambiar estado a "en_proceso"
- `POST /mantenimientos/{id}/completar/` - Completar mantenimiento
  - Body: `{"fecha_ejecucion": "2025-10-21", "observaciones": "...", "costo": 2500}`
- `POST /mantenimientos/{id}/cancelar/` - Cancelar mantenimiento
  - Body: `{"motivo": "Cliente solicitó cancelación"}`
- `GET /mantenimientos/estadisticas/` - Estadísticas de mantenimientos
- `GET /mantenimientos/por_activo/?activo_id=1` - Mantenimientos de un activo

### Filtros disponibles
- `?tipo_mantenimiento=preventivo` - Filtrar por tipo (preventivo, correctivo)
- `?estado=pendiente` - Filtrar por estado (pendiente, en_proceso, completado, cancelado)
- `?activo=1` - Filtrar por activo
- `?proveedor_servicio=1` - Filtrar por proveedor
- `?empleado_responsable=1` - Filtrar por empleado
- `?search=lubricación` - Búsqueda por código de activo, nombre o descripción

### Respuesta de estadísticas
```json
{
  "total_mantenimientos": 9,
  "por_estado": {
    "pendiente": 5,
    "en_proceso": 1,
    "completado": 3
  },
  "por_tipo": {
    "preventivo": 8,
    "correctivo": 1
  },
  "costo_total": 5100.00,
  "costo_promedio": 1700.00,
  "alertas": 2,
  "vencidos": 1
}
```

---

## 📋 ÓRDENES DE MANTENIMIENTO

### Endpoints básicos
- `GET /ordenes/` - Listar todas las órdenes
- `POST /ordenes/` - Crear nueva orden (genera número automático)
- `GET /ordenes/{id}/` - Obtener detalle de orden
- `PUT /ordenes/{id}/` - Actualizar orden
- `PATCH /ordenes/{id}/` - Actualizar parcialmente
- `DELETE /ordenes/{id}/` - Eliminar orden

### Endpoints personalizados
- `GET /ordenes/por_prioridad/?prioridad=urgente` - Órdenes por prioridad
- `GET /ordenes/urgentes/` - Órdenes urgentes y de alta prioridad
- `POST /ordenes/{id}/cambiar_estado/` - Cambiar estado de la orden
  - Body: `{"estado_orden": "en_ejecucion"}`
- `GET /ordenes/estadisticas/` - Estadísticas de órdenes

### Filtros disponibles
- `?prioridad=urgente` - Filtrar por prioridad (baja, media, alta, urgente)
- `?estado_orden=aprobada` - Filtrar por estado (creada, aprobada, en_ejecucion, finalizada, cancelada)
- `?mantenimiento=1` - Filtrar por mantenimiento
- `?search=OM-2025` - Búsqueda por número de orden, código o nombre de activo

### Formato de número de orden
Las órdenes se generan automáticamente con el formato: `OM-{AÑO}-{CONSECUTIVO}`
Ejemplo: `OM-2025-0001`, `OM-2025-0002`, etc.

---

## 🔔 ALERTAS Y NOTIFICACIONES

### Mantenimientos que requieren atención
- **Alertas (próximos 15 días)**: `GET /mantenimientos/alertas/`
- **Vencidos**: `GET /mantenimientos/vencidos/`
- **Próximos mantenimientos**: `GET /activos/proximos_mantenimientos/`

### Propiedades calculadas en respuestas

#### Mantenimiento
- `dias_para_mantenimiento`: Días restantes hasta el mantenimiento
- `requiere_atencion`: Boolean si está en ventana de 15 días

#### Activo
- `en_mantenimiento`: Boolean si tiene mantenimientos pendientes/en proceso
- `proximo_mantenimiento`: Objeto con información del siguiente mantenimiento

---

## 📊 ESTADÍSTICAS DISPONIBLES

### Activos
`GET /activos/estadisticas/`
- Total de activos
- Distribución por estado
- Distribución por categoría
- Valor total de activos
- Valor promedio
- Alertas de mantenimiento

### Mantenimientos
`GET /mantenimientos/estadisticas/`
- Total de mantenimientos
- Distribución por estado
- Distribución por tipo
- Costo total
- Costo promedio
- Alertas
- Vencidos

### Proveedores
`GET /proveedores/estadisticas/`
- Total de proveedores
- Proveedores activos
- Proveedores inactivos

### Órdenes
`GET /ordenes/estadisticas/`
- Total de órdenes
- Distribución por estado
- Distribución por prioridad
- Tiempo promedio estimado

---

## 🔐 AUTENTICACIÓN

Todos los endpoints requieren autenticación JWT.

Headers requeridos:
```
Authorization: Bearer {token}
```

---

## 📝 VALIDACIONES IMPLEMENTADAS

### Activo
- Código único (case-insensitive)
- Número de serie único
- Espacio debe pertenecer a la sede seleccionada
- Fecha de compra no puede ser futura
- Valor debe ser positivo

### Mantenimiento
- Debe tener al menos un responsable (proveedor o empleado)
- Fecha de ejecución no puede ser anterior a fecha programada
- No puede haber múltiples mantenimientos en proceso para el mismo activo
- Al poner mantenimiento en proceso, el activo cambia a estado "mantenimiento"
- Al completar mantenimiento, el activo vuelve a "activo" si no hay otros en proceso

### Orden de Mantenimiento
- Número de orden se genera automáticamente
- Un mantenimiento solo puede tener una orden
- Prioridad se puede asignar manualmente

### Proveedor
- Teléfono debe tener 10 dígitos
- Email debe ser válido

### Categoría
- Nombre único (case-insensitive)

---

## 💡 CASOS DE USO COMUNES

### 1. Crear un activo nuevo
```bash
POST /activos/
{
  "codigo": "CARDIO-004",
  "nombre": "Bicicleta Reclinada",
  "categoria": 1,
  "fecha_compra": "2025-10-15",
  "valor": 45000.00,
  "estado": "activo",
  "sede": 1,
  "marca": "Matrix",
  "modelo": "R50"
}
```

### 2. Programar mantenimiento preventivo
```bash
POST /mantenimientos/
{
  "activo": 1,
  "tipo_mantenimiento": "preventivo",
  "fecha_programada": "2025-11-15",
  "proveedor_servicio": 1,
  "costo": 2500.00,
  "descripcion": "Mantenimiento trimestral"
}
```

### 3. Crear orden de trabajo
```bash
POST /ordenes/
{
  "mantenimiento": 1,
  "prioridad": "alta",
  "tiempo_estimado": 3.5,
  "materiales_necesarios": "Lubricantes, kit de limpieza"
}
```

### 4. Completar mantenimiento
```bash
POST /mantenimientos/1/completar/
{
  "fecha_ejecucion": "2025-10-21",
  "observaciones": "Equipo funcionando correctamente",
  "costo": 2500.00
}
```

### 5. Consultar alertas
```bash
GET /mantenimientos/alertas/
# Retorna mantenimientos próximos en 15 días

GET /mantenimientos/vencidos/
# Retorna mantenimientos con fecha pasada
```

---

## 🎯 PRÓXIMOS PASOS PARA FRONTEND

1. **Dashboard de Mantenimiento**
   - Cards con estadísticas principales
   - Alertas visuales
   - Calendario de mantenimientos

2. **Gestión de Activos**
   - Lista con filtros
   - Formulario de creación/edición
   - Vista de detalle con historial

3. **Gestión de Mantenimientos**
   - Lista con estados y alertas
   - Formulario con selección de activo y responsable
   - Acciones rápidas (iniciar, completar, cancelar)

4. **Órdenes de Trabajo**
   - Lista priorizada
   - Vista de detalle
   - Cambio de estados

5. **Proveedores**
   - Lista con contactos
   - Historial de servicios

6. **Reportes**
   - Costos de mantenimiento por período
   - Activos más costosos de mantener
   - Proveedores más utilizados
