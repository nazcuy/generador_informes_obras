#!/usr/bin/env python3
"""
Script de inicialización del proyecto.
Ayuda a configurar el entorno y validar dependencias.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_virtual_env():
    """Verifica si estamos en un entorno virtual"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Entorno virtual detectado")
        return True
    else:
        print("⚠️  Advertencia: No se detectó entorno virtual")
        print("   Se recomienda usar: python -m venv env")
        return False

def install_dependencies():
    """Instala las dependencias del proyecto"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ Error: requirements.txt no encontrado")
        return False
    
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def setup_environment():
    """Configura el archivo .env si no existe"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("🔧 Creando archivo .env...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado. Revisa y configura las variables necesarias.")
        return True
    elif env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    else:
        print("⚠️  Archivo .env.example no encontrado")
        return False

def check_wkhtmltopdf():
    """Verifica si wkhtmltopdf está instalado"""
    try:
        result = subprocess.run(["wkhtmltopdf", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ wkhtmltopdf detectado")
            return True
        else:
            print("❌ wkhtmltopdf no funciona correctamente")
            return False
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        print("❌ wkhtmltopdf no encontrado")
        print("   Descarga desde: https://wkhtmltopdf.org/downloads.html")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    directories = [
        "assets/images",
        "assets/fonts",
        "templates",
        "informes",
        "logs",
        "imagenes_obras"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")

def main():
    """Función principal de inicialización"""
    print("🚀 Configurando Generador de Informes de Obras v2.0")
    print("=" * 60)
    
    # Verificaciones
    checks = [
        ("Python", check_python_version),
        ("Entorno Virtual", check_virtual_env),
        ("wkhtmltopdf", check_wkhtmltopdf),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Verificando {name}...")
        if not check_func():
            all_passed = False
    
    # Configuraciones
    print(f"\n⚙️  Configurando proyecto...")
    setup_environment()
    create_directories()
    
    # Instalación de dependencias
    print(f"\n📦 Instalando dependencias...")
    if not install_dependencies():
        all_passed = False
    
    # Resumen final
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Configuración completada exitosamente")
        print("\n🎯 Próximos pasos:")
        print("   1. Configurar .env con tus datos")
        print("   2. Colocar archivos de datos en la raíz")
        print("   3. Ejecutar: python scripts/run.py --help")
    else:
        print("⚠️  Configuración completada con advertencias")
        print("   Revisa los errores anteriores antes de continuar")
    
    print("\n📖 Documentación completa en README.md")

if __name__ == "__main__":
    main()
