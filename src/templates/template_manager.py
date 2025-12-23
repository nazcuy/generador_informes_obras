"""
Gestión de templates Jinja2.
Configuración y renderizado de templates HTML.
"""

from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, Optional

from config.constants import FilePaths
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class TemplateManager:
    """Gestor de templates Jinja2"""
    
    def __init__(self):
        """Inicializa el gestor de templates"""
        self.env = self._setup_environment()
        self._register_filters()
    
    def _setup_environment(self) -> Environment:
        """
        Configura el entorno Jinja2.
        
        Returns:
            Environment configurado
        """
        # Crear directorio de templates si no existe
        FilePaths.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configurar environment
        env = Environment(
            loader=FileSystemLoader(FilePaths.TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        logger.info("[OK] Environment Jinja2 configurado")
        return env
    
    def _register_filters(self) -> None:
        """Registra filtros personalizados en el environment"""
        # Filtro para dividir texto en chunks
        self.env.filters['chunk'] = self._chunk_text
        
        # Filtro para dividir listas en grupos
        self.env.filters['dividir'] = self._divide_in_groups
        
        logger.info("[OK] Filtros personalizados registrados")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderiza un template con el contexto dado.
        
        Args:
            template_name: Nombre del template
            context: Variables para el template
            
        Returns:
            HTML renderizado
            
        Raises:
            TemplateNotFound: Si el template no existe
            TemplateError: Si hay error en el renderizado
        """
        try:
            template = self.env.get_template(template_name)
            html = template.render(**context)
            logger.info(f"[OK] Template renderizado: {template_name}")
            return html
            
        except Exception as e:
            logger.error(f"[!] Error renderizando template {template_name}: {e}")
            raise
    
    def template_exists(self, template_name: str) -> bool:
        """
        Verifica si un template existe.
        
        Args:
            template_name: Nombre del template
            
        Returns:
            True si existe, False en caso contrario
        """
        try:
            self.env.get_template(template_name)
            return True
        except:
            return False
    
    @staticmethod
    def _chunk_text(text: str, size: int = 20) -> str:
        """
        Filtro: Divide texto largo en líneas de tamaño especificado.
        
        Args:
            text: Texto a dividir
            size: Tamaño de cada línea
            
        Returns:
            Texto con saltos de línea
        """
        if not text:
            return ""
        return "<br>".join(text[i:i+size] for i in range(0, len(text), size))
    
    @staticmethod
    def _divide_in_groups(items: list, group_size: int = 4) -> list:
        """
        Filtro: Divide una lista en grupos del tamaño especificado.
        
        Args:
            items: Lista a dividir
            group_size: Tamaño de cada grupo
            
        Returns:
            Lista de listas (grupos)
        """
        if not items:
            return []
        return [items[i:i+group_size] for i in range(0, len(items), group_size)]

# Instancia global del template manager
template_manager = TemplateManager()
