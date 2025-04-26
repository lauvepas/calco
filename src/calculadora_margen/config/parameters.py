from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd

@dataclass(frozen=True)
class DatasetParams:
    """
    Column parameters and validations for a dataset.

    Attributes:
        cols_to_keep: List of columns to retain
        rename_map: Dictionary to rename columns
        cols_to_float: Columns to convert to float (optional)
        validation_map: Dictionary {column: regex} for validation (optional)
        drop_na_subset: Columns for which to drop rows with NA (optional)
        drop_duplicates_subset: Column for removing duplicates, keeping the last (optional)
        outliers_value_column: Column containing values to analyze for outliers (optional)
        outliers_group_column: Column by which to group when detecting outliers (optional)
        outliers_z_score: Z-score threshold to consider an outlier (optional)
        outliers_min_threshold: Minimum number of outliers to continue iterating (optional)
        outliers_max_iterations: Maximum number of allowed iterations (optional)
        viz_date_column: Column for dates in visualizations (optional)
        viz_value_column: Column for values in visualizations (optional)
        viz_group_column: Column for grouping in visualizations (optional)
        viz_title: Title for the visualization (optional)
        viz_y_label: Y-axis label for the visualization (optional)
    """
    # Cleaning and validation parameters
    cols_to_keep: List[str]
    rename_map: Dict[str, str]
    cols_to_float: Optional[List[str]] = None
    validation_map: Optional[Dict[str, str]] = None
    drop_na_subset: Optional[List[str]] = None
    drop_duplicates_subset: Optional[str] = None
    # Outlier detection parameters
    outliers_value_column: Optional[str] = None
    outliers_group_column: Optional[str] = None
    outliers_z_score: float = 3.0
    outliers_min_threshold: int = 5
    outliers_max_iterations: int = 20
    # Visualization parameters
    viz_date_column: Optional[str] = None
    viz_value_column: Optional[str] = None
    viz_group_column: Optional[str] = None
    viz_title: Optional[str] = None
    viz_y_label: Optional[str] = None

class Parameters:
    """Centralizes the parameters for each CSV or dataset."""

  
    master_lotes = DatasetParams(
        cols_to_keep=['Cód. artículo', 'LOTE', 'LOTEINTERNO'],
        rename_map={
            'Cód. artículo': 'articulo',
            'LOTE': 'lote_proveedor',
            'LOTEINTERNO': 'lote_componente'
        },
        drop_na_subset=['lote_componente']   # rows without a component lot are not relevant for merging
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
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXT + 2-3 números
            'lote_componente': r'^[0-9]{4}-[0-9]{3}$'   # 1234-567
        },
        drop_na_subset=['PRCMONEDA'],   # drop rows without a price since they’re not useful
        drop_duplicates_subset='lote_componente',  # remove duplicate lots, keeping the last
        # Outlier detection parameters
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
            'articulo': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXT + 2-3 números
            'componente': r'^[A-Za-zÀ-ÖØ-öø-ÿ]+[0-9]{2,3}$',   # TEXT + 2-3 números
        },
        drop_na_subset=['lote_articulo', 'lote_componente']   # drop rows without lots since they aren’t fabricated or cost-assignable
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
        # Outlier detection parameters
        outliers_value_column='coste_unitario',
        outliers_group_column='articulo',
        outliers_z_score=3.0,
        outliers_min_threshold=5,
        outliers_max_iterations=20,
        # Visualization parameters
        viz_date_column='fecha_fabricacion',
        viz_value_column='coste_unitario',
        viz_group_column='articulo',
        viz_title='Evolución de Costes de Fabricación',
        viz_y_label='Coste Total (€)'
    )