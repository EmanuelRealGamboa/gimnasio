@echo off
echo ========================================
echo   INICIANDO BACKEND PARA APP MOVIL
echo ========================================
echo.

REM Detener procesos existentes en el puerto 8000
echo Deteniendo procesos en puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo.

REM Esperar un segundo
timeout /t 1 /nobreak >nul

echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.

echo Iniciando servidor Django en 0.0.0.0:8000...
echo.
echo ========================================
echo   IMPORTANTE:
echo   El servidor aceptara conexiones desde
echo   cualquier dispositivo en la red local
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python manage.py runserver 0.0.0.0:8000
