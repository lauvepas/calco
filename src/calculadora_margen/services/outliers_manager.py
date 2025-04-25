import pandas as pd
from typing import Dict
from datetime import datetime
from calculadora_margen.config.parameters import DatasetParams

class OutliersManager:
    """
    Gestiona la detección y tratamiento de outliers en un DataFrame.
    """
    def __init__(self, df: pd.DataFrame, params: DatasetParams):
        """
        Inicializa el gestor de outliers.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame a procesar
        params : DatasetParams
            Parámetros de configuración del dataset
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
        Detecta outliers en un grupo usando z-score.
        
        Parameters
        ----------
        group : pd.DataFrame
            Grupo de datos para un componente específico
        group_value : str
            Valor del grupo que se está procesando
            
        Returns
        -------
        pd.DataFrame
            DataFrame con las columnas z_score e is_outlier añadidas
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
            if n_outliers > 0 and self._verbose:  # Solo mostrar si verbose es True
                print(f"  - Grupo {group_value}: {n_outliers} outliers detectados")
                print(f"    Media: {mean:.2f}, Std: {std:.2f}")
                outliers = group[group['is_outlier']]
                print(f"    Valores outlier: {outliers[self.params.outliers_value_column].tolist()}")

        return group

    def _detect_outliers(self) -> pd.DataFrame:
        """
        Detecta outliers en todo el DataFrame agrupando por grupo.
        """
        if self._verbose:  # Solo mostrar si verbose es True
            print("\nAnalizando outliers por grupo...")
        
        grupos = []
        for grupo, group in self.df.groupby(self.params.outliers_group_column):
            grupos.append(self._detect_outliers_by_group(group, grupo))

        return pd.concat(grupos, ignore_index=True)

    def process_outliers(self, verbose: bool = False) -> 'OutliersManager':
        """
        Procesa los outliers reemplazándolos por la media del grupo.
        
        Parameters
        ----------
        verbose : bool, default False
            Si True, muestra información detallada del proceso.
        """
        self._verbose = verbose
        
        # Primera detección para establecer el número inicial de outliers
        self.df = self._detect_outliers()
        self._summary['initial_outliers'] = self.df['is_outlier'].sum()
        
        count = 0
        sum_outliers = self._summary['initial_outliers']
        
        while sum_outliers > self.params.outliers_min_threshold and count < self.params.outliers_max_iterations:
            count += 1
            
            # Separar outliers
            sin_outliers = self.df[~self.df['is_outlier']].copy()
            con_outliers = self.df[self.df['is_outlier']].copy()
            
            if con_outliers.empty:
                break
                
            # Calcular y aplicar correcciones
            medias_limpias = sin_outliers.groupby(self.params.outliers_group_column)[self.params.outliers_value_column].mean()
            con_outliers[self.params.outliers_value_column] = (
                con_outliers[self.params.outliers_group_column].map(medias_limpias)
            )
            
            # Unir y recalcular
            self.df = pd.concat([sin_outliers, con_outliers], ignore_index=True)
            self.df = self._detect_outliers()
            sum_outliers = self.df['is_outlier'].sum()

        # Guardar información de outliers restantes
        if sum_outliers > 0:
            outliers_finales = self.df[self.df['is_outlier']]
            for grupo, grupo_df in outliers_finales.groupby(self.params.outliers_group_column):
                valores_grupo = self.df[self.df[self.params.outliers_group_column] == grupo][self.params.outliers_value_column]
                mean = valores_grupo.mean()
                outliers_valores = grupo_df[self.params.outliers_value_column]
                desviaciones = abs(outliers_valores - mean) / mean * 100
                
                self._summary['remaining_outliers_info'].append({
                    'grupo': grupo,
                    'n_outliers': len(grupo_df),
                    'desviacion_media': desviaciones.mean(),
                    'valores': outliers_valores.tolist(),
                    'media_grupo': mean
                })

        self._summary['replaced_outliers'] = self._summary['initial_outliers'] - sum_outliers
        self._summary['remaining_outliers'] = sum_outliers
        
        self._print_concise_summary()
        return self

    def _print_concise_summary(self):
        """Imprime un resumen conciso del proceso."""
        print("\n=== RESUMEN DE OUTLIERS ===")
        print(f"Outliers detectados inicialmente: {self._summary['initial_outliers']}")
        print(f"Outliers reemplazados por la media: {self._summary['replaced_outliers']}")
        print(f"Outliers restantes: {self._summary['remaining_outliers']}")

    def clean_columns(self) -> 'OutliersManager':
        """
        Elimina las columnas auxiliares usadas en el proceso.
        """
        self.df = self.df.drop(columns=['z_score', 'is_outlier'])
        return self

    def get_df(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame procesado.
        """
        return self.df
