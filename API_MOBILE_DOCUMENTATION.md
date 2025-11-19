# 📱 **API DOCUMENTATION - GIMNASIO APP MÓVIL**

## 🌐 **BASE URL**
```
http://localhost:8000/api/
```

---

## 🔐 **AUTENTICACIÓN**

### **1. Registro de Cliente (Público)**
```http
POST /registro/cliente/
Content-Type: application/json

{
  "email": "cliente@email.com",
  "password": "password123",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "telefono": "5551234567",
  "fecha_nacimiento": "1990-01-01",
  "genero": "masculino",
  "objetivo_fitness": "perder_peso",
  "nivel_experiencia": "principiante"
}
```

**Respuesta exitosa:**
```json
{
  "message": "Cliente registrado exitosamente",
  "cliente_id": 1,
  "user_id": 2,
  "email": "cliente@email.com"
}
```

### **2. Login (Obtener Token)**
```http
POST /token/
Content-Type: application/json

{
  "email": "cliente@email.com",
  "password": "password123"
}
```

**Respuesta exitosa:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **3. Refrescar Token**
```http
POST /token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 💳 **MEMBRESÍAS**

### **4. Ver Membresías Disponibles**
```http
GET /membresias/activas/
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre_plan": "Básico",
    "tipo": "Mensual",
    "precio": "599.00",
    "duracion_dias": 30,
    "descripcion": "Acceso completo al gimnasio durante horarios regulares",
    "beneficios": "Acceso a área de pesas, cardio y clases grupales básicas",
    "activo": true
  }
]
```

### **5. Adquirir Membresía**
```http
POST /membresias/{id}/adquirir/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "metodo_pago": "tarjeta",
  "meses_adicionales": 0
}
```

**Respuesta exitosa:**
```json
{
  "message": "Membresía adquirida exitosamente",
  "membresia_cliente_id": 1,
  "membresia": "Básico",
  "fecha_inicio": "2025-10-26",
  "fecha_fin": "2025-11-25",
  "precio": 599.0,
  "duracion_dias": 30
}
```

### **6. Ver Mis Membresías**
```http
GET /membresias/mis_membresias/
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "membresia": {
      "id": 1,
      "nombre_plan": "Básico",
      "tipo": "Mensual",
      "precio": 599.0,
      "beneficios": "Acceso a área de pesas, cardio y clases grupales básicas"
    },
    "fecha_inicio": "2025-10-26",
    "fecha_fin": "2025-11-25",
    "estado": "Activa",
    "dias_restantes": 30,
    "activa": true
  }
]
```

---

## 📅 **HORARIOS Y CLASES**

### **7. Ver Tipos de Actividades**
```http
GET /horarios/api/tipos-actividad/
Authorization: Bearer {access_token}
```

### **8. Ver Horarios Semanales**
```http
GET /horarios/api/horarios/calendario_semanal/?sede_id=1
Authorization: Bearer {access_token}
```

### **9. Ver Sesiones del Mes**
```http
GET /horarios/api/sesiones/calendario_mensual/?año=2025&mes=10
Authorization: Bearer {access_token}
```

### **10. Reservar Clase**
```http
POST /horarios/api/reservas-clases/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "sesion_clase": 5,
  "observaciones": "Mi primera clase de yoga"
}
```

**Respuesta exitosa:**
```json
{
  "id": 1,
  "cliente": {
    "id": 1,
    "nombre": "Juan Pérez"
  },
  "sesion_clase": {
    "id": 5,
    "horario": {
      "tipo_actividad": "Yoga",
      "entrenador": "María González",
      "espacio": "Salón A"
    },
    "fecha": "2025-10-27",
    "hora_inicio": "09:00:00",
    "hora_fin": "10:00:00"
  },
  "fecha_reserva": "2025-10-26T15:30:00Z",
  "estado": "confirmada"
}
```

### **11. Ver Mis Reservas**
```http
GET /horarios/api/reservas-clases/mis_reservas/
Authorization: Bearer {access_token}
```

### **12. Cancelar Reserva**
```http
POST /horarios/api/reservas-clases/{id}/cancelar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "motivo": "No puedo asistir"
}
```

---

## 👤 **PERFIL DE CLIENTE**

### **13. Ver Mi Perfil**
```http
GET /clientes/{id}/
Authorization: Bearer {access_token}
```

### **14. Actualizar Mi Perfil**
```http
PATCH /clientes/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "objetivo_fitness": "ganar_masa_muscular",
  "nivel_experiencia": "intermedio"
}
```

---

## 🏋️ **RESERVAS DE EQUIPOS**

### **15. Reservar Equipo**
```http
POST /horarios/api/reservas-equipos/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "activo": 1,
  "fecha_reserva": "2025-10-27",
  "hora_inicio": "14:00:00",
  "hora_fin": "15:00:00"
}
```

### **16. Ver Mis Reservas de Equipos**
```http
GET /horarios/api/reservas-equipos/?cliente={cliente_id}
Authorization: Bearer {access_token}
```

---

## 💪 **ENTRENADORES PERSONALES**

### **17. Reservar Sesión con Entrenador**
```http
POST /horarios/api/reservas-entrenadores/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "entrenador": 1,
  "fecha_sesion": "2025-10-28",
  "hora_inicio": "16:00:00",
  "hora_fin": "17:00:00",
  "tipo_sesion": "individual",
  "objetivo": "Mejorar técnica en levantamiento de pesas"
}
```

---

## 📊 **ESTADÍSTICAS Y DATOS**

### **18. Estadísticas de Membresías**
```http
GET /membresias/estadisticas/
Authorization: Bearer {access_token}
```

### **19. Estadísticas de Horarios**
```http
GET /horarios/api/estadisticas/
Authorization: Bearer {access_token}
```

---

## 🔧 **CONFIGURACIÓN DE HEADERS**

Para todas las peticiones autenticadas, incluir:

```javascript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};
```

---

## ⚠️ **CÓDIGOS DE ERROR COMUNES**

- **400**: Datos inválidos o faltantes
- **401**: Token inválido o expirado
- **403**: Sin permisos para esta acción
- **404**: Recurso no encontrado
- **500**: Error interno del servidor

---

## 🎯 **FLUJO RECOMENDADO PARA LA APP**

### **Registro/Login:**
1. Pantalla de bienvenida
2. Registro de cliente → `POST /registro/cliente/`
3. Login → `POST /token/`
4. Guardar tokens en AsyncStorage

### **Dashboard Principal:**
1. Verificar membresía activa → `GET /membresias/mis_membresias/`
2. Mostrar próximas reservas → `GET /horarios/api/reservas-clases/mis_reservas/`
3. Accesos rápidos a funciones principales

### **Membresías:**
1. Ver disponibles → `GET /membresias/activas/`
2. Adquirir → `POST /membresias/{id}/adquirir/`
3. Ver historial → `GET /membresias/mis_membresias/`

### **Reservas:**
1. Ver horarios → `GET /horarios/api/sesiones/calendario_mensual/`
2. Reservar clase → `POST /horarios/api/reservas-clases/`
3. Gestionar reservas → `GET /horarios/api/reservas-clases/mis_reservas/`

---

## 🧪 **DATOS DE PRUEBA DISPONIBLES**

- **Membresías**: 8 planes diferentes (Básico, Premium, VIP, etc.)
- **Tipos de Actividad**: Yoga, Spinning, CrossFit, etc.
- **Usuario Admin**: `admin@gimnasio.com` / `admin123`

---

## 📞 **SOPORTE**

Si encuentras algún error o necesitas más endpoints, contacta al equipo de desarrollo.

# Registro de Cliente (App Móvil)

- Método: POST
- URL: /api/registro/cliente/
- Auth: No requiere (público)

Campos requeridos:
- email: string (único)
- password: string
- nombre: string
- apellido_paterno: string
- telefono: string (10 dígitos)

Campos opcionales:
- apellido_materno: string
- fecha_nacimiento: YYYY-MM-DD
- sexo: masculino | femenino | no_especificado
  - También se acepta el alias "genero" desde la app; el backend lo mapea a "sexo".
- objetivo_fitness: string (por defecto: mantenimiento)
- nivel_experiencia: principiante | intermedio | avanzado (por defecto: principiante)

Ejemplo de petición:
```json
{
  "email": "cliente@example.com",
  "password": "Password123",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "telefono": "5551234567",
  "genero": "masculino",
  "fecha_nacimiento": "1990-01-01",
  "objetivo_fitness": "perder_peso",
  "nivel_experiencia": "principiante"
}
```

Respuestas:
- 201 Created
```json
{
  "message": "Cliente registrado exitosamente",
  "cliente_id": 1,
  "user_id": 10,
  "email": "cliente@example.com"
}
```

- 400 Bad Request
```json
{ "error": "El campo nombre es requerido" }
```

- 500 Error interno
```json
{ "error": "Error al registrar cliente: <detalle>" }
```