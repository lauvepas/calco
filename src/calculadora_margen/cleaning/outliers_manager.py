import pandas as pd
from typing import Dict

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

    def _detect_outliers_by_group(self, group: pd.DataFrame, componente: str) -> pd.DataFrame:
        """
        Detecta outliers en un grupo usando z-score.
        """
        group = group.copy()
        group['componente'] = componente  # Restauramos la columna que eliminamos antes

        mean = group['coste_componente_unitario'].mean()
        std = group['coste_componente_unitario'].std()

        if std == 0:
            group['z_score'] = 0
            group['is_outlier'] = False
        else:
            group['z_score'] = (group['coste_componente_unitario'] - mean) / std
            group['is_outlier'] = group['z_score'].abs() > self._z_score_threshold

        return group

    def _detect_outliers(self) -> pd.DataFrame:
        """
        Detecta outliers en todo el DataFrame agrupando por componente.
        """
        grupos = []
        for componente, group in self.df.groupby('componente'):
            group_sin_componente = group.drop(columns='componente')
            grupos.append(self._detect_outliers_by_group(group_sin_componente, componente))

        return pd.concat(grupos, ignore_index=True)

    def process_outliers(self) -> 'OutliersManager':
        """
        Procesa los outliers reemplazándolos por la media del grupo hasta que
        el número de outliers sea menor que el umbral o se alcance el máximo de iteraciones.
        """
        count = 0
        sum_outliers = float('inf')

        print("Iniciando procesamiento de outliers...")
        
        while sum_outliers > self._min_outliers_threshold and count < self._max_iterations:
            # 1. Detectar outliers
            self.df = self._detect_outliers()
            
            # 2. Separar outliers
            sin_outliers = self.df[~self.df['is_outlier']].copy()
            con_outliers = self.df[self.df['is_outlier']].copy()
            
            if con_outliers.empty:
                break
                
            # 3. Calcular medias de valores válidos
            medias_limpias = (sin_outliers
                            .groupby('componente')['coste_componente_unitario']
                            .mean()
                            .to_dict())
            
            # 4. Reemplazar outliers con medias
            con_outliers['coste_componente_unitario'] = (
                con_outliers['componente'].map(medias_limpias)
            )
            
            # 5. Unir datos
            self.df = pd.concat([sin_outliers, con_outliers], ignore_index=True)
            
            # 6. Recalcular outliers
            self.df = self._detect_outliers()
            sum_outliers = self.df['is_outlier'].sum()
            count += 1
            
            print(f"Iteración {count}: {sum_outliers} outliers restantes")

        print(f"\nProceso completado en {count} iteraciones")
        print(f"Outliers finales: {sum_outliers}")
        
        return self

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
