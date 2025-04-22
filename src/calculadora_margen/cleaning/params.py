from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd

@dataclass(frozen=True)
class DatasetParams:
    """
    Parámetros de columnas y validaciones para un dataset.

    attrs:
        cols_to_keep: Lista de columnas a conservar.
        rename_map: Diccionario para renombrar columnas.
        cols_to_float: Columnas a convertir a float (opcional).
        validation_map: Diccionario {columna: regex} para validación in place (opcional).
    """
    cols_to_keep: List[str]
    rename_map: Dict[str, str]
    cols_to_float: Optional[List[str]] = None
    validation_map: Optional[Dict[str, str]] = None

class Parameters:
    """Centraliza los parámetros para cada CSV o dataset."""
    master_lotes = DatasetParams(
        cols_to_keep=['Cód. artículo', 'LOTE', 'LOTEINTERNO'],
        rename_map={
            'Cód. artículo': 'articulo',
            'LOTE': 'lote_proveedor',
            'LOTEINTERNO': 'lote_interno'
        }
    )

    costes = DatasetParams(
        cols_to_keep=[
            'Cód. artículo',
            'PRCMONEDA',
            'LOTEINTERNO'
        ],
        rename_map={
            'Cód. artículo': 'componente',
            'PRCMONEDA': 'coste_componente_unitario',
            'LOTEINTERNO': 'lote_interno'
        },
        cols_to_float=['coste_componente_unitario'],
        validation_map={
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
            'lote_interno': r'^[0-9]{4}-[0-9]{3}$'   # 1234-567
        }
    )


