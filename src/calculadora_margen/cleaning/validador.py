import re
import pandas as pd
from typing import Optional, Dict

class Validator:
    """
    Valida y filtra filas de un DataFrame según expresiones regulares.
    Trabaja sobre una copia del DataFrame original.
    """
    def __init__(self, df: pd.DataFrame):
        # Hacemos copia para no modificar el original por accidente
        self.df = df.copy()
        # Guardará las filas inválidas por columna
        self.invalid = {}

    def validate_with_map(self, validation_map: Optional[Dict[str, str]] = None) -> 'Validator':
        """
        Valida las columnas según el diccionario de validaciones proporcionado.

        Parámetros
        ----------
        validation_map : Dict[str, str], opcional
            Diccionario {columna: patron_regex} con las validaciones a aplicar.

        Retorna
        -------
        self : Validator
        """
        if validation_map:
            print(f"Tamaño inicial del DataFrame: {len(self.df)}")
            for column, pattern in validation_map.items():
                if column in self.df.columns:
                    print(f"\nValidando columna: {column}")
                    # Compilar el patrón para eficiencia
                    compiled = re.compile(pattern)
                    # Aplicar fullmatch usando re
                    mask = self.df[column].astype(str).apply(lambda x: bool(compiled.fullmatch(x)))
                    # Filas inválidas
                    invalid_rows = self.df[~mask].copy()
                    print(f"Filas inválidas encontradas: {len(invalid_rows)}")
                    
                    if not invalid_rows.empty:
                        # Guardar las filas inválidas
                        self.invalid[column] = invalid_rows
                        # Mantener solo las filas válidas
                        self.df = self.df[mask].copy()
                else:
                    print(f"Advertencia: La columna {column} no existe en el DataFrame")
            
            print(f"\nTamaño final del DataFrame: {len(self.df)}")
        return self

    def get_invalid(self, column: str) -> pd.DataFrame:
        """
        Devuelve las filas inválidas registradas para `column`.
        """
        return self.invalid.get(column, pd.DataFrame())

    def get_df(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame filtrado tras todas las validaciones.
        """
        return self.df