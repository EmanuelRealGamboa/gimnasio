# 📘 Guía Completa del Panel de Gestión de Mantenimientos

## Fecha: 23 de Octubre de 2025

---

## 📋 ÍNDICE

1. [Introducción](#introducción)
2. [Acceso al Panel](#acceso-al-panel)
3. [Interfaz del Panel](#interfaz-del-panel)
4. [Filtros y Búsqueda](#filtros-y-búsqueda)
5. [Estados de Mantenimiento](#estados-de-mantenimiento)
6. [Tipos de Mantenimiento](#tipos-de-mantenimiento)
7. [Flujo de Trabajo](#flujo-de-trabajo)
8. [Acciones Disponibles](#acciones-disponibles)
9. [Indicadores Visuales](#indicadores-visuales)
10. [Casos de Uso](#casos-de-uso)

---

## 🎯 INTRODUCCIÓN

El Panel de Gestión de Mantenimientos es una herramienta completa para programar, ejecutar y dar seguimiento a los mantenimientos de todos los equipos del gimnasio.

### Características Principales

✅ **Visualización en Cards**: Diseño moderno con toda la información relevante
✅ **Filtros Avanzados**: Búsqueda por texto, tipo, estado y filtros especiales
✅ **Indicadores de Urgencia**: Sistema de alertas para mantenimientos vencidos
✅ **Flujo de Estados**: Control del ciclo de vida del mantenimiento
✅ **Acciones Rápidas**: Botones contextuales según el estado

---

## 🚪 ACCESO AL PANEL

### Desde el Dashboard Principal

1. Click en el menú lateral: **"Equipos y Mantenimiento"**
2. En el Dashboard de Gestión de Equipos, sección **"Accesos Rápidos"**
3. Click en la card **"Mantenimientos"**

### Desde Notificaciones

- Click en las notificaciones de mantenimientos vencidos (🚨)
- Click en las notificaciones de mantenimientos próximos (⚠️)
- Te redirige automáticamente con el filtro aplicado

---

## 🖥️ INTERFAZ DEL PANEL

### Header del Panel

```
┌──────────────────────────────────────────────────────────┐
│  Gestión de Mantenimientos        [+ Nuevo Mantenimiento]│
│  Programación y seguimiento de mantenimientos...         │
└──────────────────────────────────────────────────────────┘
```

**Elementos:**
- **Título**: "Gestión de Mantenimientos"
- **Subtítulo**: Cambia según el filtro activo
- **Botón Principal**: "+ Nuevo Mantenimiento" (siempre visible)

### Sección de Filtros

```
┌──────────────────────────────────────────────────────────┐
│  🔍 Buscar por activo o descripción...                   │
├────────────────┬─────────────────┬──────────────────────┤
│ 🏷️ Tipo        │ 🔄 Estado       │ ⚡ Filtros Especiales│
│ [Todos    ▼]  │ [Todos     ▼]  │ [Ninguno        ▼]  │
│                │                 │ ✕ Limpiar filtros    │
└────────────────┴─────────────────┴──────────────────────┘
```

### Cards de Mantenimientos

Cada mantenimiento se muestra en una card con:

```
┌─────────────────────────────────────────────────┐
│ 🛡️ PREVENTIVO              ⏳ Pendiente       │
├─────────────────────────────────────────────────┤
│ 📦  CARDIO-001                                  │
│     Caminadora TechnoGym                        │
├─────────────────────────────────────────────────┤
│ 📅 Fecha Programada: 25 oct 2025                │
│ 👤 Responsable: Juan Pérez                      │
│ 💵 Costo: $1,500.00                             │
│ ⚠️ En 2 días                                    │
├─────────────────────────────────────────────────┤
│ [👁️ Ver Detalles] [▶️ Iniciar] [✏️ Editar]    │
│ [❌ Cancelar] [🗑️ Eliminar]                     │
└─────────────────────────────────────────────────┘
```

---

## 🔍 FILTROS Y BÚSQUEDA

### 1. Búsqueda por Texto

**Campo**: 🔍 Buscar por activo o descripción...

**Busca en:**
- Código del activo (ej: "CARDIO-001")
- Nombre del activo (ej: "Caminadora")
- Descripción del mantenimiento
- Marca y modelo del equipo

**Ejemplos:**
```
"CARDIO"       → Encuentra todos los mantenimientos de equipos cardiovasculares
"Caminadora"   → Encuentra mantenimientos de caminadoras
"TechnoGym"    → Encuentra mantenimientos de equipos TechnoGym
```

**Características:**
- ✅ Búsqueda en tiempo real
- ✅ No distingue mayúsculas/minúsculas
- ✅ Busca coincidencias parciales

### 2. Filtro por Tipo

**Opciones:**
```
📁 Todos los tipos
🛡️ Preventivo
🔧 Correctivo
```

**Cuándo usar:**

**Preventivo** (🛡️):
- Mantenimientos programados regularmente
- Revisiones de rutina
- Cambios de consumibles programados
- Lubricación y limpieza profunda

**Correctivo** (🔧):
- Reparaciones por fallas
- Reemplazo de piezas dañadas
- Solución de problemas reportados
- Mantenimientos de emergencia

### 3. Filtro por Estado

**Opciones:**
```
🔄 Todos los estados
⏳ Pendiente
🔄 En Proceso
✅ Completado
❌ Cancelado
```

**Descripción de cada estado:**

| Estado | Icono | Descripción | Color |
|--------|-------|-------------|-------|
| Pendiente | ⏳ | Programado pero no iniciado | Naranja (#f59e0b) |
| En Proceso | 🔄 | Actualmente en ejecución | Azul (#3b82f6) |
| Completado | ✅ | Finalizado exitosamente | Verde (#10b981) |
| Cancelado | ❌ | No se realizará | Gris (#6b7280) |

### 4. Filtros Especiales

**Opciones:**
```
⚡ Ninguno
⚠️ Próximos (15 días)
🚨 Vencidos
```

**Próximos (15 días)** ⚠️:
- Muestra mantenimientos programados para los próximos 15 días
- Útil para planificación semanal/quincenal
- Te permite preparar recursos y personal

**Vencidos** 🚨:
- Muestra mantenimientos con fecha pasada
- Requieren atención **inmediata**
- Pueden afectar la disponibilidad de equipos

**Importante**:
- Los filtros especiales **sobreescriben** el filtro de estado
- Al seleccionar un estado, se limpia el filtro especial automáticamente

### 5. Limpiar Filtros

**Botón**: ✕ Limpiar filtros

**Acción**: Restaura todos los filtros a su valor por defecto
```
Búsqueda: (vacío)
Tipo: Todos los tipos
Estado: Todos los estados
Filtro Especial: Ninguno
```

---

## 🔄 ESTADOS DE MANTENIMIENTO

### Ciclo de Vida de un Mantenimiento

```
┌──────────────┐
│  PENDIENTE   │ ← Creación inicial
└──────┬───────┘
       │ [Iniciar]
       ↓
┌──────────────┐
│  EN PROCESO  │ ← Trabajo en ejecución
└──────┬───────┘
       │ [Completar]
       ↓
┌──────────────┐
│  COMPLETADO  │ ← Finalizado
└──────────────┘

En cualquier momento:
  ↓ [Cancelar]
┌──────────────┐
│  CANCELADO   │ ← No se realizará
└──────────────┘
```

### Estado: PENDIENTE ⏳

**Descripción**: El mantenimiento está programado pero no ha comenzado.

**Acciones Disponibles:**
- ▶️ **Iniciar**: Cambia el estado a "En Proceso"
- ✏️ **Editar**: Modificar fecha, responsable, costo, etc.
- ❌ **Cancelar**: Cancelar el mantenimiento
- 🗑️ **Eliminar**: Borrar permanentemente

**Indicadores:**
- Muestra días restantes hasta la fecha programada
- Si está vencido, muestra días de retraso en rojo
- Si es hoy, muestra "Hoy" en naranja
- Si faltan 7 días o menos, muestra advertencia

**Ejemplo de Card:**
```
┌─────────────────────────────────────────┐
│ 🛡️ PREVENTIVO       ⏳ Pendiente      │
│                                         │
│ 📦 CARDIO-001 - Caminadora              │
│ 📅 25 oct 2025                          │
│ 💵 $1,500.00                            │
│ ⚠️ En 2 días                            │
│                                         │
│ [👁️][▶️][✏️][❌][🗑️]                   │
└─────────────────────────────────────────┘
```

### Estado: EN PROCESO 🔄

**Descripción**: El mantenimiento está siendo ejecutado actualmente.

**Acciones Disponibles:**
- ✅ **Completar**: Finalizar el mantenimiento (pide datos)
- ❌ **Cancelar**: Cancelar el trabajo en curso
- 🗑️ **Eliminar**: Borrar permanentemente

**Información Adicional:**
- Ya no se puede editar la programación
- El activo puede estar marcado como "En Mantenimiento"
- Se registra la fecha de inicio automáticamente

**Datos Requeridos al Completar:**
1. **Fecha de Ejecución**: Fecha real de finalización
2. **Observaciones**: Descripción del trabajo realizado
3. **Costo** (opcional): Costo final si cambió

**Ejemplo de Card:**
```
┌─────────────────────────────────────────┐
│ 🔧 CORRECTIVO       🔄 En Proceso     │
│                                         │
│ 📦 ELEC-001 - Elíptica                  │
│ 📅 Programado: 20 oct 2025              │
│ 👤 Técnico Externo                      │
│ 💵 $2,500.00                            │
│                                         │
│ [👁️][✅][❌][🗑️]                       │
└─────────────────────────────────────────┘
```

### Estado: COMPLETADO ✅

**Descripción**: El mantenimiento finalizó exitosamente.

**Acciones Disponibles:**
- 👁️ **Ver Detalles**: Ver información completa
- 🗑️ **Eliminar**: Borrar registro (con precaución)

**Información Registrada:**
- Fecha programada (original)
- Fecha de ejecución (real)
- Observaciones del trabajo realizado
- Costo final
- Responsable que ejecutó

**Ejemplo de Card:**
```
┌─────────────────────────────────────────┐
│ 🛡️ PREVENTIVO       ✅ Completado    │
│                                         │
│ 📦 CARDIO-002 - Bicicleta               │
│ 📅 Programado: 18 oct 2025              │
│ ✓ Ejecutado: 18 oct 2025                │
│ 👤 Juan Pérez                           │
│ 💵 $800.00                              │
│                                         │
│ [👁️][🗑️]                               │
└─────────────────────────────────────────┘
```

### Estado: CANCELADO ❌

**Descripción**: El mantenimiento fue cancelado y no se realizará.

**Acciones Disponibles:**
- 👁️ **Ver Detalles**: Ver motivo de cancelación
- 🗑️ **Eliminar**: Borrar registro

**Información Registrada:**
- Motivo de cancelación
- Fecha de cancelación
- Usuario que canceló

**Razones Comunes de Cancelación:**
- Equipo dado de baja
- Mantenimiento no necesario
- Cambio de programación
- Equipo vendido o retirado

---

## 🛠️ TIPOS DE MANTENIMIENTO

### Mantenimiento PREVENTIVO 🛡️

**Objetivo**: Prevenir fallas y mantener el equipo en óptimas condiciones.

**Características:**
- Se programa **regularmente** (ej: cada 30, 60, 90 días)
- Se ejecuta **antes** de que haya problemas
- Es **predecible** y se puede planificar
- **Reduce** la probabilidad de fallas

**Ejemplos de Tareas:**

#### Equipos Cardiovasculares
```
✓ Lubricación de banda de caminadora
✓ Ajuste de tensión de cables
✓ Limpieza de sensores
✓ Verificación de frenos
✓ Calibración de pantallas
✓ Revisión de ruidos anormales
```

#### Equipos de Fuerza
```
✓ Lubricación de guías y poleas
✓ Ajuste de asientos y respaldos
✓ Revisión de cables de acero
✓ Verificación de pesos y seguros
✓ Limpieza profunda de estructura
```

#### Máquinas de Pesas
```
✓ Inspección de placas de peso
✓ Lubricación de pines selectores
✓ Revisión de acolchados
✓ Ajuste de topes
```

**Frecuencias Recomendadas:**
- **Diario**: Limpieza superficial
- **Semanal**: Inspección visual
- **Mensual**: Lubricación y ajustes menores
- **Trimestral**: Mantenimiento profundo
- **Semestral**: Revisión técnica completa
- **Anual**: Mantenimiento mayor

### Mantenimiento CORRECTIVO 🔧

**Objetivo**: Reparar fallas o problemas existentes.

**Características:**
- Se realiza **cuando hay una falla**
- Es **reactivo** (responde a un problema)
- Puede ser **urgente** o de emergencia
- **Restaura** la funcionalidad del equipo

**Ejemplos de Problemas:**

#### Emergencias (Inmediatas)
```
🚨 Caminadora detenida en medio de uso
🚨 Cable roto en máquina de poleas
🚨 Asiento suelto o roto
🚨 Fuga de aceite hidráulico
🚨 Ruidos anormales fuertes
```

#### Reparaciones Programables
```
🔧 Pantalla digital no enciende
🔧 Botones no responden
🔧 Acolchado desgastado
🔧 Crujidos en estructura
🔧 Pesas descalibradas
```

**Clasificación por Prioridad:**

| Prioridad | Tiempo | Descripción |
|-----------|--------|-------------|
| **CRÍTICA** | Inmediato | Equipo inutilizable, peligro para usuarios |
| **ALTA** | 1-2 días | Equipo con falla pero usable con limitaciones |
| **MEDIA** | 1 semana | Problema menor, no afecta función principal |
| **BAJA** | Próximo preventivo | Desgaste estético, problemas cosméticos |

**Flujo de Correctivo de Emergencia:**

```
1. Usuario reporta falla
   ↓
2. Se marca equipo como "Inactivo"
   ↓
3. Se crea mantenimiento correctivo "Pendiente"
   ↓
4. Se asigna responsable (interno o externo)
   ↓
5. Se inicia mantenimiento
   ↓
6. Se repara el equipo
   ↓
7. Se completa mantenimiento con observaciones
   ↓
8. Equipo vuelve a estado "Activo"
```

---

## 📊 FLUJO DE TRABAJO COMPLETO

### Escenario 1: Mantenimiento Preventivo Programado

**Paso 1: Programar el Mantenimiento**
```
1. Click en "+ Nuevo Mantenimiento"
2. Llenar formulario:
   - Activo: CARDIO-001
   - Tipo: Preventivo
   - Fecha Programada: 30 oct 2025
   - Responsable: Juan Pérez (empleado)
   - Costo Estimado: $1,500
   - Descripción: "Mantenimiento trimestral: lubricación, ajustes y limpieza"
3. Guardar
```

**Resultado**: Mantenimiento creado en estado **"Pendiente"**

**Paso 2: Recibir Notificación**
```
📅 15 días antes: Aparece en filtro "Próximos (15 días)"
⚠️ 7 días antes: Notificación amarilla en dashboard
🚨 Día programado: Si no se inicia, pasa a "Vencidos"
```

**Paso 3: Ejecutar el Mantenimiento**
```
1. Abrir la card del mantenimiento
2. Click en "▶️ Iniciar"
3. Estado cambia a "En Proceso"
4. El activo se marca automáticamente como "En Mantenimiento"
```

**Paso 4: Completar el Trabajo**
```
1. Realizar el mantenimiento físico
2. Click en "✅ Completar"
3. Se solicita:
   - Fecha de ejecución: 30 oct 2025
   - Observaciones: "Se lubricó banda, ajustó velocidad, limpieza completa. Todo OK."
   - Costo final: $1,500
4. Confirmar
```

**Resultado**:
- Mantenimiento en estado **"Completado"**
- Activo vuelve a estado **"Activo"**
- Se registra historial

### Escenario 2: Mantenimiento Correctivo de Emergencia

**Paso 1: Reporte de Falla**
```
Usuario reporta: "Caminadora CARDIO-003 hace ruido extraño y huele a quemado"
```

**Paso 2: Acción Inmediata**
```
1. Ir a Gestión de Activos
2. Buscar CARDIO-003
3. Cambiar estado a "Inactivo" (para evitar uso)
4. Click en "Crear Mantenimiento" desde el detalle del activo
```

**Paso 3: Crear Mantenimiento Correctivo**
```
Formulario:
- Activo: CARDIO-003 (ya seleccionado)
- Tipo: Correctivo 🔧
- Fecha Programada: HOY
- Responsable: Técnico Externo (proveedor)
- Costo Estimado: $3,000
- Descripción: "EMERGENCIA: Ruido y olor a quemado. Posible motor dañado."
- Prioridad: CRÍTICA
```

**Paso 4: Coordinación**
```
1. Llamar al proveedor de servicio
2. Agendar visita (mismo día si es posible)
3. Iniciar mantenimiento cuando llegue el técnico
```

**Paso 5: Diagnóstico y Reparación**
```
Técnico diagnostica:
- Motor sobrecalentado
- Necesita reemplazo de rodamiento
- Tiempo estimado: 2 horas
```

**Paso 6: Finalización**
```
1. Click en "✅ Completar"
2. Datos:
   - Fecha de ejecución: HOY
   - Observaciones: "Reemplazado rodamiento delantero. Motor limpiado y lubricado.
                     Pruebas satisfactorias. Recomendación: mantenimiento preventivo mensual."
   - Costo final: $3,500 (mayor por pieza adicional)
3. Confirmar
```

**Paso 7: Reactivación**
```
1. Ir a Gestión de Activos
2. Buscar CARDIO-003
3. Cambiar estado a "Activo"
4. Agregar nota: "Equipo reparado - Listo para uso"
```

**Resultado**:
- Equipo operativo nuevamente
- Historial de falla registrado
- Información para prevención futura

---

## 🎨 INDICADORES VISUALES

### Colores de Estado

| Estado | Color | Código | Uso |
|--------|-------|--------|-----|
| Pendiente | Naranja | #f59e0b | Alerta moderada |
| En Proceso | Azul | #3b82f6 | Información |
| Completado | Verde | #10b981 | Éxito |
| Cancelado | Gris | #6b7280 | Neutral/Inactivo |

### Indicadores de Urgencia (Días)

#### Vencido 🚨
```
Color: Rojo (#ef4444)
Formato: "Vencido hace X días"
Nivel: CRÍTICO
Acción: Atención inmediata
```

#### Hoy ⚠️
```
Color: Naranja (#f59e0b)
Formato: "Hoy"
Nivel: URGENTE
Acción: Realizar hoy mismo
```

#### Próximo (1-7 días) ⚠️
```
Color: Naranja (#f59e0b)
Formato: "En X día(s)"
Nivel: PRIORITARIO
Acción: Programar en la semana
```

#### Futuro (8+ días) 📅
```
Color: Azul (#3b82f6)
Formato: "En X días"
Nivel: NORMAL
Acción: Monitorear
```

### Iconos de Responsable

| Icono | Tipo | Descripción |
|-------|------|-------------|
| 👤 | Interno | Empleado del gimnasio |
| 🏢 | Externo | Proveedor de servicio externo |

### Iconos de Tipo

| Icono | Tipo | Descripción |
|-------|------|-------------|
| 🛡️ | Preventivo | Programado regularmente |
| 🔧 | Correctivo | Reparación de fallas |

---

## 💡 CASOS DE USO

### Caso 1: Planificación Mensual

**Objetivo**: Ver todos los mantenimientos del próximo mes

**Pasos:**
```
1. Seleccionar filtro especial: "⚠️ Próximos (15 días)"
2. Revisar la lista
3. Coordinar recursos y personal
4. Comprar consumibles necesarios
5. Agendar técnicos externos si es necesario
```

**Resultado**: Plan de mantenimiento organizado

### Caso 2: Atención de Emergencias

**Objetivo**: Resolver mantenimientos vencidos

**Pasos:**
```
1. Seleccionar filtro especial: "🚨 Vencidos"
2. Ordenar por días de retraso
3. Priorizar los más urgentes
4. Asignar responsables
5. Iniciar mantenimientos inmediatamente
```

**Resultado**: Backlog reducido

### Caso 3: Seguimiento de Mantenimientos en Curso

**Objetivo**: Monitorear trabajos en ejecución

**Pasos:**
```
1. Filtrar por estado: "🔄 En Proceso"
2. Revisar cada mantenimiento
3. Contactar responsables para actualización
4. Completar los finalizados
```

**Resultado**: Control del progreso

### Caso 4: Análisis de Costos

**Objetivo**: Revisar gastos de mantenimiento

**Pasos:**
```
1. Filtrar por estado: "✅ Completado"
2. Revisar costos en cada card
3. Sumar totales
4. Comparar con presupuesto
```

**Resultado**: Reporte de gastos

### Caso 5: Auditoría de Equipo Específico

**Objetivo**: Ver historial de un activo

**Pasos:**
```
1. En búsqueda escribir código: "CARDIO-001"
2. Ver todos los mantenimientos
3. Revisar frecuencia y costos
4. Identificar patrones de fallas
```

**Resultado**: Historial completo

---

## 📱 DISEÑO RESPONSIVE

### Desktop (> 1200px)
- Grid de 3 columnas
- Todas las acciones visibles
- Filtros en línea horizontal

### Tablet (768px - 1200px)
- Grid de 2 columnas
- Acciones en dos filas
- Filtros en línea

### Mobile (< 768px)
- Grid de 1 columna
- Acciones en columna vertical
- Header colapsado
- Filtros en columna

---

## 🎯 MEJORES PRÁCTICAS

### Para Mantenimientos Preventivos

✅ **DO (Hacer):**
- Programar con al menos 15 días de anticipación
- Asignar responsable desde el inicio
- Estimar costos realistas
- Incluir descripción detallada de tareas
- Mantener calendario regular

❌ **DON'T (No Hacer):**
- Postergar constantemente
- Cambiar fecha programada repetidamente
- Omitir observaciones al completar
- Cancelar sin motivo válido

### Para Mantenimientos Correctivos

✅ **DO (Hacer):**
- Crear inmediatamente al detectar falla
- Marcar prioridad correctamente
- Incluir síntomas detallados
- Actualizar estado del activo
- Registrar observaciones completas

❌ **DON'T (No Hacer):**
- Retrasar reporte de fallas
- Permitir uso de equipo con fallas
- Omitir detalles del problema
- No documentar la solución

### Para Gestión General

✅ **DO (Hacer):**
- Revisar diariamente el panel
- Atender vencidos prioritariamente
- Actualizar costos reales
- Documentar todo el trabajo
- Mantener historial completo

❌ **DON'T (No Hacer):**
- Ignorar notificaciones
- Eliminar registros históricos
- Omitir información relevante
- Cancelar sin explicación

---

## 🔧 TROUBLESHOOTING

### Problema: No aparecen mantenimientos

**Causas Posibles:**
1. Filtros muy restrictivos
2. No hay mantenimientos creados
3. Búsqueda no coincide

**Solución:**
1. Click en "✕ Limpiar filtros"
2. Verificar que existan mantenimientos
3. Usar búsqueda más amplia

### Problema: No puedo iniciar mantenimiento

**Causas Posibles:**
1. Ya está en otro estado
2. Permisos insuficientes

**Solución:**
1. Verificar estado actual
2. Contactar administrador si es necesario

### Problema: Badge de días no aparece

**Causa:**
- El mantenimiento está completado o cancelado

**Explicación:**
- Solo se muestra para estados "Pendiente" y "En Proceso"

---

## 📊 RESUMEN DE ACCIONES POR ESTADO

| Estado | Iniciar | Editar | Completar | Cancelar | Ver | Eliminar |
|--------|---------|--------|-----------|----------|-----|----------|
| Pendiente | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| En Proceso | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Completado | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Cancelado | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## 🎓 CONCLUSIÓN

El Panel de Gestión de Mantenimientos es una herramienta poderosa para:

1. **Prevenir Fallas**: Con mantenimientos preventivos regulares
2. **Resolver Problemas**: Con flujo ágil de correctivos
3. **Controlar Costos**: Con registro detallado de gastos
4. **Mantener Historial**: Para análisis y mejora continua
5. **Optimizar Recursos**: Con planificación efectiva

**Recuerda:**
- 🛡️ Lo preventivo es más barato que lo correctivo
- 🚨 Atender vencidos reduce riesgos
- 📊 Documentar ayuda a mejorar
- ⚡ La rapidez en correctivos mejora la experiencia del usuario

---

¡El panel está listo para gestionar eficientemente todos tus mantenimientos! 🎉
