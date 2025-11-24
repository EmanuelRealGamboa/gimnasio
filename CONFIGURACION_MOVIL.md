# Configuración para App Móvil

## 📱 Pasos para conectar la App Móvil

### 1. Obtener tu IP local

**Windows:**
```bash
ipconfig
```
Busca "Dirección IPv4" en la sección de tu adaptador de red WiFi (ej: `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig
# o
ip addr show
```

### 2. Ejecutar Django en todas las interfaces de red

En lugar de ejecutar Django solo en localhost, ejecuta:

```bash
python manage.py runserver 0.0.0.0:8000
```

Esto permite que tu dispositivo móvil se conecte a `http://TU_IP:8000`

Por ejemplo, si tu IP es `192.168.1.100`, la app móvil deberá conectarse a:
```
http://192.168.1.100:8000/api/
```

### 3. Configuraciones ya aplicadas en Django

✅ `ALLOWED_HOSTS = ['*']` - Permite conexiones desde cualquier host
✅ `CORS_ALLOW_ALL_ORIGINS = True` - Permite peticiones desde cualquier origen (desarrollo)

### 4. Verificar que funciona

Desde tu dispositivo móvil (conectado a la misma WiFi), abre el navegador y visita:
```
http://TU_IP:8000/api/
```

Deberías ver la API de Django REST Framework.

### 5. Configurar la App Móvil

Una vez clonada la app móvil, necesitarás actualizar la URL base del API con tu IP local.

---

## ⚠️ Notas Importantes

- **Ambos dispositivos deben estar en la misma red WiFi**
- **Desactiva el firewall** temporalmente si tienes problemas de conexión
- **Estas configuraciones son solo para desarrollo**, en producción debes usar configuraciones más restrictivas
