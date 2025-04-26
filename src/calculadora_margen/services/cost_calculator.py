import pandas as pd
from typing import Optional

class CostCalculator:
    """
    Class for recursively calculating manufacturing costs.
    """
    
    def __init__(self, fabricaciones: pd.DataFrame):
        """
        Initializes the cost calculator.
        
        Parameters
        ----------
        fabricaciones : pd.DataFrame
            DataFrame with fabrications and their components. Must contain the columns:
            - componente
            - coste_componente_unitario
        """
        self.fabricaciones = fabricaciones.copy()
        
        # Initialize cost_calculated flag
        # Components not starting with 'SEM' already have calculated cost
        self.fabricaciones['flag_coste_calculado'] = ~self.fabricaciones['componente'].str.startswith('SEM')
        
        # Print initial state
        false_flag_num = len(self.fabricaciones) - self.fabricaciones['flag_coste_calculado'].sum()
        print(f"Estado inicial: {false_flag_num} registros pendientes de calcular coste")
        
        # Optional control: show summary by product type
        control = (self.fabricaciones
                  .groupby('articulo')
                  .agg({'flag_coste_calculado': 'all'})
                  .reset_index()
                  .groupby('flag_coste_calculado')
                  .agg({'articulo': 'count'})
                  .reset_index())
        
        print("\nResumen por estado de cálculo:")
        for _, row in control.iterrows():
            status = "calculados" if row['flag_coste_calculado'] else "pendientes"
            print(f"Artículos {status}: {row['articulo']}")

    def calculate_costs_recursively(self, max_iterations: int = 6) -> pd.DataFrame:
        """
        Recursively calculates component costs based on fabrications.
        
        Parameters
        ----------
        max_iteraciones : int, optional
            Maximum number of iterations to avoid infinite loops, by default 6
            
        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated costs
        """
        previous_nulls = float('inf')
        
        for i in range(max_iterations):
            nulls = self.fabricaciones['coste_componente_unitario'].isna().sum()
            print(f"\n{i+1}ª iteración:")
            print(f"Registros sin coste: {nulls}")
            
            if nulls == 0:
                print("Todos los costes han sido calculados.")
                break
                
            if nulls >= previous_nulls:
                print("No se pueden calcular más costes.")
                break
                
            previous_nulls = nulls
            
            # Identify calculable products
            calculable_products = (
                self.fabricaciones
                .groupby(['articulo', 'lote_articulo'])
                .agg({'coste_componente_unitario': lambda x: x.notna().all()})
                .reset_index()
            )
            
            calculables = calculable_products[
                calculable_products['coste_componente_unitario']
            ][['articulo', 'lote_articulo']]
            
            # Calculate costs for calculable products
            for _, producto in calculables.iterrows():
                self._calculate_product_cost(producto)
            
            # Update flags
            self.fabricaciones['flag_coste_calculado'] = self.fabricaciones['coste_componente_unitario'].notna()
        
        self._print_concise_summary()
        return self.fabricaciones
    
    def _calculate_product_cost(self, producto: pd.Series) -> None:
        """
        Calculates the cost of a specific product and updates related records.
        
        Parameters
        ----------
        producto : pd.Series
            Series with the 'articulo' and 'lote_articulo' of the product to calculate
        """
        # Filter components of the current product
        mask_product = (
            (self.fabricaciones['articulo'] == producto['articulo']) & 
            (self.fabricaciones['lote_articulo'] == producto['lote_articulo'])
        )
        
        product_components = self.fabricaciones[mask_product].copy()
        
       # Calculate total cost of the product
        total_cost = (
            product_components['consumo_unitario'] * 
            product_components['coste_componente_unitario']
        ).sum()
        
        # Identify where this product is used as a component
        mask_as_component = (
            self.fabricaciones['componente'].astype(str) == producto['articulo']
        )
        
        # Update costs where this product is used as a component
        if mask_as_component.any():
            self.fabricaciones.loc[mask_as_component, 'coste_componente_unitario'] = total_cost
            self.fabricaciones.loc[mask_as_component, 'flag_coste_calculado'] = True
    
    def _print_concise_summary(self) -> None:
        """
        Prints a summary of the final cost calculation status.
        """
        nulos_final = self.fabricaciones['coste_componente_unitario'].isna().sum()
        print("\nResumen final:")
        print(f"Total registros: {len(self.fabricaciones)}")
        print(f"Registros sin coste: {nulos_final}")
        print(f"Registros con coste calculado: {len(self.fabricaciones) - nulos_final}")

    def generate_manufacturing_costs(self) -> pd.DataFrame:
        """
        Generates a summarized DataFrame with manufacturing costs per order.
        
        This method:
        1. Calculates the unit cost per component
        2. Groups by manufacturing order
        3. Sums the total costs
        4. Sorts by date
        
        Returns
        -------
        pd.DataFrame
            DataFrame with the columns:
            - id_orden
            - fecha_fabricacion
            - articulo
            - unidades_fabricadas
            - coste_total_fabricacion
        """
        # Verify that all costs have been calculated
        if self.fabricaciones['coste_componente_unitario'].isna().any():
            print("ADVERTENCIA: Hay costes pendientes de calcular. Los resultados pueden ser incompletos.")
        
        # Calculate unit cost per component
        df = self.fabricaciones.copy()
        df['coste_unitario'] = (
            df['coste_componente_unitario'] * 
            df['consumo_unitario']
        )
        
        # Group by order and sum costs
        costes_fabricacion = (
            df
            .groupby([
                'id_orden',
                'fecha_fabricacion',
                'articulo',
                'unidades_fabricadas'
            ])['coste_unitario']
            .sum()
            .reset_index()
        )
        # Sort by date
        costes_fabricacion = costes_fabricacion.sort_values(
            'fecha_fabricacion',
            ascending=True
        )
        
        # Reset index after sorting
        costes_fabricacion = costes_fabricacion.reset_index(drop=True)
        
        print("\nResumen de costes de fabricación:")
        print(f"Total órdenes procesadas: {len(costes_fabricacion)}")
        print(f"Rango de fechas: {costes_fabricacion['fecha_fabricacion'].min()} a {costes_fabricacion['fecha_fabricacion'].max()}")
        
        return costes_fabricacion