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
            'LOTEINTERNO': 'lote_componente'
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
            'LOTEINTERNO': 'lote_componente'
        },
        cols_to_float=['coste_componente_unitario'],
        validation_map={
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
            'lote_componente': r'^[0-9]{4}-[0-9]{3}$'   # 1234-567
        }
    )

    fabricaciones = DatasetParams(
        cols_to_keep=[
            'Fecha Recepción',
            'Producto',
            'Lote Producto',
            'Unidades Fabricadas',
            'Componente',
            'Lote Componente',
            'Consumo Unitario',
            'Consumo Total', 
            'Nº Orden'
        ],
        rename_map={
            'Fecha Recepción': 'fecha_fabricacion',
            'Producto': 'articulo',
            'Lote Producto': 'lote_articulo',
            'Componente': 'componente',
            'Lote Componente': 'lote_componente_proveedor',
            'Consumo Unitario': 'consumo_unitario',
            'Consumo Total': 'consumo_total',
            'Unidades Fabricadas':'unidades_fabricadas',
            'Nº Orden': 'id_orden'
        },
        cols_to_float=['unidades_fabricadas', 'consumo_unitario', 'consumo_total'],
        validation_map={
            'articulo': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
        }
    )
