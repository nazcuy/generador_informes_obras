"""
Generador de PDFs usando wkhtmltopdf.
Maneja la conversión de HTML a PDF con configuraciones específicas.
"""

from __future__ import annotations

import os
import re
import pdfkit
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.data.sheets_reader import SheetsReader
from config.constants import Config, FilePaths
from config.paths import PathManager
from src.templates.template_manager import template_manager
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class PDFGenerator:
    """Generador de PDFs con wkhtmltopdf"""
    
    def __init__(self, resources: Dict[str, str], output_dir: Optional[str] = None):
        """
        Inicializa el generador de PDFs.
        
        Args:
            resources: Recursos necesarios (imágenes, fuentes, etc.)
            output_dir: Directorio de salida (opcional)
        """
        self.resources = resources
        self.output_dir = Path(output_dir) if output_dir else PathManager.get_output_dir()
        self.pdf_config = self._setup_pdf_config()
        
        # Asegurar que existe el directorio de salida
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[OK] PDF Generator inicializado. Output: {self.output_dir}")
    
    def _setup_pdf_config(self) -> pdfkit.configuration:
        """
        Configura wkhtmltopdf.
        
        Returns:
            Configuración de wkhtmltopdf
        """
        try:
            config = pdfkit.configuration(wkhtmltopdf=Config.WKHTMLTOPDF_PATH)
            logger.info("[OK] Configuración wkhtmltopdf cargada")
            return config
        except Exception as e:
            logger.error(f"[!] Error configurando wkhtmltopdf: {e}")
            raise
    
    def generate_pdf(self, html_content: str, filename: str) -> bool:
        """
        Genera un PDF desde contenido HTML.
        
        Args:
            html_content: Contenido HTML a convertir
            filename: Nombre del archivo de salida
            
        Returns:
            True si se generó exitosamente, False en caso contrario
        """
        try:
            # Crear ruta completa del archivo
            output_path = self.output_dir / filename
            
            # Configurar opciones de PDF
            options = self._get_pdf_options()
            
            # Generar PDF
            pdfkit.from_string(html_content, str(output_path), 
                             configuration=self.pdf_config, options=options)
            
            logger.info(f"[+] PDF generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"[!] Error generando PDF {filename}: {e}")
            return False
    
    def generate_all(self, df, filter_prefix: str = "OTRAS") -> None:
        """
        Genera PDFs para todas las obras en el DataFrame.
        
        Args:
            df: DataFrame con datos de obras
            filter_prefix: Prefijo para filtrar obras ("OTRAS", "CONVE", "TODAS")
        """
        logger.info(f"[>] Iniciando generación masiva (filtro: {filter_prefix})")
        
        # Filtrar datos según prefijo
        filtered_df = self._filter_dataframe(df, filter_prefix)
        
        if filtered_df.empty:
            logger.warning(f"[!] No hay obras con prefijo '{filter_prefix}'")
            return
        
        logger.info(f"[>] Procesando {len(filtered_df)} obras...")
        
        success_count = 0
        error_count = 0
        
        for idx, row in filtered_df.iterrows():
            try:
                # Generar contexto para el template
                context = self._build_template_context(row)
                
                # Renderizar HTML
                html = template_manager.render_template('informe_template.html', context)
                
                # Generar nombre de archivo seguro
                filename = self._generate_safe_filename(row['id_obra'])
                
                # Generar PDF
                if self.generate_pdf(html, filename):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"[!] Error en obra {idx}: {e}")
                error_count += 1
                
                # Guardar HTML para debugging
                try:
                    debug_filename = f"error_{idx}.html"
                    with open(debug_filename, 'w', encoding='utf-8') as f:
                        f.write(html)
                except:
                    pass
        
        logger.info(f"[OK] Proceso completado. Exitosos: {success_count}, Errores: {error_count}")
    
    def _filter_dataframe(self, df, filter_prefix: str) -> 'pd.DataFrame':
        """
        Filtra el DataFrame según el prefijo especificado.
        
        Args:
            df: DataFrame a filtrar
            filter_prefix: Prefijo para filtrar
            
        Returns:
            DataFrame filtrado
        """
        if filter_prefix == "TODAS":
            return df
        elif filter_prefix == "OTRAS":
            return df[df['id_obra'].str.startswith('OTRAS-', na=False)]
        elif filter_prefix == "CONVE":
            return df[df['id_obra'].str.startswith('CONVE-', na=False)]
        else:
            return df
    
    def _build_template_context(self, row) -> Dict[str, Any]:
        """
        Construye el contexto para el template desde una fila del DataFrame.
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            Diccionario con contexto para el template
        """
        from src.processors.formatters import DataFormatters
        from src.processors.calculations import CalculosFinancieros
        
        # Procesar imágenes de la obra
        from src.processors.resources import ResourceProcessor

        obra_images = ResourceProcessor.get_work_images(
            obra_id=row.get('id_obra', '')
        )

        # Obtener UVIs restantes del merge
        uvis_restantes = row.get('UVI Restante', '--')
        if pd.isna(uvis_restantes):
            uvis_restantes = '--'
            
        # =========================
        # NOTICIAS DESDE GOOGLE SHEETS
        # =========================
        try:
            noticias = SheetsReader.obtener_noticias_por_obra(
                sheet_id=Config.GOOGLE_SHEET_ID_NOTICIAS,
                hoja_noticias=Config.GOOGLE_SHEET_NAME_NOTICIAS, 
                id_obra=row.get('id_obra')
            )
        except Exception as e:
            logger.warning(f"[!] Error trayendo noticias para {row.get('id_obra')}: {e}")
            noticias = []

        context = {
            # Recursos visuales
            'banner_path': self.resources.get('banner', ''),
            'footer_path': self.resources.get('footer', ''),
            'doble_flecha': self.resources.get('doble_flecha', ''),
            'fuente_regular': self.resources.get('fuente_regular', ''),
            'fuente_bold': self.resources.get('fuente_bold', ''),
            
            # Datos básicos
            'Memoria_Descriptiva': row.get('descripcion', '--'),
            'Imagen_Obra': obra_images.get('principal', ''),
            'Imagenes_Extra': obra_images.get('adicionales', []),
            'ID_obra': row.get('id_obra', '--'),
            'ID_historico': row.get('id_historico', '--'),
            'Descripcion_Corta': DataFormatters.extraer_descripcion_corta(row.get('descripcion', '--')),       
            # Datos formateados
            'Viviendas_Totales': DataFormatters.formatear_numero(row.get('viv_totales', '--')),
            'Viviendas_Entregadas': DataFormatters.formatear_numero(row.get('viv_entregadas', '--')),
            'Viviendas_Restantes': CalculosFinancieros.calculo_viviendas_restantes(
                row.get('viv_totales', '--'), 
                row.get('viv_entregadas', '--')
            ),
            'Estado': row.get('estado', '--'),
            'Solicitante_Financiamiento': row.get('solicitante_financiero', '--'),
            'Solicitante_Presupuestario': row.get('solicitante_presupuestario', '--'),
            'Municipio': row.get('municipio', '--'),
            'Localidad': row.get('localidad', '--'),
            'Modalidad': row.get('modalidad', '--'),
            'Programa': 'Programa COMPLETAR',
            'noticias': noticias,
            
            # Códigos
            'Cod_emprendimiento': DataFormatters.formatear_integer(row.get('emprendimiento_incluidos', '--')),
            'Cod_obra': DataFormatters.formatear_integer(row.get('codigos_incluidos', '--')),
            
            # Información financiera
            'Monto_Convenio': DataFormatters.formatear_moneda(row.get('monto_convenio', '--')),
            'Fecha_UVI': DataFormatters.formatear_fecha(row.get('fecha_cotizacion_uvi_convenio')),
            'Total_UVI': DataFormatters.formatear_numero(row.get('cantidad_uvis', '--')),
            'Uvis_Restantes': CalculosFinancieros.calcular_uvi_restantes(
                row.get('cantidad_uvis', '--'),
                uvis_restantes
            ),
            'Exp_GDEBA': '' if pd.isna(row.get('expediente_gdeba')) else str(row.get('expediente_gdeba')),
            
            # Avances
            'Avance_fisico': DataFormatters.formatear_porcentaje(row.get('porcentaje_avance_fisico', '--')),
            'Avance_Restante': CalculosFinancieros.calculo_viviendas_restantes(
                row.get('porcentaje_avance_fisico', '--')
            ),
            'Avance_financiero': DataFormatters.formatear_porcentaje(row.get('avance_financiero', '--')),
            
            # Montos
            """ 'Saldo_UVI_Pendiente': saldo_uvi_pendiente,
            'Saldo_Obra_Actualizado': saldo_actualizado_formateado, """
            
            'Monto_Restante_Actualizado': CalculosFinancieros.calcular_monto_restante(
                row.get('monto_actualizado', '--'),
                row.get('monto_pagado', '--')
            ),
            'Monto_Devengado': DataFormatters.formatear_moneda(row.get('monto_devengado', '--')),
            'Monto_Pagado': DataFormatters.formatear_moneda(row.get('monto_pagado', '--')),
            'Fecha_ultimo_pago': DataFormatters.formatear_fecha(row.get('fecha_ultimo_pago'))
        }
        
        return context
    
    def _get_pdf_options(self) -> Dict[str, Any]:
        """
        Obtiene las opciones de configuración para wkhtmltopdf.
        
        Returns:
            Diccionario con opciones de PDF
        """
        return {
            'enable-local-file-access': None,
            'margin-top': '30mm',
            'margin-bottom': '20mm',
            'margin-left': '4mm',
            'margin-right': '4mm',
            'footer-html': str(FilePaths.FOOTER_RENDERED_HTML),
            'header-html': str(FilePaths.HEADER_RENDERED_HTML),
            'encoding': Config.ENCODING,
        }
    
    def _generate_safe_filename(self, obra_id: str) -> str:
        """
        Genera un nombre de archivo seguro desde el ID de obra.
        
        Args:
            obra_id: ID de la obra
            
        Returns:
            Nombre de archivo seguro
        """
        # Crear nombre base
        nombre_base = f"informe_{obra_id}"
        
        # Remover caracteres peligrosos para文件名
        nombre_seguro = re.sub(r'[\\/*?:"<>|]', '', nombre_base)
        
        # Asegurar extensión
        if not nombre_seguro.endswith('.pdf'):
            nombre_seguro += '.pdf'
        
        return nombre_seguro
