"""
Gestión de rutas del proyecto.
Funciones para validar y obtener rutas de archivos.
"""

from pathlib import Path
from typing import Optional
from config.constants import FilePaths

class PathManager:
    """Gestor de rutas del proyecto"""
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Asegura que el directorio existe"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def validate_image_path(path: Path) -> Optional[Path]:
        """Valida si existe la imagen, intenta JPG y PNG"""
        if not path.exists():
            # Intentar con extensión diferente
            if path.suffix.lower() == '.jpg':
                png_path = path.with_suffix('.png')
                return png_path if png_path.exists() else None
            elif path.suffix.lower() == '.png':
                jpg_path = path.with_suffix('.jpg')
                return jpg_path if jpg_path.exists() else None
        return path if path.exists() else None
    
    @staticmethod
    def get_output_dir() -> Path:
        """Obtiene y crea el directorio de salida"""
        return PathManager.ensure_dir(Path(FilePaths.OUTPUT_DIR))
    
    @staticmethod
    def get_template_dir() -> Path:
        """Obtiene el directorio de templates"""
        return Path(FilePaths.TEMPLATES_DIR)
    
    @staticmethod
    def get_assets_dir() -> Path:
        """Obtiene el directorio de assets"""
        return Path(FilePaths.ASSETS_DIR)
