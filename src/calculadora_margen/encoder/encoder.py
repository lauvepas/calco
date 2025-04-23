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





    """Uso:
    
    # Instead of:
    encoder = Encoder(fabricaciones)
    fabricaciones = encoder.create_key(col1='componente', col2='lote_componente_proveedor', new_col_name='clave_merge')
    fabricaciones = fabricaciones.merge(master_lotes, on="clave_merge", how="left")

    # You can now do:
    encoder = Encoder(fabricaciones)
    fabricaciones = encoder.merge_with(
    right_df=master_lotes,
    left_cols=('componente', 'lote_componente_proveedor'),
    right_cols=('articulo', 'lote_proveedor'),
    how='left'"""



    def merge_with(
        self,
        right_df: pd.DataFrame,
        left_cols: tuple[str, str] = None,
        right_cols: tuple[str, str] = None,
        how: str = "left",
        merge_key: str = "clave_merge"
    ) -> pd.DataFrame:
        """
        Creates merge keys in both DataFrames and performs a merge operation.

        Parameters
        ----------
        right_df : pd.DataFrame
            The DataFrame to merge with.
        left_cols : tuple[str, str], optional
            Tuple of (col1, col2) to create merge key in left DataFrame.
            If None, assumes merge_key already exists.
        right_cols : tuple[str, str], optional
            Tuple of (col1, col2) to create merge key in right DataFrame.
            If None, assumes merge_key already exists.
        how : str, default "left"
            Type of merge to be performed: 'left', 'right', 'outer', 'inner'.
        merge_key : str, default "clave_merge"
            Name of the column to use as merge key.

        Returns
        -------
        pd.DataFrame
            The merged DataFrame.
        """
        # Create temporary right DataFrame to avoid modifying the original
        right_temp = right_df.copy()

        # Create merge keys if columns are specified
        if left_cols:
            self.create_key(col1=left_cols[0], col2=left_cols[1], new_col_name=merge_key)
        
        if right_cols:
            right_temp = Encoder(right_temp).create_key(
                col1=right_cols[0],
                col2=right_cols[1],
                new_col_name=merge_key
            )

        # Perform the merge
        result = self.df.merge(right_temp, on=merge_key, how=how)
        return result
