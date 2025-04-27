import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple
from calculadora_margen.config.parameters import DatasetParams



# Personalized exception
class VisualizationError(Exception):
    """Excepción base para errores en VisualizationManager."""
    pass


class VisualizationManager:
    """
    Manages the creation of visualizations for data analysis.
    """
    
    def __init__(self, df: pd.DataFrame, params: DatasetParams):
        """
        Initializes the visualization manager.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to visualize
        params : DatasetParams
            Configuration parameters for visualizations
        """
        if not all([params.viz_date_column, params.viz_value_column, params.viz_group_column]):
            raise VisualizationError("Missing required visualization parameters")
            
        self.df = df.copy()
        self.params = params
        
        # Default matplotlib configuration
        # Use a pastel style if seaborn is available, otherwise use ggplot
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
        Creates a line plot for the temporal evolution of costs.
        
        Parameters
        ----------
        articulo : str
            Specific product to visualize
        start_date : str, optional
            Start date in 'YYYY-MM-DD' format
        end_date : str, optional
            End date in 'YYYY-MM-DD' format
        figsize : tuple, optional
            Size of the plot (width, height)

        Returns
        -------
        None
        """
       
        # Check if the article is specified. Not for start_date and end_date as they are optional
        if not articulo:
            raise VisualizationError("Debes especificar un valor para `articulo`.")

        try:
            # Filter by product
            df_art = self.df[self.df[self.params.viz_group_column] == articulo].copy()
            if df_art.empty:
                raise VisualizationError(f"No hay datos para el artículo «{articulo}»")

            # Convert dates if necessary
            try:
                if not pd.api.types.is_datetime64_any_dtype(df_art[self.params.viz_date_column]):
                    df_art[self.params.viz_date_column] = pd.to_datetime(
                        df_art[self.params.viz_date_column], format='%Y-%m-%d'
                    )
            except ValueError:
                raise VisualizationError(f"Fecha de inicio inválida: {start_date}")

            # Filter by date range if specified
            if start_date:
                try:
                    start = pd.to_datetime(start_date, format='%Y-%m-%d')
                except ValueError:
                    print(f"Fecha de inicio inválida: «{start_date}». "
                          "Usa 'YYYY-MM-DD'.")
                    return
                df_art = df_art[df_art[self.params.viz_date_column] >= start]

            if end_date:
                try:
                    end = pd.to_datetime(end_date, format='%Y-%m-%d')
                except ValueError:
                    print(f"⚠️ Fecha de fin inválida: «{end_date}». "
                          "Usa 'YYYY-MM-DD'.")
                    return
                df_art = df_art[df_art[self.params.viz_date_column] <= end]


            df_art = df_art.sort_values(self.params.viz_date_column)
            if df_art.shape[0] < 2:
                print("La fecha de inicio no puede ser posterior a la fecha de fin.")
                return

            # Create the plot
            plt.figure(figsize=figsize or self.default_figsize)
            plt.plot(
                df_art[self.params.viz_date_column],
                df_art[self.params.viz_value_column],
                marker='o', linestyle='-', linewidth=2, markersize=6,
                label=f'Coste {articulo}'
            )

            # Main line (can fail if there are less than 2 points)
            try:
                x = np.arange(len(df_art))
                coeffs = np.polyfit(x, df_art[self.params.viz_value_column], 1)
                trend = np.poly1d(coeffs)(x)
                plt.plot(df_art[self.params.viz_date_column], trend,
                         'r--', alpha=0.8, label='Tendencia')
            except Exception:
                print("No se pudo calcular la línea de tendencia. Amplía el rango de fechas.")

            # Plot configuration
            plt.title(f"{self.params.viz_title} – {articulo}")
            plt.xlabel('Fecha')
            plt.ylabel(self.params.viz_y_label)
            plt.grid(alpha=0.3)
            plt.legend()
            plt.xticks(rotation=45)   # Rotate x-axis labels
            plt.tight_layout()       # Adjust margins

            # Show statistics
            stats = df_art[self.params.viz_value_column].describe()
            print(f"\nEstadísticas para {articulo}:")
            print(f" • Media:       {stats['mean']:.2f}")
            print(f" • Desv. Est.:  {stats['std']:.2f}")
            print(f" • Mínimo:      {stats['min']:.2f}")
            print(f" • Máximo:      {stats['max']:.2f}")

            plt.show()

        except Exception as e:
            # Capture any unexpected errors
            print(f"Ha ocurrido un error al generar la gráfica de «{articulo}»: {e}.")

    def plot_multiple_time_series(self,
                                articulos: list[str],
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Creates a comparative plot of multiple products.

        Parameters
        ----------
        articulos : list[str]
            List of products to visualize
        start_date : str, optional
            Start date in 'YYYY-MM-DD' format
        end_date : str, optional

        Returns
        -------
        None
        """

        # Check if the article is specified. Not for start_date and end_date as they are optional
        if not articulos:
            raise VisualizationError("Debes especificar al menos un valor para `articulos`.")

        try:
            plt.figure(figsize=figsize or self.default_figsize)
            any_data = False

            for art in articulos:
                df_art = self.df[self.df[self.params.viz_group_column] == art].copy()
                
                if df_art.empty:
                    print(f"Sin datos para «{art}» – se omite.")
                    continue

                # Check if the date column is a datetime
                try:
                    df_art[self.params.viz_date_column] = pd.to_datetime(
                        df_art[self.params.viz_date_column]
                    )
                except Exception:
                    print(f"No se pudo parsear fechas de «{art}», se omite.")
                    continue

                plt.plot(
                    df_art[self.params.viz_date_column],
                    df_art[self.params.viz_value_column],
                    marker='o',
                    label=art
                )
                any_data = True

            if not any_data:
                print("No hay datos para ninguno de los artículos solicitados.")
                return

            plt.title(self.params.viz_title)
            plt.xlabel('Fecha')
            plt.ylabel(self.params.viz_y_label)
            plt.grid(alpha=0.3)
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error al generar gráfico múltiple: {e}")
