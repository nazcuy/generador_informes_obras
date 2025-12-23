"""
Cálculos financieros específicos del dominio.
Lógica de negocio para UVIs, montos y avances.
"""

from __future__ import annotations

import pandas as pd
from typing import Union, Any
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class CalculosFinancieros:
    """Cálculos financieros específicos del dominio"""
    
    @staticmethod
    def calculate_remaining_uvi(total_uvi: Union[str, float, int], paid_uvi: Union[str, float, int]) -> str:
        """
        Calcula UVIs restantes: total - pagado.
        
        Args:
            total_uvi: Total de UVIs del convenio
            paid_uvi: UVIs ya pagadas
            
        Returns:
            String formateado con UVIs restantes
        """
        try:
            if CalculosFinancieros._is_empty(total_uvi) or CalculosFinancieros._is_empty(paid_uvi):
                return "--"
            
            # Limpiar y convertir
            total_clean = CalculosFinancieros._clean_numeric(total_uvi)
            paid_clean = CalculosFinancieros._clean_numeric(paid_uvi)
            
            # Calcular restantes
            remaining = total_clean - paid_clean
            
            # Asegurar que no sea negativo
            remaining = max(0, remaining)
            
            # Formatear como moneda sin decimales
            from .formatters import DataFormatters
            return DataFormatters.formatear_moneda_sin_decimales(remaining)
            
        except Exception as e:
            logger.warning(f"Error calculando UVIs restantes: {e} | Total: {total_uvi}, Pagado: {paid_uvi}")
            return "--"
    
    @staticmethod
    def calculate_remaining_amount(updated_amount: Union[str, float, int], paid_amount: Union[str, float, int]) -> str:
        """
        Calcula monto restante: monto_actualizado - monto_pagado.
        
        Args:
            updated_amount: Monto actualizado total
            paid_amount: Monto ya pagado
            
        Returns:
            String formateado con monto restante
        """
        try:
            if (CalculosFinancieros._is_empty(updated_amount) or 
                CalculosFinancieros._is_empty(paid_amount)):
                return "--"
            
            # Limpiar y convertir
            updated_clean = CalculosFinancieros._clean_numeric(updated_amount)
            paid_clean = CalculosFinancieros._clean_numeric(paid_amount)
            
            # Calcular restantes
            remaining = updated_clean - paid_clean
            
            # Asegurar que no sea negativo
            remaining = max(0, remaining)
            
            # Formatear como moneda sin decimales
            from .formatters import DataFormatters
            return DataFormatters.formatear_moneda_sin_decimales(remaining)
            
        except Exception as e:
            logger.warning(f"Error calculando monto restante: {e} | Actualizado: {updated_amount}, Pagado: {paid_amount}")
            return "--"
    
    @staticmethod
    def calculate_remaining_progress(current_progress: Union[str, float, int]) -> str:
        """
        Calcula progreso restante: 100% - progreso_actual.
        
        Args:
            current_progress: Porcentaje de avance actual
            
        Returns:
            String formateado con porcentaje restante
        """
        try:
            if CalculosFinancieros._is_empty(current_progress):
                return "--"
            
            # Limpiar y convertir
            progress_clean = CalculosFinancieros._clean_numeric(current_progress)
            
            # Si está entre 0 y 1, multiplicar por 100
            if 0 <= progress_clean <= 1:
                progress_clean *= 100
            
            # Calcular restante
            remaining = 100 - progress_clean
            
            # Asegurar que esté entre 0 y 100
            remaining = max(0, min(100, remaining))
            
            # Formatear como porcentaje
            from .formatters import DataFormatters
            return DataFormatters.formatear_porcentaje(remaining)
            
        except Exception as e:
            logger.warning(f"Error calculando progreso restante: {e} | Actual: {current_progress}")
            return "--"
    
    @staticmethod
    def calculate_remaining_houses(total_houses: Union[str, float, int], delivered_houses: Union[str, float, int]) -> str:
        """
        Calcula viviendas restantes: total - entregadas.
        
        Args:
            total_houses: Total de viviendas del proyecto
            delivered_houses: Viviendas ya entregadas
            
        Returns:
            String formateado con viviendas restantes
        """
        try:
            if (CalculosFinancieros._is_empty(total_houses) or 
                CalculosFinancieros._is_empty(delivered_houses)):
                return "--"
            
            # Limpiar y convertir
            total_clean = CalculosFinancieros._clean_numeric(total_houses)
            delivered_clean = CalculosFinancieros._clean_numeric(delivered_houses)
            
            # Calcular restantes
            remaining = total_clean - delivered_clean
            
            # Asegurar que no sea negativo
            remaining = max(0, remaining)
            
            # Formatear como número
            from .formatters import DataFormatters
            return DataFormatters.formatear_numero(remaining)
            
        except Exception as e:
            logger.warning(f"Error calculando viviendas restantes: {e} | Total: {total_houses}, Entregadas: {delivered_houses}")
            return "--"
    
    @staticmethod
    def _clean_numeric(value: Union[str, float, int]) -> float:
        """
        Limpia y convierte un valor a float.
        
        Args:
            value: Valor a limpiar
            
        Returns:
            Valor como float
        """
        if isinstance(value, str):
            # Remover separadores argentinos
            value = value.replace('.', '').replace(',', '.')
        
        return float(value)
    
    @staticmethod
    def _is_empty(value: Any) -> bool:
        """Verifica si un valor está vacío"""
        return value in ["--", "", None] or pd.isna(value)
