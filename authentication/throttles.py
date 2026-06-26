from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limita los intentos de login por IP para frenar ataques de fuerza bruta.

    Solo se aplica al endpoint de obtención de token (no al resto de la API).
    La tasa se define en REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'].

    Nota de producción: con varios workers de gunicorn, la caché por defecto
    (LocMemCache) es por proceso, así que el conteo es por worker. Para un límite
    global robusto conviene una caché compartida (Redis) vía CACHES.
    """
    scope = 'login'
