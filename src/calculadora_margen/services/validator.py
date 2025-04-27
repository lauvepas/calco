import re
import pandas as pd
from typing import Optional, Dict

class Validator:
    """
    Validates and filters rows of a DataFrame based on regular expressions.
    Rows that do not match the patterns are removed and stored
    for later reference.
    """
    def __init__(self, df: pd.DataFrame):
        """
        Initializes the Validator with the given DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to validate.
        
        Returns
        -------
        Validator
            The initialized validator.
        """

        # Make a copy to avoid accidentally modifying the original
        self.df = df.copy()
        # Will store invalid rows by column
        self.invalid = {}
        # Validation summary
        self._summary = {
            'initial_size': 0,
            'final_size': 0,
            'invalid_rows_by_column': {}
        }

    def validate_with_map(self, validation_map: Optional[Dict[str, str]] = None) -> 'Validator':
        """
        Validates columns according to the provided validation dictionary.
        Removes rows that do not match the specified patterns.

        Parameters
        ----------
        validation_map : Dict[str, str], optional
            Dictionary {column: regex_pattern} of validations to apply.

        Returns
        -------
        self : Validator
        """
        if validation_map:
            self._summary['initial_size'] = len(self.df)
            
            for column, pattern in validation_map.items():
                if column in self.df.columns:
                    # Compile the pattern for efficiency
                    compiled = re.compile(pattern)
                    # Apply fullmatch using re
                    mask = self.df[column].astype(str).apply(lambda x: bool(compiled.fullmatch(x)))
                    # Invalid rows
                    invalid_rows = self.df[~mask].copy()
                    self._summary['invalid_rows_by_column'][column] = len(invalid_rows)
                    
                    if not invalid_rows.empty:
                        # Save invalid rows
                        self.invalid[column] = invalid_rows
                        # Remove invalid rows
                        self.df = self.df[mask].copy()
            
            self._summary['final_size'] = len(self.df)
            self._print_concise_summary()
        return self

    def _print_concise_summary(self):
        """Prints a concise summary of the validation process (private method)."""
        print("\n=== RESUMEN DE VALIDACIÓN ===")
        print(f"Tamaño inicial del DataFrame: {self._summary['initial_size']}")
        print("\nFilas inválidas por columna:")
        for column, count in self._summary['invalid_rows_by_column'].items():
            print(f"  - {column}: {count} filas")
        print(f"\nTamaño final del DataFrame: {self._summary['final_size']}")
        print(f"Total filas eliminadas: {self._summary['initial_size'] - self._summary['final_size']}")

    def get_invalid(self, column: str) -> pd.DataFrame:
        """
        Returns the invalid rows recorded for `column`.

        Parameters
        ----------
        column : str
            The column to get invalid rows from.

        Returns
        -------
        pd.DataFrame
            The invalid rows recorded for `column`.
        """
        return self.invalid.get(column, pd.DataFrame())

    def get_df(self) -> pd.DataFrame:
        """
        Returns the filtered DataFrame after all validations.
        """
        return self.df
