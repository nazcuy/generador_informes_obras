"""
Lector especializado para archivos Excel.
"""

from __future__ import annotations

import pandas as pd
from typing import Optional, List
from pathlib import Path

from config.constants import Config
from utils.helpers import setup_logging

logger = setup_logging(__name__)

class ExcelReader:
    """Lector especializado para archivos Excel"""
    
    @staticmethod
    def read_excel(path: Optional[str] = None) -> pd.DataFrame:
        """
        Lee archivo Excel con validación y manejo de errores.
        
        Args:
            path: Ruta al archivo Excel (opcional, usa Config.EXCEL_PATH por defecto)
            
        Returns:
            DataFrame con los datos del Excel
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si hay problemas de lectura
        """
        file_path = path or Config.EXCEL_PATH
        
        try:
            logger.info(f"[>] Leyendo Excel: {file_path}")
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info(f"[OK] Excel cargado: {len(df)} registros")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo Excel: {file_path}")
        except Exception as e:
            raise ValueError(f"Error leyendo Excel {file_path}: {e}")
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Valida que el DataFrame tenga las columnas requeridas.
        
        Args:
            df: DataFrame a validar
            required_columns: Lista de columnas requeridas
            
        Returns:
            True si es válido, False en caso contrario
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"[!] Columnas faltantes en Excel: {missing_columns}")
            return False
        
        logger.info(f"[OK] Validación de columnas exitosa")
        return True
    
    @staticmethod
    def filter_by_prefix(df: pd.DataFrame, column: str, prefix: str) -> pd.DataFrame:
        """
        Filtra DataFrame por prefijo en una columna específica.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna para filtrar
            prefix: Prefijo a buscar
            
        Returns:
            DataFrame filtrado
        """
        return df[df[column].str.startswith(prefix, na=False)]
    
    @staticmethod
    def exclude_by_prefix(df: pd.DataFrame, column: str, prefix: str) -> pd.DataFrame:
        """
        Excluye filas por prefijo en una columna específica.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna para filtrar
            prefix: Prefijo a excluir
            
        Returns:
            DataFrame filtrado
        """
        return df[~df[column].str.startswith(prefix, na=False)]
