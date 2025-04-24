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
        """Devuelve el DataFrame resultante tras las operaciones."""
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

        Parámetros
        ----------
        cols_to_keep : list[str]
            Lista de nombres de columnas a conservar.
        rename_map : dict[str, str], opcional
            Mapeo {columna_original: nuevo_nombre}. Las claves deben
            estar dentro de cols_to_keep.

        Retorna
        -------
        self : ColumnsCleaner
            La misma instancia, con self.df actualizada.            
        """
        if rename_map:
            invalid = set(rename_map) - set(cols_to_keep)
            if invalid:
                raise ValueError(f"Las claves {invalid} no están en cols_to_keep")

        self.df = (
            self.df
            .loc[:, cols_to_keep]
            .rename(columns=rename_map or {})
        )
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
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        if self._parent:
            self._parent.df = self.df
        return self
    
    def drop_na(self,
                subset: list[str] = None
               ) -> "RowsCleaner":
        """
        Elimina filas que contienen valores NA en las columnas indicadas.

        Parámetros
        ----------
        subset : list[str], opcional
            Columnas a considerar para identificar NA. Si es None,
            se consideran todas las columnas.

        Retorna
        -------
        self : RowsCleaner
            La misma instancia, con self.df actualizada.            
        """
        self.df = self.df.dropna(subset=subset)
        if self._parent:
            self._parent.df = self.df
        return self

    def drop_duplicates_batch(self,
                            column: str = 'lote_interno'
                           ) -> "RowsCleaner":
        """
        Elimina duplicados en la columna especificada, manteniendo la última aparición.
        Por defecto usamos lote_interno porque los duplicados se producen por actualizaciones 
        de precios. Entendemos que el correcto es el último.

        Parámetros
        ----------
        column : str
            Nombre de la columna donde buscar duplicados.
        
        Retorna
        -------
        self : RowsCleaner
            La misma instancia, con self.df actualizada.            
        """
        self.df = self.df.drop_duplicates(subset=[column], keep='last')
        if self._parent:
            self._parent.df = self.df
        return self

class DataCleaner(BaseCleaner):
    """
    Clase especializada en operaciones de limpieza y transformación de datos.
    """
    def fix_numeric_format(self, cols: Optional[List[str]] = None) -> "DataCleaner":
        """
        Corrige el formato numérico en las columnas indicadas:
        elimina puntos de miles y reemplaza comas por puntos,
        luego convierte a float.

        Parámetros
        ----------
        cols : list[str], opcional
            Lista de columnas cuyos valores numéricos están en formato string.
            Si es None, no se realiza ninguna conversión.

        Retorna
        -------
        self : DataCleaner
            La misma instancia, con self.df actualizada.
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
        if self._parent:
            self._parent.df = self.df
        return self

    def to_upper(self) -> "DataCleaner":
        """
        Convierte a mayúsculas todos los valores no nulos del DataFrame.
        Preserva los valores nulos (NaN) para mantener la funcionalidad de pandas.

        Retorna
        -------
        self : DataCleaner
            La misma instancia, con self.df actualizada.            
        """
        for column in self.df.columns:
            if self.df[column].dtype == 'object':
                self.df[column] = self.df[column].apply(
                    lambda x: x.upper() if pd.notna(x) else x
                )
        if self._parent:
            self._parent.df = self.df
        return self

class DataFrameCleaner(BaseCleaner):
    """
    Clase fachada que proporciona acceso a todas las funcionalidades de limpieza.
    """
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
