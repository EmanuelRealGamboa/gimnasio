# 📋 Resumen de Configuración Completa - App Móvil + Backend

## ✅ Cambios Realizados

### 1. Backend Django (c:\gimnasio)

#### Archivo: `gym/settings.py`
- ✅ `ALLOWED_HOSTS = ['*']` - Permite conexiones desde cualquier host
- ✅ `CORS_ALLOW_ALL_ORIGINS = True` - Permite CORS desde cualquier origen

#### Documentación creada:
- ✅ `CONFIGURACION_MOVIL.md` - Guía para configurar Django para conexiones móviles

### 2. App Móvil (c:\gimnasio\AppMovilGimnasio)

#### Archivos modificados/creados:
- ✅ `src/config/config.ts` - **NUEVO** Configuración centralizada de la API
- ✅ `src/services/api.ts` - Actualizado para usar config centralizado
- ✅ `CONFIGURACION.md` - Guía completa de instalación y configuración
- ✅ `README.md` - Documentación principal del proyecto

---

## 🚀 Pasos para Ejecutar Todo

### Paso 1: Obtener tu IP Local

**Windows:**
```bash
ipconfig
```
Busca "Dirección IPv4" (ej: `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig
```

### Paso 2: Configurar la App Móvil

Edita: `AppMovilGimnasio/src/config/config.ts`

```typescript
API_BASE_URL: 'http://TU_IP:8000/api/',
```

Ejemplo:
```typescript
API_BASE_URL: 'http://192.168.1.100:8000/api/',
```

### Paso 3: Ejecutar Backend Django

Desde `c:\gimnasio`:

```bash
python manage.py runserver 0.0.0.0:8000
```

⚠️ **IMPORTANTE**: Usa `0.0.0.0:8000` (NO `localhost:8000`)

### Paso 4: Instalar Dependencias de la App Móvil

Desde `c:\gimnasio\AppMovilGimnasio`:

```bash
npm install
```

### Paso 5: Ejecutar la App Móvil

**Opción A - Script (Windows):**
```bash
EJECUTAR_APP.bat
```

**Opción B - Manual:**
```bash
npm start
```

### Paso 6: Conectar tu Dispositivo

1. Instala **Expo Go** en tu celular:
   - [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS](https://apps.apple.com/app/expo-go/id982107779)

2. Escanea el código QR que aparece en la terminal

3. ¡Listo! La app debería cargar en tu celular

---

## 🔍 Verificar que Todo Funciona

### 1. Backend Django
Abre en el navegador de tu PC:
```
http://localhost:8000/api/
```
Deberías ver la API de Django REST Framework.

### 2. Conexión desde el Celular
Abre en el navegador de tu CELULAR (conectado a la misma WiFi):
```
http://TU_IP:8000/api/
```
Si carga, la conexión está bien configurada.

### 3. App Móvil
- Deberías ver la pantalla de Login
- Intenta iniciar sesión
- Navega por las diferentes secciones

---

## ❌ Solución de Problemas Comunes

### 1. "Network request failed" en la app

**Causa**: La app no puede conectarse al backend

**Solución**:
- Verifica que la IP en `src/config/config.ts` sea correcta
- Confirma que Django esté corriendo en `0.0.0.0:8000`
- Asegúrate de estar en la misma red WiFi
- Desactiva el firewall temporalmente

### 2. Django no acepta conexiones

**Causa**: Django está corriendo en `localhost:8000` en lugar de `0.0.0.0:8000`

**Solución**:
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. No aparece el QR de Expo

**Solución**:
```bash
# Limpiar caché de Expo
cd AppMovilGimnasio
npx expo start -c
```

### 4. Error de CORS en el navegador

**Causa**: CORS no está configurado correctamente

**Solución**: Ya está configurado en `settings.py` con `CORS_ALLOW_ALL_ORIGINS = True`

---

## 📱 Estructura de Archivos Importante

```
c:\gimnasio\
├── gym/
│   └── settings.py                    # ✅ Configurado para CORS y ALLOWED_HOSTS
├── CONFIGURACION_MOVIL.md             # 📄 Guía de configuración del backend
├── AppMovilGimnasio/
│   ├── src/
│   │   ├── config/
│   │   │   └── config.ts              # ⚙️ CAMBIAR IP AQUÍ
│   │   ├── services/
│   │   │   └── api.ts                 # 🔗 Configuración de Axios
│   │   └── screens/                   # 📱 Pantallas de la app
│   ├── CONFIGURACION.md               # 📄 Guía completa de la app móvil
│   ├── README.md                      # 📄 Documentación principal
│   └── package.json                   # 📦 Dependencias
└── RESUMEN_CONFIGURACION_COMPLETA.md  # 📋 Este archivo
```

---

## 🎯 Checklist Final

Antes de ejecutar todo, verifica:

- [ ] Django tiene `ALLOWED_HOSTS = ['*']` en `settings.py`
- [ ] Django tiene `CORS_ALLOW_ALL_ORIGINS = True` en `settings.py`
- [ ] Has obtenido tu IP local (con `ipconfig` o `ifconfig`)
- [ ] Has configurado la IP en `AppMovilGimnasio/src/config/config.ts`
- [ ] Has instalado las dependencias con `npm install` en la carpeta de la app móvil
- [ ] Ambos dispositivos (PC y celular) están en la misma red WiFi
- [ ] Tienes instalado **Expo Go** en tu celular
- [ ] Django está corriendo en `0.0.0.0:8000` (no en `localhost:8000`)

---

## 📞 Referencias Rápidas

- **Backend Django**: `http://TU_IP:8000/api/`
- **Frontend Web**: `http://localhost:3000`
- **App Móvil**: Expo Go + código QR
- **Archivo de config de IP**: `AppMovilGimnasio/src/config/config.ts`

---

## 🔐 Credenciales

Usa las mismas credenciales que tienes configuradas en el sistema web.

---

**¿Todo listo?** Ejecuta los comandos en el orden indicado y disfruta de tu app móvil! 🎉
