"""
Configuraciones centrales del proyecto.
Rutas dinámicas y configuraciones de entorno.
"""

import os
from pathlib import Path

# Configuración dinámica de rutas
BASE_DIR = Path(__file__).parent.parent.resolve()
PROJECT_NAME = "generador_informes_obras"

# Directorios de recursos
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
TEMPLATES_DIR = BASE_DIR / "templates"
IMAGENES_OBRAS_DIR = BASE_DIR / "imagenes_obras"

# Archivos específicos
DEFAULT_EXCEL = "pdf_generator_3000_paralizadas.xlsx"
OUTPUT_DIR = "informes"

# Configuración de clases de archivo
class FilePaths:
    """Paths específicos de archivos del proyecto"""
    # Directorios
    BASE_DIR = BASE_DIR
    ASSETS_DIR = ASSETS_DIR
    IMAGES_DIR = IMAGES_DIR
    IMAGENES_OBRAS_DIR = IMAGENES_OBRAS_DIR
    FONTS_DIR = FONTS_DIR
    TEMPLATES_DIR = TEMPLATES_DIR
    OUTPUT_DIR = OUTPUT_DIR
    
    # Imágenes
    BANNER_PATH = IMAGES_DIR / "banner.jpg"
    FOOTER_PATH = IMAGES_DIR / "footer.jpg"
    DOBLE_FLECHA_PATH = IMAGES_DIR / "doble_flecha.jpg"
    
    # Fuentes
    FUENTE_REGULAR_PATH = FONTS_DIR / "EncodeSans-Regular.ttf"
    FUENTE_BOLD_PATH = FONTS_DIR / "EncodeSans-Bold.ttf"
    
    # Templates HTML
    HEADER_HTML_PATH = TEMPLATES_DIR / "header.html"
    HEADER_RENDERED_HTML = TEMPLATES_DIR / "header_rendered.html"
    FOOTER_HTML_PATH = TEMPLATES_DIR / "footer.html"
    FOOTER_RENDERED_HTML = TEMPLATES_DIR / "footer_rendered.html"
    TEMPLATE_HTML_PATH = TEMPLATES_DIR / "informe_template.html"

# Configuración de aplicación
class Config:
    """Configuración centralizada de la aplicación"""
    
    # Variables de entorno - Excel
    EXCEL_PATH = os.getenv("EXCEL_PATH", DEFAULT_EXCEL)
    
    # Variables de entorno - Google Sheets
    GOOGLE_SHEET_ID_OBRAS = "1uHWntTfMfUt08Keau9yKWYHs5IL0LhjX"
    GOOGLE_SHEET_NAME_OBRAS = "Resumen Viv. Nación -"
    GOOGLE_COLUMNS = ['ID', 'UVI Restante']
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_SHEET_ID_NOTICIAS = "1_n-5TWac7OOGEDeXQWScMHJsH5N9rq7FZratnckAyg0"
    GOOGLE_SHEET_NAME_NOTICIAS = "Noticias"
    
    # Variables de entorno - wkhtmltopdf
    WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    
    # Configuración de procesamiento
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", OUTPUT_DIR)
    DEFAULT_FILTER = "OTRAS"  # OTRAS, CONVE, TODAS
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    
    # Configuración de encoding
    ENCODING = "utf-8"
