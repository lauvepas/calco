import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple
from calculadora_margen.config.parameters import DatasetParams

class VisualizationManager:
    """
    Gestiona la creación de visualizaciones para análisis de datos.
    """
    
    def __init__(self, df: pd.DataFrame, params: DatasetParams):
        """
        Inicializa el gestor de visualizaciones.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame a visualizar
        params : DatasetParams
            Parámetros de configuración para las visualizaciones
        """
        if not all([params.viz_date_column, params.viz_value_column, params.viz_group_column]):
            raise ValueError("Se requieren los parámetros de visualización")
            
        self.df = df.copy()
        self.params = params
        
        # Configuración por defecto de matplotlib
# Usa un estilo pastel si tienes seaborn, si no, usa ggplot
        try:
            plt.style.use('seaborn-v0_8-pastel')
        except Exception:
            plt.style.use('ggplot')
        self.default_figsize = (12, 6)
        self.colors = plt.cm.Set3(np.linspace(0, 1, 12))

    def plot_time_series(self, 
                        articulo: str,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Crea un gráfico de líneas para la evolución temporal de costes.
        
        Parameters
        ----------
        articulo : str
            Artículo específico a visualizar
        start_date : str, optional
            Fecha de inicio en formato 'YYYY-MM-DD'
        end_date : str, optional
            Fecha fin en formato 'YYYY-MM-DD'
        figsize : tuple, optional
            Tamaño del gráfico (ancho, alto)
        """
        # Filtrar por artículo
        df_articulo = self.df[self.df[self.params.viz_group_column] == articulo].copy()
        
        if df_articulo.empty:
            print(f"No hay datos para el artículo {articulo}")
            return
            
        # Convertir fechas si es necesario
        if not pd.api.types.is_datetime64_any_dtype(df_articulo[self.params.viz_date_column]):
            df_articulo[self.params.viz_date_column] = pd.to_datetime(
                df_articulo[self.params.viz_date_column]
            )
            
        # Filtrar por rango de fechas si se especifica
        if start_date:
            df_articulo = df_articulo[
                df_articulo[self.params.viz_date_column] >= pd.to_datetime(start_date)
            ]
        if end_date:
            df_articulo = df_articulo[
                df_articulo[self.params.viz_date_column] <= pd.to_datetime(end_date)
            ]
            
        # Ordenar por fecha
        df_articulo = df_articulo.sort_values(self.params.viz_date_column)
        
        # Crear el gráfico
        plt.figure(figsize=figsize or self.default_figsize)
        
        # Línea principal
        plt.plot(
            df_articulo[self.params.viz_date_column],
            df_articulo[self.params.viz_value_column],
            marker='o',
            linestyle='-',
            linewidth=2,
            markersize=8,
            label=f'Coste {articulo}'
        )
        
        # Línea de tendencia
        z = np.polyfit(
            range(len(df_articulo)),
            df_articulo[self.params.viz_value_column],
            1
        )
        p = np.poly1d(z)
        plt.plot(
            df_articulo[self.params.viz_date_column],
            p(range(len(df_articulo))),
            "r--",
            alpha=0.8,
            label='Tendencia'
        )
        
        # Configuración del gráfico
        plt.title(f"{self.params.viz_title} - {articulo}")
        plt.xlabel('Fecha')
        plt.ylabel(self.params.viz_y_label)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Rotar etiquetas del eje x
        plt.xticks(rotation=45)
        
        # Ajustar márgenes
        plt.tight_layout()
        
        # Mostrar estadísticas
        stats = df_articulo[self.params.viz_value_column].describe()
        print(f"\nEstadísticas para {articulo}:")
        print(f"Media: {stats['mean']:.2f}")
        print(f"Desv. Est.: {stats['std']:.2f}")
        print(f"Min: {stats['min']:.2f}")
        print(f"Max: {stats['max']:.2f}")
        
        plt.show()



    def plot_multiple_time_series(self,
                                articulos: list[str],
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Crea un gráfico comparativo de varios artículos.
        """
        plt.figure(figsize=figsize or self.default_figsize)
        
        for i, articulo in enumerate(articulos):
            df_articulo = self.df[
                self.df[self.params.viz_group_column] == articulo
            ].copy()
            
            if df_articulo.empty:
                print(f"No hay datos para el artículo {articulo}")
                continue
                
            plt.plot(
                df_articulo[self.params.viz_date_column],
                df_articulo[self.params.viz_value_column],
                marker='o',
                label=articulo
            )
        
        plt.title(self.params.viz_title)
        plt.xlabel('Fecha')
        plt.ylabel(self.params.viz_y_label)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()