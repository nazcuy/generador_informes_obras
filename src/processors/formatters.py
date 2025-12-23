"""
Formateadores de datos para la aplicación.
Convierte datos en formatos presentables.
"""

from __future__ import annotations

import pandas as pd
from typing import Union, Any
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class DataFormatters:
    """Formateadores de datos para presentación"""
    
    @staticmethod
    def formatear_moneda(value: Union[str, float, int]) -> str:
        """Formatea número como moneda (arg): $ 1.234.567,89"""
        if DataFormatters._esta_vacio(value):
            return "--"
        
        try:
            # Limpiar string si es necesario
            if isinstance(value, str):
                value = value.replace('.', '').replace(',', '.')
            
            # Convertir a float
            float_value = float(value)
            
            # Formatear con separadores argentinos
            formatted = f"$ {float_value:,.2f}"
            return formatted.replace(",", "X").replace('.', ',').replace('X', '.')
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando moneda: {e} | Valor: {value}")
            return str(value)
    
    @staticmethod
    def formatear_moneda_sin_decimales(value: Union[str, float, int]) -> str:
        """Formatea número como moneda sin decimales: $ 1.234.567"""
        if DataFormatters._esta_vacio(value):
            return "--"
        
        try:
            # Limpiar string si es necesario
            if isinstance(value, str):
                value = value.replace('.', '').replace(',', '.')
            
            # Convertir a float
            float_value = float(value)
            
            # Formatear sin decimales
            formatted = f"$ {float_value:,.0f}"
            return formatted.replace(",", "X").replace('.', ',').replace('X', '.')
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando moneda sin decimales: {e} | Valor: {value}")
            return str(value)
    
    @staticmethod
    def formatear_porcentaje(value: Union[str, float, int]) -> str:
        """Formatea número como porcentaje: 50,00%"""
        if DataFormatters._esta_vacio(value):
            return "--"
        
        try:
            # Limpiar y convertir a float
            if isinstance(value, str):
                value = value.strip().replace('%', '').replace(',', '.')
            
            float_value = float(value)
            
            # Si está entre 0 y 1, multiplicar por 100
            if 0 <= float_value <= 1:
                float_value *= 100
            
            # Formatear con dos decimales
            return f"{float_value:.2f}".replace('.', ',') + "%"
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando porcentaje: {e} | Valor: {value}")
            return str(value)
    
    @staticmethod
    def formatear_numero(value: Union[str, float, int]) -> str:
        """Formatea número con separadores de miles: 1.234.567"""
        if DataFormatters._esta_vacio(value):
            return "--"
        
        try:
            # Limpiar string si es necesario
            if isinstance(value, str):
                value = value.replace('.', '').replace(',', '.')
            
            # Convertir a float
            float_value = float(value)
            
            # Formatear sin decimales
            formatted = f"{float_value:,.0f}"
            return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando número: {e} | Valor: {value}")
            return str(value)
    
    @staticmethod
    def formatear_integer(value: Union[str, float, int]) -> str:
        """Formatea número como entero sin separadores: 1234567"""
        if DataFormatters._esta_vacio(value):
            return "--"
        
        try:
            # Limpiar string si es necesario
            if isinstance(value, str):
                value = value.replace('.', '').replace(',', '.')
            
            # Convertir a entero
            int_value = int(float(value))
            return str(int_value)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formateando entero: {e} | Valor: {value}")
            return str(value)
    
    @staticmethod
    def formatear_fecha(fecha) -> str:
        """Formatea fecha como DD/MM/YYYY"""
        if DataFormatters._esta_vacio(fecha):
            return "--"
        
        try:
            # Si ya es datetime, formatear directamente
            if hasattr(fecha, 'strftime'):
                return fecha.strftime("%d/%m/%Y")
            
            # Si es string, intentar parsear
            if isinstance(fecha, str):
                # Intentar varios formatos comunes
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                    try:
                        parsed = pd.to_datetime(fecha, format=fmt)
                        return parsed.strftime("%d/%m/%Y")
                    except:
                        continue
                
                # Fallback: usar pandas to_datetime
                parsed = pd.to_datetime(fecha)
                return parsed.strftime("%d/%m/%Y")
            
            return str(fecha)
            
        except Exception as e:
            logger.warning(f"Error formateando fecha: {e} | Valor: {fecha}")
            return str(fecha)
    
    @staticmethod
    def _esta_vacio(value: Any) -> bool:
        """Verifica si un valor está vacío"""
        return value in ["--", "", None] or pd.isna(value)

    @staticmethod
    def extraer_descripcion_corta(descripcion_completa):
        """
        Extrae la descripción corta de una descripción completa.
        Soporta comas inconsistentes, espacios, saltos de línea.
        """
        if descripcion_completa in ["--", "", None] or pd.isna(descripcion_completa):
            return "--"

        try:
            texto = str(descripcion_completa).strip()

            # Normalizar separadores
            texto = texto.replace('\n', ' ').replace('  ', ' ')
            
            # Separar por coma
            partes = [p.strip() for p in texto.split(',') if p.strip()]

            # Si hay 3 o más partes, tomar desde la tercera
            if len(partes) >= 3:
                return ', '.join(partes[2:])

            # Si hay menos, devolver todo
            return texto

        except Exception as e:
            logger.warning(
                f"Error extrayendo descripcion corta: {e} | Valor: {descripcion_completa}"
            )
            return str(descripcion_completa).strip()
