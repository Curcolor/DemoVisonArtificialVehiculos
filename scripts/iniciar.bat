@echo off
echo Sistema de Detección y Seguimiento de Vehículos
echo ==============================================
echo.

REM Verificar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH.
    echo Por favor, instale Python 3.7 o superior desde https://www.python.org/downloads/
    echo y asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)

echo Verificando requisitos...
python -m pip -V >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando pip...
    python -m ensurepip --default-pip
)

echo Instalando dependencias...
python -m pip install -r ../requirements.txt

echo.
echo Descargando modelos YOLO...
python ../tools/descargar_modelos.py

echo.
echo ==============================================
echo Opciones disponibles:
echo.
echo 1. Detección en tiempo real (cámara)
echo 2. Detección en archivo de video
echo 3. Calibrar parámetros
echo 4. Salir
echo.
set /p opcion="Seleccione una opción (1-4): "

if "%opcion%"=="1" (
    echo.
    echo Iniciando detección en tiempo real...
    python ../main.py --input 0
) else if "%opcion%"=="2" (
    echo.
    set /p video="Introduzca la ruta del archivo de video: "
    python ../main.py --input "%video%"
) else if "%opcion%"=="3" (
    echo.
    echo Seleccione la fuente para calibrar:
    echo 1. Cámara
    echo 2. Archivo de video
    set /p fuente="Seleccione una opción (1-2): "
    
    if "%fuente%"=="1" (
        python ../tools/calibracion.py --input 0
    ) else if "%fuente%"=="2" (
        set /p video="Introduzca la ruta del archivo de video para calibración: "
        python ../tools/calibracion.py --input "%video%"
    ) else (
        echo Opción no válida.
    )
) else if "%opcion%"=="4" (
    echo Saliendo...
) else (
    echo Opción no válida.
)

echo.
pause
