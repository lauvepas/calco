import pandas as pd

class Encoder:
    def __init__(self, df: pd.DataFrame):
        """
        Initializes the Encoder with the given DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame on which operations will be performed.
        """
        self.df = df

    def create_key(self, col1: str = "articulo", col2: str = None, new_col_name: str = "clave_unica") -> pd.DataFrame:
        """
        Creates a new column by concatenating two existing columns with a hyphen.

        Parameters
        ----------
        col1 : str, default "articulo"
            The name of the first column to concatenate.
        col2 : str
            The name of the second column to concatenate. Required.
        new_col_name : str, default "clave_unica"
            The name of the new column that will contain the concatenated keys.

        Returns
        -------
        pd.DataFrame
            The modified DataFrame with the new concatenated key column.
        """
        if col2 is None:
            raise ValueError("You must specify the second column to concatenate with.")

        self.df[new_col_name] = self.df[col1].astype(str) + "-" + self.df[col2].astype(str)
        return self.df



# no hacer esto, hacer una función que me diga si el merge va a funcionar o si estoy perdiendo datos.
