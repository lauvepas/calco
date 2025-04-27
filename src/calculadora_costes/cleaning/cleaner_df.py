import pandas as pd
from typing import Optional, List
from abc import ABC, abstractmethod

class BaseCleaner(ABC):
    """
    Abstract base class for cleaning/transformation operations on a pandas DataFrame.
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
        """Returns the resulting DataFrame after operations."""
        return self.df

class ColumnsCleaner(BaseCleaner):
    """
    Specialized class for column operations on the DataFrame.
    """
    def keep_and_rename(self,
                       cols_to_keep: list[str],
                       rename_map: dict[str, str] = None
                      ) -> "ColumnsCleaner":
        """
        Keeps only the columns in cols_to_keep and renames them according to rename_map.

        Parameters
        ----------
        cols_to_keep : list[str]
            List of column names to keep.
        rename_map : dict[str, str], optional
            Mapping {original_column: new_name}. Keys must be within cols_to_keep.

        Returns
        -------
        self : ColumnsCleaner
            The same instance, with self.df updated.
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
    Specialized class for row operations on the DataFrame.
    """
    def drop_duplicates(self,
                       subset: list[str] = None,
                       keep: str = 'first'
                      ) -> "RowsCleaner":
        """
        Removes duplicate rows.

        Parameters
        ----------
        subset : list[str], optional
            Columns to consider for identifying duplicates.
        keep : str, optional
            Determines which duplicate rows to keep.

        Returns
        -------
        self : RowsCleaner
            The same instance, with self.df updated.
        """
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        if self._parent:
            self._parent.df = self.df
        return self
    
    def drop_na(self,
                subset: list[str] = None
               ) -> "RowsCleaner":
        """
        Removes rows containing NA values in the specified columns.

        Parameters
        ----------
        subset : list[str], optional
            Columns to consider for identifying NA. If None,
            all columns are considered.

        Returns
        -------
        self : RowsCleaner
            The same instance, with self.df updated.
        """
        self.df = self.df.dropna(subset=subset)
        if self._parent:
            self._parent.df = self.df
        return self

    def drop_duplicates_batch(self,
                            column: str = 'lote_interno'
                           ) -> "RowsCleaner":
        """
        Removes duplicates in the specified column, keeping the last occurrence.
        By default, we use lote_interno because duplicates occur due to price updates.
        We assume the correct one is the last.

        Parameters
        ----------
        column : str
            Name of the column in which to search for duplicates.
        
        Returns
        -------
        self : RowsCleaner
            The same instance, with self.df updated.
        """
        self.df = self.df.drop_duplicates(subset=[column], keep='last')
        if self._parent:
            self._parent.df = self.df
        return self

class DataCleaner(BaseCleaner):
    """
    Specialized class for data cleaning and transformation operations.
    """
    def fix_numeric_format(self, cols: Optional[List[str]] = None) -> "DataCleaner":
        """
        Fixes numeric format in the specified columns:
        removes thousand separators and replaces commas with dots,
        then converts to float.

        Parameters
        ----------
        cols : list[str], optional
            List of columns whose numeric values are in string format.
            If None, no conversion is performed.

        Returns
        -------
        self : DataCleaner
            The same instance, with self.df updated.
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
        Converts all non-null DataFrame values to uppercase.
        Preserves null values (NaN) to maintain pandas functionality.

        Parameters
        ----------
        None

        Returns
        -------
        self : DataCleaner
            The same instance, with self.df updated.
        """
        for column in self.df.columns:
            if self.df[column].dtype == 'object':
                self.df[column] = self.df[column].apply(
                    lambda x: x.upper() if pd.notna(x) else x
                )
        if self._parent:
            self._parent.df = self.df
        return self
    
    def fix_date_format(self, cols: List[str], format: str = '%d/%m/%Y') -> "DataCleaner":
        """
        Converts the specified columns to datetime format.
        
        Parameters
        ----------
        cols : List[str]
            List of columns containing dates.
        format : str, optional
            Date format of input data, default '%d/%m/%Y'.
            
        Returns
        -------
        DataCleaner
            The current cleaner instance.
        """
        for col in cols:
            try:
                self.df[col] = pd.to_datetime(
                    self.df[col],
                    format=format,
                    errors='coerce'
                )
            except Exception as e:
                print(f"Error al convertir la columna {col}: {e}")
        
        if self._parent:
            self._parent.df = self.df
        return self


class DataFrameCleaner(BaseCleaner):
    """
    Facade class that provides access to all cleaning functionalities.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to clean.
    
    Returns
    -------
    DataFrameCleaner
        The cleaner instance.
    """
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
