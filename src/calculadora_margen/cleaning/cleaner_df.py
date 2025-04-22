import pandas as pd
from typing import Optional, List

class Cleaner:
    """
    Clase para aplicar operaciones de limpieza/transformación
    sobre un DataFrame de pandas de forma encadenada.
    """
    def __init__(self, df: pd.DataFrame):
        # Hacemos copia para no modificar el original por accidente
        self.df = df.copy()


    def keep_and_rename(self,
                        cols_to_keep: list[str],
                        rename_map: dict[str, str] = None
                       ) -> "Cleaner":
        """
        Conserva sólo las columnas en cols_to_keep y renómbralas según rename_map.

        Parámetros
        ----------
        cols_to_keep : list[str]
            Lista de nombres de columnas a conservar.
        rename_map : dict[str, str], opcional
            Mapeo {columna_original: nuevo_nombre}. Las claves deben
            estar dentro de cols_to_keep.


        """
        # Validación de rename_map
        if rename_map:
            invalid = set(rename_map) - set(cols_to_keep)
            if invalid:
                raise ValueError(f"Las claves {invalid} no están en cols_to_keep")

        # Filtramos y renombramos en un solo paso
        self.df = (
            self.df
            .loc[:, cols_to_keep]
            .rename(columns=rename_map or {})
        )
        return self
    

    def drop_duplicates(self,
                   subset: list[str] = None,
                   keep: str = 'first'
                  ) -> "Cleaner":
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        return self
    
    def drop_na(self,
                subset: list[str] = None
               ) -> "Cleaner":
        """
        Elimina filas que contienen valores NA en las columnas indicadas.

        Parámetros
        ----------
        subset : list[str], opcional
            Columnas a considerar para identificar NA. Si es None,
            se consideran todas las columnas.

        """
   
        self.df = self.df.dropna(subset=subset)
        return self
    


    def drop_duplicates_batch(self,
                                column: str = 'lote_interno'
                               ) -> "Cleaner":
        """
        Elimina duplicados en la columna especificada, manteniendo la última aparición.
        Por defecto usamos lote_interno porque los duplicados se producen por actualizaciones de precios. Entendemos que el correcto es el último.

        Parámetros
        ----------
        column : str
            Nombre de la columna donde buscar duplicados.
        """
        
        self.df = self.df.drop_duplicates(subset=[column], keep='last')
        return self




    def fix_numeric_format(self, cols: Optional[List[str]] = None) -> "Cleaner":
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
        self : Cleaner
            La misma instancia, con self.df actualizada.
        """
        if cols is not None:  # Solo procesar si hay columnas especificadas
            for col in cols:
                self.df[col] = (
                    self.df[col]
                    .astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .astype(float)
                )
        return self



    def get_df(self) -> pd.DataFrame:
        """Devuelve el DataFrame resultante tras las operaciones."""
        return self.df

