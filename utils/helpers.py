"""
Funciones utilitarias generales para el proyecto.
Logging, validaciones y funciones auxiliares.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Configura el sistema de logging para el proyecto.
    
    Args:
        name: Nombre del logger (opcional)
        
    Returns:
        Logger configurado
    """
    from config.constants import Config
    
    # Crear logger
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Configurar nivel
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))
    
    # Crear formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def validate_environment() -> bool:
    """
    Valida que el entorno esté correctamente configurado.
    
    Returns:
        True si el entorno es válido, False en caso contrario
    """
    from config.constants import Config
    
    issues = []
    
    # Validar Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ requerido")
    
    # Validar wkhtmltopdf
    wkhtml_path = Path(Config.WKHTMLTOPDF_PATH)
    if not wkhtml_path.exists():
        issues.append(f"wkhtmltopdf no encontrado en: {Config.WKHTMLTOPDF_PATH}")
    
    # Validar archivos requeridos
    required_files = [
        Path(Config.EXCEL_PATH),
        Path("templates/informe_template.html")
    ]
    
    for file_path in required_files:
        if not file_path.exists():
            issues.append(f"Archivo requerido no encontrado: {file_path}")
    
    # Reportar issues
    if issues:
        logger = setup_logging(__name__)
        logger.error("[!] Problemas de configuración encontrados:")
        for issue in issues:
            logger.error(f"    - {issue}")
        return False
    
    return True

def create_project_structure():
    """
    Crea la estructura de directorios del proyecto si no existe.
    """
    directories = [
        "assets/images",
        "assets/fonts", 
        "templates",
        "informes",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def safe_filename(filename: str) -> str:
    """
    Convierte un string en un nombre de archivo seguro.
    
    Args:
        filename: Nombre original
        
    Returns:
        Nombre seguro para usar como archivo
    """
    import re
    
    # Remover caracteres peligrosos
    safe = re.sub(r'[\\/*?:"<>|]', '', filename)
    
    # Remover espacios al inicio y final
    safe = safe.strip()
    
    # Limitar longitud
    if len(safe) > 200:
        safe = safe[:200]
    
    return safe

def format_bytes(size_bytes: int) -> str:
    """
    Formatea bytes en una cadena legible.
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.2 MB")
    """
    import math
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def get_project_info() -> dict:
    """
    Obtiene información del proyecto.
    
    Returns:
        Diccionario con información del proyecto
    """
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    
    return {
        "name": "Generador de Informes de Obras",
        "version": "2.0.0",
        "description": "Sistema automatizado de generación de informes PDF para obras públicas",
        "author": "MiniMax Agent",
        "root_directory": str(project_root),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
