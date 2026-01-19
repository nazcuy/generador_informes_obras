"""
Procesador especializado para cálculo de saldo con UVI del BCRA.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from utils.helpers import setup_logging
from .calculations import CalculosSaldoObra

logger = setup_logging(__name__)

class SaldoCalculator:
    """Calcula y agrega el saldo actualizado a los datos de cada obra"""
    
    def __init__(self):
        self.valor_uvi_diario = None
    
    def obtener_valor_uvi(self) -> Optional[float]:
        """Obtiene el valor UVI del día (con caché por ejecución)"""
        if self.valor_uvi_diario is None:
            self.valor_uvi_diario = CalculosSaldoObra.obtener_valor_uvi_diario()
            
            if self.valor_uvi_diario:
                logger.info(f"[OK] Valor UVI diario obtenido: {self.valor_uvi_diario}")
            else:
                logger.warning("[!] No se pudo obtener valor UVI diario")
                
        return self.valor_uvi_diario
    
    def procesar_obra(self, obra_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una obra individual, calculando su saldo actualizado.
        
        Args:
            obra_data: Diccionario con datos de la obra
            
        Returns:
            Diccionario con campo 'Saldo_Obra_Actualizado' agregado
        """
        try:
            # Obtener valor UVI del día
            valor_uvi = self.obtener_valor_uvi()
            
            # Obtener Total_UVI de la obra
            total_uvi = obra_data.get('Total_UVI', 
                           obra_data.get('total_uvi', 
                           obra_data.get('UVI_Total', '--')))
            
            # Calcular saldo actualizado usando CalculosSaldoObra
            saldo_actualizado = CalculosSaldoObra.calcular_saldo_obra_actualizado(
                total_uvi=total_uvi,
                valor_uvi_actual=valor_uvi
            )
            
            # Agregar al diccionario de datos
            obra_data['Saldo_Obra_Actualizado'] = saldo_actualizado
            
            # También agregar el valor UVI diario para referencia
            if valor_uvi:
                obra_data['Valor_UVI_Diario'] = valor_uvi
                obra_data['Valor_UVI_Diario_Formateado'] = f"${valor_uvi:,.2f}"
            
            logger.debug(f"Saldo calculado para obra {obra_data.get('ID_obra', 'N/A')}: {saldo_actualizado}")
            
        except Exception as e:
            logger.error(f"Error procesando obra: {e}")
            obra_data['Saldo_Obra_Actualizado'] = "--"
        
        return obra_data
    
    def procesar_lote(self, obras_data: list) -> list:
        """
        Procesa múltiples obras de manera eficiente.
        
        Args:
            obras_data: Lista de diccionarios con datos de obras
            
        Returns:
            Lista de obras con campo 'Saldo_Obra_Actualizado' agregado
        """
        logger.info(f"[>] Calculando saldos actualizados para {len(obras_data)} obras")
        
        # Obtener valor UVI una sola vez para todo el lote
        valor_uvi = self.obtener_valor_uvi()
        
        if not valor_uvi:
            logger.error("[!] No se pudo obtener valor UVI. Todos los saldos serán '--'")
            for obra in obras_data:
                obra['Saldo_Obra_Actualizado'] = "--"
            return obras_data
        
        # Procesar cada obra
        obras_procesadas = []
        for obra in obras_data:
            obras_procesadas.append(self.procesar_obra(obra))
        
        logger.info(f"[OK] Saldos calculados: {len(obras_procesadas)} obras")
        return obras_procesadas