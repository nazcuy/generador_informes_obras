#!/usr/bin/env python3
"""
Script principal para el generador de informes de obras.
Versión 2.0 - Refactorizada y modularizada.

Uso:
    python run.py [opciones]
    python run.py --filter OTRAS
    python run.py --excel mi_archivo.xlsx --output informes/
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

# Agregar el directorio del proyecto al path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.excel_reader import ExcelReader
from src.data.sheets_reader import SheetsReader
from src.processors.resources import ResourceProcessor
from src.pdf.generator import PDFGenerator
from utils.helpers import setup_logging, validate_environment, create_project_structure, get_project_info
from src.processors.saldo_calculator import SaldoCalculator
from src.processors.formatters import DataFormatters
from src.processors.calculations import CalculosFinancieros

logger = setup_logging(__name__)

def main():
    """Función principal del programa"""
    
    # Mostrar información del proyecto
    project_info = get_project_info()
    logger.info(f"🚀 {project_info['name']} v{project_info['version']}")
    logger.info(f"📁 Directorio: {project_info['root_directory']}")
    
    # Crear estructura de directorios si no existe
    create_project_structure()
    
    # Validar entorno
    if not validate_environment():
        logger.error("❌ Problemas de configuración encontrados. Revisar configuración.")
        return 1
    
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Generador automatizado de informes PDF para obras públicas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run.py                                    # Ejecutar con configuración por defecto
  python run.py --filter OTRAS                    # Solo obras con prefijo 'OTRAS-'
  python run.py --excel mi_archivo.xlsx           # Usar archivo Excel específico
  python run.py --output mis_informes/            # Cambiar directorio de salida
  python run.py --help                            # Ver todas las opciones
        """
    )
    
    parser.add_argument(
        "--excel", 
        help="Ruta al archivo Excel con datos de obras"
    )
    
    parser.add_argument(
        "--output", 
        default="informes",
        help="Directorio de salida para los PDFs (default: informes)"
    )
    
    parser.add_argument(
        "--filter",
        choices=["OTRAS", "CONVE", "TODAS"],
        default="OTRAS",
        help="Filtro de obras por prefijo (default: OTRAS)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ejecutar en modo verbose (DEBUG)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular ejecución sin generar PDFs"
    )
    
    args = parser.parse_args()
    
    # Configurar logging según argumentos
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Banner de inicio
    logger.info("=" * 60)
    logger.info("🎯 GENERADOR DE INFORMES DE OBRAS PÚBLICAS")
    logger.info("=" * 60)
    
    try:
        # 1. CARGAR DATOS
        logger.info("[1/4] 📥 Cargando datos...")
        
        # Leer Excel
        df_excel = ExcelReader.read_excel(args.excel)
        
        # Leer Google Sheets si está configurado
        df_sheets = SheetsReader.read_if_configured()
        
        # 2. COMBINAR DATOS
        logger.info("[2/4] 🔄 Combinando fuentes de datos...")
        
        if df_sheets is not None:
            # Merge por id_obra (left join: mantiene todas las filas de Excel)
            df_combined = df_excel.merge(
                df_sheets, 
                on='id_obra', 
                how='left', 
                suffixes=('_excel', '_sheets')
            )
            logger.info(f"[OK] Datos combinados: {len(df_combined)} registros")
        else:
            df_combined = df_excel
            logger.info("[OK] Solo datos de Excel")
        
        # 3. CALCULAR SALDOS CON UVI DEL BCRA
        logger.info("[🔄] Calculando saldos de obra con UVI del BCRA...")
        
        # Convertir DataFrame a lista de diccionarios para procesar
        obras_data = df_combined.to_dict('records')
        
        # Inicializar calculadora de saldos
        calculadora = SaldoCalculator()
        
        # Procesar todas las obras con el valor UVI del día
        obras_con_saldo = calculadora.procesar_lote(obras_data)
        
        # 4. PREPARAR RECURSOS
        logger.info("[3/4] 🎨 Preparando recursos visuales...")
        resources = ResourceProcessor.prepare_all()
        
        # Procesar imágenes de obras para cada registro
        logger.info("[🔄] Procesando imágenes de obras...")
        for idx, row in df_combined.iterrows():
            obra_id = str(row.get('id_obra', '')).strip()
            if obra_id and obra_id not in ['--', '']:
                obra_images = ResourceProcessor.get_work_images(obra_id)
                resources[f'obra_images_{idx}'] = obra_images
        
        # Formatear campos necesarios para cada obra
        obras_procesadas = []
        for obra in obras_con_saldo:
            obra_procesada = {}
            
            # Copiar todos los campos originales
            obra_procesada.update(obra)
            
            # Formatear campos específicos
            if 'Total_UVI' in obra:
                obra_procesada['Total_UVI'] = DataFormatters.formatear_numero(obra['Total_UVI'])
            
            # Calcular avance restante si no existe
            if 'Avance_fisico' in obra and 'Avance_Restante' not in obra:
                obra_procesada['Avance_Restante'] = CalculosFinancieros.calculate_progreso_restante(
                    obra.get('Avance_fisico', '--')
                )
            
            # Asegurar que Saldo_Obra_Actualizado esté presente
            if 'Saldo_Obra_Actualizado' not in obra_procesada:
                obra_procesada['Saldo_Obra_Actualizado'] = "--"
            
            # Asegurar formato de otros campos clave para el template
            campos_a_formatear = {
                'Viviendas_Totales': 'formatear_numero',
                'Viviendas_Entregadas': 'formatear_numero',
                'Monto_Convenio': 'formatear_moneda_sin_decimales',
                'Saldo_UVI_Pendiente': 'formatear_numero',
                'Uvis_Restantes': 'formatear_numero'
            }
            
            for campo, formateador in campos_a_formatear.items():
                if campo in obra and obra[campo] not in ['--', '', None]:
                    try:
                        if formateador == 'formatear_numero':
                            obra_procesada[campo] = DataFormatters.formatear_numero(obra[campo])
                        elif formateador == 'formatear_moneda_sin_decimales':
                            obra_procesada[campo] = DataFormatters.formatear_moneda_sin_decimales(obra[campo])
                    except Exception as e:
                        logger.warning(f"Error formateando {campo}: {e}")
                        obra_procesada[campo] = obra.get(campo, '--')
            
            obras_procesadas.append(obra_procesada)
        
        # 4. GENERAR PDFs
        logger.info("[4/4] 📄 Generando informes PDF...")
        
        if args.dry_run:
            logger.info("[SIMULACIÓN] Modo dry-run activado. No se generarán PDFs.")
            logger.info(f"[SIMULACIÓN] Se procesarían {len(df_combined)} obras")
            logger.info(f"[SIMULACIÓN] Filtro: {args.filter}")
            logger.info(f"[SIMULACIÓN] Directorio: {args.output}")
        else:
            # Crear generador de PDFs
            generator = PDFGenerator(resources, args.output)
            
            # Generar todos los PDFs
            generator.generate_all(df_combined, args.filter)
        
        # Mensaje de finalización exitosa
        logger.info("=" * 60)
        logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 60)
        
        if not args.dry_run:
            output_path = Path(args.output).resolve()
            logger.info(f"📁 Informes generados en: {output_path}")
            logger.info(f"🔍 Total de registros procesados: {len(df_combined)}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Proceso interrumpido por el usuario")
        return 1
        
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        logger.debug("Detalles del error:", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
