import pandas as pd
from typing import Optional, List
from abc import ABC, abstractmethod

class BaseCleaner(ABC):
    """
    Clase base abstracta para operaciones de limpieza/transformación
    sobre un DataFrame de pandas.
    """
    def __init__(self, df: pd.DataFrame, parent_cleaner=None):
        self.df = df.copy()
        self._parent = parent_cleaner
        self._initial_size = len(df)

    def _print_operation_summary(self, operation: str, details: dict):
        """Imprime un resumen de la operación realizada."""
        print(f"\n=== {operation.upper()} ===")
        for key, value in details.items():
            print(f"  {key}: {value}")
        if 'filas_eliminadas' in details:
            print(f"  Tamaño final del DataFrame: {len(self.df)}")

    @property
    def columns_cleaner(self):
        return ColumnsCleaner(self.df, self)

    @property
    def rows_cleaner(self):
        return RowsCleaner(self.df, self)

    @property
    def data_cleaner(self):
        return DataCleaner(self.df, self)

    def get_df(self) -> pd.DataFrame:
        """Devuelve el DataFrame resultante."""
        return self.df

class ColumnsCleaner(BaseCleaner):
    """
    Clase especializada en operaciones sobre columnas del DataFrame.
    """
    def keep_and_rename(self,
                       cols_to_keep: list[str],
                       rename_map: dict[str, str] = None
                      ) -> "ColumnsCleaner":
        """
        Conserva sólo las columnas en cols_to_keep y renómbralas según rename_map.
        """
        initial_cols = len(self.df.columns)
        
        if rename_map:
            invalid = set(rename_map) - set(cols_to_keep)
            if invalid:
                raise ValueError(f"Las claves {invalid} no están en cols_to_keep")

        self.df = (
            self.df
            .loc[:, cols_to_keep]
            .rename(columns=rename_map or {})
        )
        
        self._print_operation_summary("Selección y renombrado de columnas", {
            "columnas_iniciales": initial_cols,
            "columnas_finales": len(self.df.columns),
            "columnas_conservadas": cols_to_keep,
            "columnas_renombradas": rename_map or {}
        })
        
        if self._parent:
            self._parent.df = self.df
        return self

class RowsCleaner(BaseCleaner):
    """
    Clase especializada en operaciones sobre filas del DataFrame.
    """
    def drop_duplicates(self,
                       subset: list[str] = None,
                       keep: str = 'first'
                      ) -> "RowsCleaner":
        """
        Elimina filas duplicadas.
        """
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        
        self._print_operation_summary("Eliminación de duplicados", {
            "filas_eliminadas": initial_rows - len(self.df),
            "columnas_consideradas": subset or "todas",
            "criterio": f"mantener_{keep}"
        })
        
        if self._parent:
            self._parent.df = self.df
        return self
    
    def drop_na(self,
                subset: list[str] = None
               ) -> "RowsCleaner":
        """
        Elimina filas que contienen valores NA en las columnas indicadas.
        """
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=subset)
        
        self._print_operation_summary("Eliminación de valores NA", {
            "filas_eliminadas": initial_rows - len(self.df),
            "columnas_consideradas": subset or "todas"
        })
        
        if self._parent:
            self._parent.df = self.df
        return self

    def drop_duplicates_batch(self,
                            column: str = 'lote_interno'
                           ) -> "RowsCleaner":
        """
        Elimina duplicados en la columna especificada.
        """
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=[column], keep='last')
        
        self._print_operation_summary("Eliminación de duplicados por lote", {
            "columna": column,
            "filas_eliminadas": initial_rows - len(self.df)
        })
        
        if self._parent:
            self._parent.df = self.df
        return self

class DataCleaner(BaseCleaner):
    """
    Clase especializada en operaciones de limpieza y transformación de datos.
    """
    def fix_numeric_format(self, cols: Optional[List[str]] = None) -> "DataCleaner":
        """
        Corrige el formato numérico en las columnas indicadas.
        """
        if cols is not None:
            for col in cols:
                self.df[col] = (
                    self.df[col]
                    .astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .astype(float)
                )
            
            self._print_operation_summary("Corrección de formato numérico", {
                "columnas_procesadas": cols
            })
            
        if self._parent:
            self._parent.df = self.df
        return self

    def to_upper(self) -> "DataCleaner":
        """
        Convierte a mayúsculas todos los valores no nulos del DataFrame.
        """
        columns_processed = []
        for column in self.df.columns:
            if self.df[column].dtype == 'object':
                self.df[column] = self.df[column].apply(
                    lambda x: x.upper() if pd.notna(x) else x
                )
                columns_processed.append(column)
        
        if columns_processed:
            self._print_operation_summary("Conversión a mayúsculas", {
                "columnas_procesadas": columns_processed
            })
        
        if self._parent:
            self._parent.df = self.df
        return self

class DataFrameCleaner(BaseCleaner):
    """
    Clase fachada que proporciona acceso a todas las funcionalidades de limpieza.
    """
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self._columns_cleaner = None
        self._rows_cleaner = None
        self._data_cleaner = None

    @property
    def columns_cleaner(self):
        if self._columns_cleaner is None:
            self._columns_cleaner = ColumnsCleaner(self.df, self)
        return self._columns_cleaner

    @property
    def rows_cleaner(self):
        if self._rows_cleaner is None:
            self._rows_cleaner = RowsCleaner(self.df, self)
        return self._rows_cleaner

    @property
    def data_cleaner(self):
        if self._data_cleaner is None:
            self._data_cleaner = DataCleaner(self.df, self)
        return self._data_cleaner

    def get_df(self) -> pd.DataFrame:
        """Devuelve el DataFrame resultante."""
        return self.df

    def __repr__(self):
        """Asegura que el resumen se muestre cuando se imprime el objeto en un notebook."""
        self._print_operation_summary("Resumen de limpieza", {
            "initial_size": self._initial_size,
            "final_size": len(self.df)
        })
        return self.df.__repr__()

    def _repr_html_(self):
        """Asegura que el resumen se muestre cuando se muestra el DataFrame en HTML (notebooks)."""
        self._print_operation_summary("Resumen de limpieza", {
            "initial_size": self._initial_size,
            "final_size": len(self.df)
        })
        return self.df._repr_html_()