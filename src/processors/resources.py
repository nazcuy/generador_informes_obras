"""
Procesamiento de recursos (imágenes, fuentes, etc.).
Convierte archivos a formatos embebibles en HTML/PDF.
"""

from __future__ import annotations

import os
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from config.constants import FilePaths
from config.paths import PathManager
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class ResourceProcessor:
    """Procesador de recursos para embebido en HTML"""
    
    @staticmethod
    def prepare_all() -> Dict[str, str]:
        """
        Prepara todos los recursos necesarios para los PDFs.
        
        Returns:
            Diccionario con todos los recursos en formato base64
        """
        logger.info("[>] Preparando recursos para PDF...")
        
        resources = {
            'banner': ResourceProcessor.image_to_data_uri(FilePaths.BANNER_PATH),
            'footer': ResourceProcessor.image_to_data_uri(FilePaths.FOOTER_PATH),
            'doble_flecha': ResourceProcessor.image_to_data_uri(FilePaths.DOBLE_FLECHA_PATH),
            'fuente_regular': ResourceProcessor.font_to_base64(FilePaths.FUENTE_REGULAR_PATH),
            'fuente_bold': ResourceProcessor.font_to_base64(FilePaths.FUENTE_BOLD_PATH),
        }
        
        # Renderizar templates HTML con imágenes embebidas
        ResourceProcessor._render_html_templates(resources)
        
        logger.info("[OK] Recursos preparados exitosamente")
        return resources
    
    @staticmethod
    def font_to_base64(font_path: Path) -> str:
        """
        Convierte una fuente TTF a base64 para embebido en CSS.
        
        Args:
            font_path: Ruta a la fuente
            
        Returns:
            String base64 de la fuente o string vacío si no existe
        """
        if not font_path or not font_path.exists():
            logger.warning(f"[!] Fuente no encontrada: {font_path}")
            return ""
        
        try:
            with open(font_path, "rb") as font_file:
                encoded = base64.b64encode(font_file.read()).decode('utf-8')
            logger.info(f"[OK] Fuente convertida: {font_path.name}")
            return encoded
            
        except Exception as e:
            logger.error(f"[!] Error procesando fuente {font_path}: {e}")
            return ""
    
    @staticmethod
    def image_to_data_uri(image_path: Path) -> str:
        """
        Convierte una imagen a Data URI para embebido en HTML.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Data URI string o string vacío si no existe
        """
        if not image_path or not image_path.exists():
            # Intentar con extensión alternativa
            validated_path = PathManager.validate_image_path(image_path)
            if not validated_path:
                logger.warning(f"[!] Imagen no encontrada: {image_path}")
                return ""
            image_path = validated_path
        
        try:
            # Determinar tipo MIME
            ext = image_path.suffix.lower().replace('.', '')
            mime_type = f"image/{'jpeg' if ext == 'jpg' else ext}"
            
            # Leer y codificar
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
            
            logger.info(f"[OK] Imagen convertida: {image_path.name}")
            return f"data:{mime_type};base64,{encoded}"
            
        except Exception as e:
            logger.error(f"[!] Error procesando imagen {image_path}: {e}")
            return ""
    
    @staticmethod
    def get_work_images(obra_id: str, images_dir: Optional[Path] = None) -> Dict[str, List[str]]:
        """
        Obtiene todas las imágenes asociadas a una obra.
        
        Args:
            obra_id: ID de la obra
            images_dir: Directorio de imágenes (opcional)
            
        Returns:
            Diccionario con imagen principal e imágenes adicionales
        """
        if images_dir is None:
            images_dir = FilePaths.IMAGENES_OBRAS_DIR
        
        if not images_dir.exists():
            logger.warning(f"[!] Directorio de imágenes no existe: {images_dir}")
            return {'principal': '', 'adicionales': []}
        
        result = {
            'principal': '',
            'adicionales': []
        }
        
        # Buscar imagen principal (ID_obra.jpg o .png)
        principal_paths = [
            images_dir / f"{obra_id}.jpg",
            images_dir / f"{obra_id}.png"
        ]
        
        for path in principal_paths:
            if path.exists():
                result['principal'] = ResourceProcessor.image_to_data_uri(path)
                break
        
        # Buscar imágenes adicionales (ID_obra_*.jpg o .png)
        for file_path in sorted(images_dir.iterdir()):
            if (file_path.is_file() and 
                file_path.name.startswith(f"{obra_id}_") and
                file_path.suffix.lower() in ['.jpg', '.png']):
                
                uri = ResourceProcessor.image_to_data_uri(file_path)
                if uri:
                    result['adicionales'].append(uri)
        
        return result
    
    @staticmethod
    def _render_html_templates(resources: Dict[str, str]) -> None:
        """
        Renderiza templates HTML con imágenes embebidas.
        
        Args:
            resources: Diccionario con recursos base64
        """
        # Renderizar header
        if FilePaths.HEADER_HTML_PATH.exists():
            try:
                with open(FilePaths.HEADER_HTML_PATH, 'r', encoding='utf-8') as f:
                    header_content = f.read()
                
                header_rendered = header_content.replace('{{ banner_base64 }}', resources.get('banner', ''))
                
                with open(FilePaths.HEADER_RENDERED_HTML, 'w', encoding='utf-8') as f:
                    f.write(header_rendered)
                
                logger.info("[OK] Header HTML renderizado")
                
            except Exception as e:
                logger.error(f"[!] Error renderizando header: {e}")
        
        # Renderizar footer
        if FilePaths.FOOTER_HTML_PATH.exists():
            try:
                with open(FilePaths.FOOTER_HTML_PATH, 'r', encoding='utf-8') as f:
                    footer_content = f.read()
                
                fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                footer_rendered = (
                    footer_content
                    .replace('{{ footer_base64 }}', resources.get('footer', ''))
                    .replace('{{ fecha_generacion }}', fecha_generacion)
                )
                
                with open(FilePaths.FOOTER_RENDERED_HTML, 'w', encoding='utf-8') as f:
                    f.write(footer_rendered)
                
                logger.info("[OK] Footer HTML renderizado")
                
            except Exception as e:
                logger.error(f"[!] Error renderizando footer: {e}")
