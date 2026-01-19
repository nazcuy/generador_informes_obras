"""
Cálculos financieros específicos del dominio.
Lógica de negocio para UVIs, montos y avances.
"""

from __future__ import annotations

import pandas as pd
from typing import Union, Any, Optional
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class CalculosFinancieros:
    """Cálculos financieros específicos del dominio"""
    
    @staticmethod
    def calcular_uvi_restantes(total_uvi: Union[str, float, int], paid_uvi: Union[str, float, int]) -> str:
        """
        Calcula UVIs restantes: total - pagado.
        
        Args:
            total_uvi: Total de UVIs del convenio
            paid_uvi: UVIs ya pagadas
            
        Returns:
            String formateado con UVIs restantes
        """
        try:
            if CalculosFinancieros._esta_vacio(total_uvi) or CalculosFinancieros._esta_vacio(paid_uvi):
                return "--"
            
            # Limpiar y convertir
            total_clean = CalculosFinancieros._numero_limpio(total_uvi)
            paid_clean = CalculosFinancieros._numero_limpio(paid_uvi)
            
            # Calcular restantes
            restantes = total_clean - paid_clean
            
            # Asegurar que no sea negativo
            restantes = max(0, restantes)
            
            # Formatear como moneda sin decimales
            from .formatters import DataFormatters
            return DataFormatters.formatear_numero(restantes)
            
        except Exception as e:
            logger.warning(f"Error calculando UVIs restantes: {e} | Total: {total_uvi}, Pagado: {paid_uvi}")
            return "--"
    
    @staticmethod
    def calcular_monto_restante(updated_monto: Union[str, float, int], paid_monto: Union[str, float, int]) -> str:
        """
        Calcula monto restante: monto_actualizado - monto_pagado.
        
        Args:
            updated_monto: Monto actualizado total
            paid_monto: Monto ya pagado
            
        Returns:
            String formateado con monto restante
        """
        try:
            if (CalculosFinancieros._esta_vacio(updated_monto) or 
                CalculosFinancieros._esta_vacio(paid_monto)):
                return "--"
            
            # Limpiar y convertir
            updated_clean = CalculosFinancieros._numero_limpio(updated_monto)
            paid_clean = CalculosFinancieros._numero_limpio(paid_monto)
            
            # Calcular restantes
            restantes = updated_clean - paid_clean
            
            # Asegurar que no sea negativo
            restantes = max(0, restantes)
            
            # Formatear como moneda sin decimales
            from .formatters import DataFormatters
            return DataFormatters.formatear_moneda_sin_decimales(restantes)
            
        except Exception as e:
            logger.warning(f"Error calculando monto restante: {e} | Actualizado: {updated_monto}, Pagado: {paid_monto}")
            return "--"
    
    @staticmethod
    def calculate_progreso_restante(current_progreso: Union[str, float, int]) -> str:
        """
        Calcula progreso restante: 100% - progreso_actual.
        
        Args:
            current_progreso: Porcentaje de avance actual
            
        Returns:
            String formateado con porcentaje restante
        """
        try:
            if CalculosFinancieros._esta_vacio(current_progreso):
                return "--"
            
            # Limpiar y convertir
            progreso_clean = CalculosFinancieros._numero_limpio(current_progreso)
            
            # Si está entre 0 y 1, multiplicar por 100
            if 0 <= progreso_clean <= 1:
                progreso_clean *= 100
            
            # Calcular restante
            restantes = 100 - progreso_clean
            
            # Asegurar que esté entre 0 y 100
            restantes = max(0, min(100, restantes))
            
            # Formatear como porcentaje
            from .formatters import DataFormatters
            return DataFormatters.formatear_porcentaje(restantes)
            
        except Exception as e:
            logger.warning(f"Error calculando progreso restante: {e} | Actual: {current_progreso}")
            return "--"
    
    @staticmethod
    def calculo_viviendas_restantes(total_viviendas: Union[str, float, int], delivered_viviendas: Union[str, float, int]) -> str:
        """
        Calcula viviendas restantes: total - entregadas.
        
        Args:
            total_viviendas: Total de viviendas del proyecto
            delivered_viviendas: Viviendas ya entregadas
            
        Returns:
            String formateado con viviendas restantes
        """
        try:
            if (CalculosFinancieros._esta_vacio(total_viviendas) or 
                CalculosFinancieros._esta_vacio(delivered_viviendas)):
                return "--"
            
            # Limpiar y convertir
            total_clean = CalculosFinancieros._numero_limpio(total_viviendas)
            delivered_clean = CalculosFinancieros._numero_limpio(delivered_viviendas)
            
            # Calcular restantes
            restantes = total_clean - delivered_clean
            
            # Asegurar que no sea negativo
            restantes = max(0, restantes)
            
            # Formatear como número
            from .formatters import DataFormatters
            return DataFormatters.formatear_numero(restantes)
            
        except Exception as e:
            logger.warning(f"Error calculando viviendas restantes: {e} | Total: {total_viviendas}, Entregadas: {delivered_viviendas}")
            return "--"
    
    @staticmethod
    def _numero_limpio(value: Union[str, float, int]) -> float:
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
    def _esta_vacio(value: Any) -> bool:
        """Verifica si un valor está vacío"""
        return value in ["--", "", None] or pd.isna(value)

class CalculosUVI:
    """Cálculos específicos con valor UVI actualizado del BCRA"""
    
    @staticmethod
    def calcular_saldo_actualizado(
        cantidad_uvis: Union[str, float, int], 
        valor_uvi_actual: Union[str, float, int, None]
    ) -> str:
        """
        Calcula saldo actualizado: cantidad_uvis * valor_uvi_diario.
        
        Args:
            cantidad_uvis: Cantidad de UVIs del proyecto (puede ser string o número)
            valor_uvi_actual: Valor diario de la UVI obtenido del BCRA
            
        Returns:
            String formateado como moneda, o "--" si no hay datos
        """
        try:
            # Verificar si tenemos los datos necesarios
            if (CalculosFinancieros._esta_vacio(cantidad_uvis) or 
                valor_uvi_actual is None or 
                CalculosFinancieros._esta_vacio(valor_uvi_actual)):
                logger.warning("Datos insuficientes para cálculo de saldo actualizado")
                return "--"
            
            # Limpiar y convertir valores
            cantidad_limpia = CalculosFinancieros._numero_limpio(cantidad_uvis)
            valor_uvi_limpio = float(valor_uvi_actual) if isinstance(valor_uvi_actual, (int, float, str)) else 0
            
            if valor_uvi_limpio <= 0:
                logger.warning(f"Valor UVI inválido: {valor_uvi_actual}")
                return "--"
            
            # Calcular saldo actualizado
            saldo_actualizado = cantidad_limpia * valor_uvi_limpio
            
            # Formatear como moneda
            from .formatters import DataFormatters
            return DataFormatters.formatear_moneda_sin_decimales(saldo_actualizado)
            
        except Exception as e:
            logger.error(f"Error calculando saldo actualizado: {e}")
            return "--"
    
    @staticmethod
    def obtener_valor_uvi_diario() -> Optional[float]:
        """
        Obtiene el valor diario de la UVI desde el BCRA.
        Integra con el método existente en SheetsReader.
        
        Returns:
            Valor de la UVI como float, o None si no se puede obtener
        """
        try:
            from src.data.sheets_reader import SheetsReader
            valor_uvi_str = SheetsReader.obtener_valor_uvi_api()
            
            if valor_uvi_str:
                # Limpiar y convertir a float
                return float(str(valor_uvi_str).replace(',', '.'))
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo valor UVI: {e}")
            return None

class CalculosSaldoObra:
    """Cálculos específicos para saldo de obra actualizado con UVI"""
    
    @staticmethod
    def calcular_saldo_obra_actualizado(
        total_uvi: Union[str, float, int], 
        valor_uvi_actual: Union[str, float, int, None]
    ) -> str:
        """
        Calcula saldo de obra actualizado: Total_UVI * Valor_UVI_Diario.
        
        Args:
            total_uvi: Total de UVIs del convenio (campo Total_UVI)
            valor_uvi_actual: Valor diario de la UVI obtenido del BCRA
            
        Returns:
            String formateado como moneda, o "--" si no hay datos
        """
        try:
            # Validar datos de entrada
            if (CalculosFinancieros._esta_vacio(total_uvi) or 
                valor_uvi_actual is None or 
                CalculosFinancieros._esta_vacio(valor_uvi_actual)):
                logger.warning("Datos insuficientes para cálculo de saldo")
                return "--"
            
            # Limpiar y convertir valores
            total_uvi_limpio = CalculosFinancieros._numero_limpio(total_uvi)
            valor_uvi_limpio = float(valor_uvi_actual) if isinstance(valor_uvi_actual, (int, float, str)) else 0
            
            if valor_uvi_limpio <= 0:
                logger.warning(f"Valor UVI inválido o cero: {valor_uvi_actual}")
                return "--"
            
            # Calcular saldo actualizado: TOTAL_UVI * VALOR_UVI_DIARIO
            saldo_actualizado = total_uvi_limpio * valor_uvi_limpio
            
            # Formatear como moneda sin decimales (igual que otros montos)
            from .formatters import DataFormatters
            return DataFormatters.formatear_moneda_sin_decimales(saldo_actualizado)
            
        except Exception as e:
            logger.error(f"Error calculando saldo de obra: {e} | Total_UVI: {total_uvi}, Valor_UVI: {valor_uvi_actual}")
            return "--"
    
    @staticmethod
    def obtener_valor_uvi_diario() -> Optional[float]:
        """
        Obtiene el valor diario de la UVI desde el BCRA.
        Reutiliza el método existente en SheetsReader.
        
        Returns:
            Valor de la UVI como float, o None si no se puede obtener
        """
        try:
            from src.data.sheets_reader import SheetsReader
            valor_uvi_str = SheetsReader.obtener_valor_uvi_api()
            
            if valor_uvi_str:
                # Convertir a float manejando formato argentino
                valor_limpio = str(valor_uvi_str).replace('.', '').replace(',', '.')
                return float(valor_limpio)
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo valor UVI diario: {e}")
            return None