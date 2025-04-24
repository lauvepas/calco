import pandas as pd
from typing import Dict
from datetime import datetime

class OutliersManager:
    """
    Gestiona la detección y tratamiento de outliers en un DataFrame.
    Trabaja sobre una copia del DataFrame original.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._z_score_threshold = 3
        self._min_outliers_threshold = 5
        self._max_iterations = 20
        self._summary = {
            'initial_outliers': 0,
            'replaced_outliers': 0,
            'remaining_outliers': 0,
            'remaining_outliers_info': []
        }
        self._verbose = False  # Añadimos un flag para controlar el nivel de detalle

    def _detect_outliers_by_group(self, group: pd.DataFrame, componente: str) -> pd.DataFrame:
        """
        Detecta outliers en un grupo usando z-score.
        
        Parameters
        ----------
        group : pd.DataFrame
            Grupo de datos para un componente específico
        componente : str
            Nombre del componente que se está procesando
            
        Returns
        -------
        pd.DataFrame
            DataFrame con las columnas z_score e is_outlier añadidas
        """
        group = group.copy()
        group['componente'] = componente

        mean = group['coste_componente_unitario'].mean()
        std = group['coste_componente_unitario'].std()

        if std == 0:
            group['z_score'] = 0
            group['is_outlier'] = False
            if self._verbose:  # Solo mostrar si verbose es True
                print(f"  - Componente {componente}: Sin variación en costes (std=0)")
        else:
            group['z_score'] = (group['coste_componente_unitario'] - mean) / std
            group['is_outlier'] = group['z_score'].abs() > self._z_score_threshold
            n_outliers = group['is_outlier'].sum()
            if n_outliers > 0 and self._verbose:  # Solo mostrar si verbose es True
                print(f"  - Componente {componente}: {n_outliers} outliers detectados")
                print(f"    Media: {mean:.2f}, Std: {std:.2f}")
                outliers = group[group['is_outlier']]
                print(f"    Valores outlier: {outliers['coste_componente_unitario'].tolist()}")

        return group

    def _detect_outliers(self) -> pd.DataFrame:
        """
        Detecta outliers en todo el DataFrame agrupando por componente.
        """
        if self._verbose:  # Solo mostrar si verbose es True
            print("\nAnalizando outliers por componente...")
        
        grupos = []
        for componente, group in self.df.groupby('componente'):
            group_sin_componente = group.drop(columns='componente')
            grupos.append(self._detect_outliers_by_group(group_sin_componente, componente))

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
        
        while sum_outliers > self._min_outliers_threshold and count < self._max_iterations:
            count += 1
            
            # Separar outliers
            sin_outliers = self.df[~self.df['is_outlier']].copy()
            con_outliers = self.df[self.df['is_outlier']].copy()
            
            if con_outliers.empty:
                break
                
            # Calcular y aplicar correcciones
            medias_limpias = sin_outliers.groupby('componente')['coste_componente_unitario'].mean()
            con_outliers['coste_componente_unitario'] = (
                con_outliers['componente'].map(medias_limpias)
            )
            
            # Unir y recalcular
            self.df = pd.concat([sin_outliers, con_outliers], ignore_index=True)
            self.df = self._detect_outliers()
            sum_outliers = self.df['is_outlier'].sum()

        # Guardar información de outliers restantes
        if sum_outliers > 0:
            outliers_finales = self.df[self.df['is_outlier']]
            for componente, grupo in outliers_finales.groupby('componente'):
                valores_grupo = self.df[self.df['componente'] == componente]['coste_componente_unitario']
                mean = valores_grupo.mean()
                outliers_valores = grupo['coste_componente_unitario']
                desviaciones = abs(outliers_valores - mean) / mean * 100
                
                self._summary['remaining_outliers_info'].append({
                    'componente': componente,
                    'n_outliers': len(grupo),
                    'desviacion_media': desviaciones.mean(),
                    'valores': outliers_valores.tolist(),
                    'media_componente': mean
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
