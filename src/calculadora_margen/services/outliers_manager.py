import pandas as pd
from typing import Dict
from datetime import datetime
from calculadora_margen.config.parameters import DatasetParams

class OutliersManager:
    """
    Manages the detection and treatment of outliers in a DataFrame.
    """
    def __init__(self, df: pd.DataFrame, params: DatasetParams):
        """
        Initializes the outliers manager.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to process
        params : DatasetParams
            Dataset configuration parameters

        Returns
        -------
        OutliersManager
            The initialized outliers manager.
        """
        if not params.outliers_value_column or not params.outliers_group_column:
            raise ValueError("Los parámetros de outliers son requeridos")
            
        self.df = df.copy()
        self.params = params
        self._summary = {
            'initial_outliers': 0,
            'replaced_outliers': 0,
            'remaining_outliers': 0,
            'remaining_outliers_info': []
        }
        self._verbose = False

    def _detect_outliers_by_group(self, group: pd.DataFrame, group_value: str) -> pd.DataFrame:
        """
        Detects outliers in a group using z-score (private method).

        Parameters
        ----------
        group : pd.DataFrame
            Data subset for a specific component
        group_value : str
            The group value being processed

        Returns
        -------
        pd.DataFrame
            DataFrame with added 'z_score' and 'is_outlier' columns
        """
        group = group.copy()
        group[self.params.outliers_group_column] = group_value

        mean = group[self.params.outliers_value_column].mean()
        std = group[self.params.outliers_value_column].std()

        if std == 0:
            group['z_score'] = 0
            group['is_outlier'] = False
            if self._verbose:
                print(f"  - Grupo {group_value}: Sin variación en valores (std=0)")
        else:
            group['z_score'] = (group[self.params.outliers_value_column] - mean) / std
            group['is_outlier'] = group['z_score'].abs() > self.params.outliers_z_score
            n_outliers = group['is_outlier'].sum()
            if n_outliers > 0 and self._verbose:  # Only if verbose is True
                print(f"  - Grupo {group_value}: {n_outliers} outliers detectados")
                print(f"    Media: {mean:.2f}, Std: {std:.2f}")
                outliers = group[group['is_outlier']]
                print(f"    Valores outlier: {outliers[self.params.outliers_value_column].tolist()}")

        return group

    def _detect_outliers(self) -> pd.DataFrame:
        """
        Detects outliers across the entire DataFrame by grouping (private method).
        """
        if self._verbose:  # Only if verbose is True
            print("\nAnalizando outliers por grupo...")
        
        groups = []
        for grupo, group in self.df.groupby(self.params.outliers_group_column):
            groups.append(self._detect_outliers_by_group(group, grupo))

        return pd.concat(groups, ignore_index=True)

    def process_outliers(self, verbose: bool = False) -> 'OutliersManager':
        """
        Processes outliers by replacing them with the group mean.

        Parameters
        ----------
        verbose : bool, default False
            If True, displays detailed process information.

        Returns
        -------
        OutliersManager
            The processed outliers manager.
        """
        self._verbose = verbose
        
        # First detection to set the initial number of outliers
        self.df = self._detect_outliers()
        self._summary['initial_outliers'] = self.df['is_outlier'].sum()
        
        count = 0
        sum_outliers = self._summary['initial_outliers']
        
        while sum_outliers > self.params.outliers_min_threshold and count < self.params.outliers_max_iterations:
            count += 1
            
            # Separate non-outliers and outliers
            without_outliers = self.df[~self.df['is_outlier']].copy()
            with_outliers = self.df[self.df['is_outlier']].copy()
            
            if with_outliers.empty:
                break
                
            # Calculate and apply corrections
            medias_limpias = without_outliers.groupby(self.params.outliers_group_column)[self.params.outliers_value_column].mean()
            with_outliers[self.params.outliers_value_column] = (
                with_outliers[self.params.outliers_group_column].map(medias_limpias)
            )
            
            # Rejoin and recalculate
            self.df = pd.concat([without_outliers, with_outliers], ignore_index=True)
            self.df = self._detect_outliers()
            sum_outliers = self.df['is_outlier'].sum()

        # Record remaining outliers information
        if sum_outliers > 0:
            final_outliers = self.df[self.df['is_outlier']]
            for grupo, grupo_df in final_outliers.groupby(self.params.outliers_group_column):
                group_values = self.df[self.df[self.params.outliers_group_column] == grupo][self.params.outliers_value_column]
                mean = group_values.mean()
                outliers_values = grupo_df[self.params.outliers_value_column]
                desviations = abs(outliers_values - mean) / mean * 100
                
                self._summary['remaining_outliers_info'].append({
                    'grupo': grupo,
                    'n_outliers': len(grupo_df),
                    'desviacion_media': desviations.mean(),
                    'valores': outliers_values.tolist(),
                    'media_grupo': mean
                })

        self._summary['replaced_outliers'] = self._summary['initial_outliers'] - sum_outliers
        self._summary['remaining_outliers'] = sum_outliers
        
        self._print_concise_summary()
        return self

    def _print_concise_summary(self):
        """Prints a concise summary of the outlier processing (private method)."""
        print("\n=== RESUMEN DE OUTLIERS ===")
        print(f"Outliers detectados inicialmente: {self._summary['initial_outliers']}")
        print(f"Outliers reemplazados por la media: {self._summary['replaced_outliers']}")
        print(f"Outliers restantes: {self._summary['remaining_outliers']}")

    def clean_columns(self) -> 'OutliersManager':
        """
        Removes auxiliary columns used in the process.
        """
        self.df = self.df.drop(columns=['z_score', 'is_outlier'])
        return self

    def get_df(self) -> pd.DataFrame:
        """
        Returns the processed DataFrame.
        """
        return self.df
