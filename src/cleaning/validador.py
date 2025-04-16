import pandas as pd
import re
from files import data_source

class DataValidationError(Exception):
    """
    Custom exception raised when data validation fails.
    """
    pass

class DataValidator:
    """
    Class to validate data in a pandas DataFrame.

    Parameters
    ----------
    df_lotes : pd.DataFrame
        The DataFrame to validate.
    """
    def __init__(self,df_lotes: pd.DataFrame):
        self.df_lotes = df_lotes
        self.errors = []

    def validate_column_types(self, expected_types: dict):
        """
        Validates that each column has the expected data type.

        Parameters
        ----------
        expected_types : dict
            Dictionary mapping column names to expected data types.

        Raises
        ------
        DataValidationError
            If any column does not match the expected type.
        """
        for column, expected_type in expected_types.items():
            if column not in self.df_lotes.columns:
                self.errors.append(f"Missing column: {column}")
            elif not pd.api.types.is_dtype_equal(self.df_lotes[column].dtype, expected_type):
                self.errors.append(
                    f"Column '{column}' has type {self.df_lotes[column].dtype}, expected {expected_type}."
                )
        if self.errors:
            raise DataValidationError("Type validation failed. Errors: " + "; ".join(self.errors))

    def validate_missing_values(self, columns: list):
        """
        Validates that the specified columns have no missing values.

        Parameters
        ----------
        columns : list
            List of column names to check for missing values.

        Raises
        ------
        DataValidationError
            If any column contains missing values.
        """
        for column in columns:
            if column not in self.df_lotes.columns:
                self.errors.append(f"Missing column: {column}")
            elif self.df_lotes[column].isnull().any():
                self.errors.append(f"Column '{column}' contains missing values.")
        if self.errors:
            raise DataValidationError("Missing values validation failed. Errors: " + "; ".join(self.errors))

    def validate_regex(self, column: str, pattern: str):
        """
        Validates values in a column against a regular expression.

        Parameters
        ----------
        column : str
            The name of the column to validate.
        pattern : str
            Regular expression pattern to apply.

        Raises
        ------
        DataValidationError
            If any value does not match the regular expression.
        """
        if column not in self.df_lotes.columns:
            self.errors.append(f"Missing column: {column}")
        else:
            invalid_values = []
            for idx, value in self.df_lotes[column].astype(str).items():
                if not re.fullmatch(pattern, value):
                    invalid_values.append((idx, value))

            if invalid_values:
                self.errors.append(
                    f"Column '{column}' contains {len(invalid_values)} values that do not match the pattern '{pattern}': {invalid_values}"
                )

        if self.errors:
            raise DataValidationError("Regex validation failed. Errors: " + "; ".join(self.errors))

    def get_errors(self):
        """
        Returns the list of validation errors.

        Returns
        -------
        list
            List of validation error messages.
        """
        return self.errors


