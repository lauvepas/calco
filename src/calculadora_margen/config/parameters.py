from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd

@dataclass(frozen=True)
class DatasetParams:
    """
    Parámetros de columnas y validaciones para un dataset.

    attrs:
        cols_to_keep: Lista de columnas a conservar
        rename_map: Diccionario para renombrar columnas
        cols_to_float: Columnas a convertir a float (opcional)
        validation_map: Diccionario {columna: regex} para validación (opcional)
        drop_na_subset: Columnas para las que eliminar filas con NA (opcional)
        drop_duplicates_subset: Columna para eliminar duplicados manteniendo el último (opcional)
        outliers_value_column: Columna que contiene los valores a analizar para outliers (opcional)
        outliers_group_column: Columna por la que agrupar para detectar outliers (opcional)
        outliers_z_score: Umbral de z-score para considerar outlier (opcional)
        outliers_min_threshold: Mínimo número de outliers para seguir iterando (opcional)
        outliers_max_iterations: Máximo número de iteraciones permitidas (opcional)
    """
    # Parámetros de cleaning y validaciones
    cols_to_keep: List[str]
    rename_map: Dict[str, str]
    cols_to_float: Optional[List[str]] = None
    validation_map: Optional[Dict[str, str]] = None
    drop_na_subset: Optional[List[str]] = None
    drop_duplicates_subset: Optional[str] = None
    # Parámetros de outliers
    outliers_value_column: Optional[str] = None
    outliers_group_column: Optional[str] = None
    outliers_z_score: float = 3.0
    outliers_min_threshold: int = 5
    outliers_max_iterations: int = 20
    # Parámetros de visualización
    viz_date_column: Optional[str] = None
    viz_value_column: Optional[str] = None
    viz_group_column: Optional[str] = None
    viz_title: Optional[str] = None
    viz_y_label: Optional[str] = None

class Parameters:
    """Centraliza los parámetros para cada CSV o dataset."""

  
    master_lotes = DatasetParams(
        cols_to_keep=['Cód. artículo', 'LOTE', 'LOTEINTERNO'],
        rename_map={
            'Cód. artículo': 'articulo',
            'LOTE': 'lote_proveedor',
            'LOTEINTERNO': 'lote_componente'
        },
        drop_na_subset=['lote_componente']   # sin lote no nos interesa para merge
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
        },
        drop_na_subset=['PRCMONEDA'],   # si no tiene precio, no nos interesa
        drop_duplicates_subset='lote_componente',  # eliminamos duplicados en lote manteniendo el último
        # Parámetros de outliers
        outliers_value_column='coste_componente_unitario',
        outliers_group_column='componente',
        outliers_z_score=3.0,
        outliers_min_threshold=5,
        outliers_max_iterations=20
    )


    fabricaciones = DatasetParams(
        cols_to_keep=[
            'Nº Orden',
            'Fecha Recepción',
            'Producto',
            'Lote Producto',
            'Unidades Fabricadas',
            'Componente',
            'lote_componente_x',
            'coste_componente_unitario',
            'Consumo Unitario',
            'Consumo Total'
        ],
        rename_map={
            'Nº Orden': 'id_orden',
            'Fecha Recepción': 'fecha_fabricacion',
            'Producto': 'articulo',
            'Lote Producto': 'lote_articulo',
            'Unidades Fabricadas':'unidades_fabricadas',
            'Componente': 'componente',
            'lote_componente_x': 'lote_componente',
            'coste_componente_unitario': 'coste_componente_unitario',
            'Consumo Unitario': 'consumo_unitario',
            'Consumo Total': 'consumo_total'
        },
        cols_to_float=['unidades_fabricadas', 'consumo_unitario', 'consumo_total'],
        validation_map={
            'articulo': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXTO + 2-3 números
        },
        drop_na_subset=['lote_articulo', 'lote_componente']   # sin lote no se ha fabricado ni le podemos asociar coste
    )

    costes_fabricacion = DatasetParams(
        cols_to_keep=['id_orden', 'fecha_fabricacion', 'articulo', 'unidades_fabricadas', 'coste_unitario'],
        rename_map={
            'id_orden': 'id_orden',
            'fecha_fabricacion': 'fecha_fabricacion',
            'articulo': 'articulo',
            'unidades_fabricadas': 'unidades_fabricadas',
            'coste_unitario': 'coste_unitario'
        },
        # Parámetros de outliers
        outliers_value_column='coste_unitario',
        outliers_group_column='articulo',
        outliers_z_score=3.0,
        outliers_min_threshold=5,
        outliers_max_iterations=20,
        # Parámetros de visualización
        viz_date_column='fecha_fabricacion',
        viz_value_column='coste_unitario',
        viz_group_column='articulo',
        viz_title='Evolución de Costes de Fabricación',
        viz_y_label='Coste Total (€)'
    )