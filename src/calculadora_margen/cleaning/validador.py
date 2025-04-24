import re
import pandas as pd
from typing import Optional, Dict

class Validator:
    """
    Valida y filtra filas de un DataFrame según expresiones regulares.
    Las filas que no cumplen los patrones son eliminadas y almacenadas
    para referencia posterior.
    """
    def __init__(self, df: pd.DataFrame):
        # Hacemos copia para no modificar el original por accidente
        self.df = df.copy()
        # Guardará las filas inválidas por columna
        self.invalid = {}
        # Resumen de la validación
        self._summary = {
            'initial_size': 0,
            'final_size': 0,
            'invalid_rows_by_column': {}
        }

    def validate_with_map(self, validation_map: Optional[Dict[str, str]] = None) -> 'Validator':
        """
        Valida las columnas según el diccionario de validaciones proporcionado.
        Elimina las filas que no cumplen con los patrones especificados.

        Parámetros
        ----------
        validation_map : Dict[str, str], opcional
            Diccionario {columna: patron_regex} con las validaciones a aplicar.

        Retorna
        -------
        self : Validator
        """
        if validation_map:
            self._summary['initial_size'] = len(self.df)
            
            for column, pattern in validation_map.items():
                if column in self.df.columns:
                    # Compilar el patrón para eficiencia
                    compiled = re.compile(pattern)
                    # Aplicar fullmatch usando re
                    mask = self.df[column].astype(str).apply(lambda x: bool(compiled.fullmatch(x)))
                    # Filas inválidas
                    invalid_rows = self.df[~mask].copy()
                    self._summary['invalid_rows_by_column'][column] = len(invalid_rows)
                    
                    if not invalid_rows.empty:
                        # Guardar las filas inválidas
                        self.invalid[column] = invalid_rows
                        # Eliminar filas inválidas
                        self.df = self.df[mask].copy()
            
            self._summary['final_size'] = len(self.df)
            self._print_concise_summary()
        return self

    def _print_concise_summary(self):
        """Imprime un resumen conciso del proceso de validación."""
        print("\n=== RESUMEN DE VALIDACIÓN ===")
        print(f"Tamaño inicial del DataFrame: {self._summary['initial_size']}")
        print("\nFilas inválidas por columna:")
        for column, count in self._summary['invalid_rows_by_column'].items():
            print(f"  - {column}: {count} filas")
        print(f"\nTamaño final del DataFrame: {self._summary['final_size']}")
        print(f"Total filas eliminadas: {self._summary['initial_size'] - self._summary['final_size']}")

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
