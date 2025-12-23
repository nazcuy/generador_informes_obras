@echo off
REM Script para ejecutar el generador de informes desde CMD
REM Versión 2.0 - Actualizada para la nueva estructura
REM Uso: run.bat [opciones]

setlocal enabledelayedexpansion

echo ========================================
echo Generador de Informes v2.0 - Obras Paralizadas
echo ========================================
echo.

REM 1. Validar que el entorno virtual existe
if not exist ".\env\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado en .\env
    echo.        Por favor, crea el entorno con: python -m venv env
    echo.        Luego instala dependencias: pip install -r requirements.txt
    exit /b 1
)

REM 2. Activar entorno virtual
echo [*] Activando entorno virtual...
call ".\env\Scripts\activate.bat"

REM 3. Configurar encoding UTF-8
set PYTHONIOENCODING=utf-8
echo [*] Encoding configurado: UTF-8

REM 4. Verificar que el script principal existe
if not exist ".\scripts\run.py" (
    echo [ERROR] scripts\run.py no encontrado
    exit /b 1
)

REM 5. Mostrar opciones disponibles
echo [*] Opciones disponibles:
echo    run.bat                    - Ejecutar con configuración por defecto
echo    run.bat --help            - Ver ayuda completa
echo    run.bat --filter OTRAS    - Solo obras OTRAS- (por defecto)
echo    run.bat --filter TODAS    - Todas las obras
echo    run.bat --verbose         - Modo verbose
echo.

REM 6. Ejecutar el generador
echo [*] Iniciando generacion de informes...
echo.

REM Pasar todos los argumentos al script Python
python .\scripts\run.py %*

set exitCode=%ERRORLEVEL%
echo.
if %exitCode% equ 0 (
    echo ========================================
    echo [OK] Proceso completado exitosamente
    echo ========================================
) else (
    echo ========================================
    echo [ERROR] El proceso termino con codigo: %exitCode%
    echo ========================================
    echo.
    echo Sugerencias:
    echo - Verificar que los archivos de datos existan
    echo - Revisar la configuracion en .env
    echo - Ejecutar con --help para ver opciones
)

exit /b %exitCode%
