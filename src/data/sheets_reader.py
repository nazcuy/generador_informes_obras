"""
Lector especializado para Google Sheets, Google Drive y APIs externas.
"""

from __future__ import annotations

import os
import io
import pandas as pd
import gspread
import requests
from typing import Optional, List, Dict, Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config.constants import Config
from utils.helpers import setup_logging

logger = setup_logging(__name__)


class SheetsReader:
    """Lector especializado para Google Sheets / Drive"""

    # =========================
    # API PÚBLICA
    # =========================

    @staticmethod
    def read_if_configured() -> Optional[pd.DataFrame]:
        """Lee Google Sheet solo si está configurado."""
        if not SheetsReader._is_configured():
            logger.info("[~] Google Sheets no configurado, saltando...")
            return None

        try:
            return SheetsReader.read_como_df(
                sheet_id=Config.GOOGLE_SHEET_ID_OBRAS,
                hoja_nombre=Config.GOOGLE_SHEET_NAME_OBRAS,
                columnas=Config.GOOGLE_COLUMNS
            )
        except Exception as e:
            logger.warning(f"[!] No se pudo leer Google Sheet: {e}")
            return None

    @staticmethod
    def read_como_df(
        sheet_id: str,
        hoja_nombre: Optional[str] = None,
        columnas: Optional[List[str]] = None
    ) -> pd.DataFrame:
        creds = SheetsReader._get_credentials(
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )

        df = None

        # 1️⃣ Intentar como Google Sheet nativo
        try:
            df = SheetsReader._leer_sheet_nativo(
                creds, sheet_id, hoja_nombre
            )
            logger.info("[OK] Leído como Google Sheet nativo")
        except Exception:
            logger.info("[~] No es Google Sheet nativo, intentando como Excel...")

            # 2️⃣ Fallback a Excel en Drive
            drive = build('drive', 'v3', credentials=creds)

            metadata = drive.files().get(
                fileId=sheet_id,
                fields='mimeType, name'
            ).execute()

            mime_type = metadata.get('mimeType', '')

            if 'spreadsheetml' in mime_type:
                df = SheetsReader._leer_excel_drive(
                    drive, sheet_id, hoja_nombre
                )
            else:
                raise ValueError(f"Tipo de archivo no soportado: {mime_type}")

        # 3️⃣ Filtrado de columnas
        if columnas:
            columnas_validas = [c for c in columnas if c in df.columns]
            df = df[columnas_validas]

        # 4️⃣ Normalización
        if 'ID' in df.columns and 'id_obra' not in df.columns:
            df.rename(columns={'ID': 'id_obra'}, inplace=True)

        logger.info(f"[OK] Archivo cargado: {len(df)} filas")
        return df

    @staticmethod
    def obtener_valor_celda(
        sheet_id: str,
        hoja_nombre: str,
        celda: str = 'I7'
    ) -> Optional[Any]:
        """Obtiene el valor de una celda de Google Sheets."""
        try:
            creds = SheetsReader._get_credentials(
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)
            ws = sh.worksheet(hoja_nombre)

            valor = ws.acell(celda).value
            logger.info(f"[OK] Celda {celda}: {valor}")
            return valor

        except Exception as e:
            logger.warning(f"[!] Error leyendo celda {celda}: {e}")
            return None

    @staticmethod
    def obtener_noticias_por_obra(
        sheet_id: str,
        hoja_noticias: str,
        id_obra: Any
    ) -> List[Dict[str, Any]]:
        """Obtiene noticias asociadas a una obra."""
        try:
            df = SheetsReader.read_como_df(
                sheet_id=sheet_id,
                hoja_nombre=hoja_noticias
            )
            # Normalizar nombres de columnas (todo lowercase, sin espacios)
            df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"), inplace=True)
            columnas=[
                    'id_obra',
                    'descripcion_municipio',
                    'diario',
                    'titulo_noticia',
                    'link_noticia',
                    'copete'
                ]
            df = df[[c for c in columnas if c in df.columns]]

            noticias = df[df['id_obra'] == id_obra].to_dict('records')
            logger.info(f"[OK] Noticias encontradas: {len(noticias)}")
            return noticias

        except Exception as e:
            logger.warning(f"[!] Error obteniendo noticias: {e}")
            return []

    @staticmethod
    def obtener_valor_uvi_api() -> Optional[str]:
        """Obtiene el valor UVI desde la API del BCRA."""
        try:
            url = "https://api.bcra.gob.ar/estadisticas/v2.0/PrincipalesVariables"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            for item in response.json().get('results', []):
                if item.get('idVariable') == 100:
                    valor = item.get('valor')
                    logger.info(f"[OK] UVI BCRA: {valor}")
                    return str(valor)

            return None

        except Exception as e:
            logger.warning(f"[!] Error consultando API BCRA: {e}")
            return None

    # =========================
    # MÉTODOS INTERNOS
    # =========================

    @staticmethod
    def _leer_sheet_nativo(
        creds,
        sheet_id: str,
        hoja_nombre: Optional[str]
    ) -> pd.DataFrame:
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet(hoja_nombre) if hoja_nombre else sh.get_worksheet(0)
        return pd.DataFrame(ws.get_all_records())

    @staticmethod
    def _leer_excel_drive(
        drive,
        file_id: str,
        hoja_nombre: Optional[str]
    ) -> pd.DataFrame:
        content = drive.files().get_media(fileId=file_id).execute()
        excel_file = io.BytesIO(content)
        xls = pd.ExcelFile(excel_file)

        sheet = hoja_nombre if hoja_nombre in xls.sheet_names else xls.sheet_names[0]
        return pd.read_excel(excel_file, sheet_name=sheet, header=7)

    @staticmethod
    def _get_credentials(scopes: List[str]) -> Credentials:
        if not SheetsReader._is_configured():
            raise ValueError("Google Sheets no configurado")

        return Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS,
            scopes=scopes
        )

    @staticmethod
    def _is_configured() -> bool:
        return bool(
            Config.GOOGLE_CREDENTIALS
            and os.path.exists(Config.GOOGLE_CREDENTIALS)
            and Config.GOOGLE_SHEET_ID_OBRAS
        )
