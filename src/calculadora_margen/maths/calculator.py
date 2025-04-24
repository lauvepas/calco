import pandas as pd
from typing import Optional

class CostCalculator:
    """
    Clase para calcular costes de fabricación de manera recursiva.
    """
    
    def __init__(self, fabricaciones: pd.DataFrame):
        """
        Inicializa el calculador de costes.
        
        Parameters
        ----------
        fabricaciones : pd.DataFrame
            DataFrame con las fabricaciones y sus componentes. Debe contener las columnas:
            - componente
            - coste_componente_unitario
        """
        self.fabricaciones = fabricaciones.copy()
        
        # Inicializar flag_coste_calculado
        # Los componentes que no empiezan por 'SEM' ya tienen coste calculado
        self.fabricaciones['flag_coste_calculado'] = ~self.fabricaciones['componente'].str.startswith('SEM')
        
        # Imprimir estado inicial
        false_flag_num = len(self.fabricaciones) - self.fabricaciones['flag_coste_calculado'].sum()
        print(f"Estado inicial: {false_flag_num} registros pendientes de calcular coste")
        
        # Control opcional: mostrar resumen por tipo de artículo
        control = (self.fabricaciones
                  .groupby('articulo')
                  .agg({'flag_coste_calculado': 'all'})
                  .reset_index()
                  .groupby('flag_coste_calculado')
                  .agg({'articulo': 'count'})
                  .reset_index())
        
        print("\nResumen por estado de cálculo:")
        for _, row in control.iterrows():
            estado = "calculados" if row['flag_coste_calculado'] else "pendientes"
            print(f"Artículos {estado}: {row['articulo']}")

    def calcular_costes_recursivamente(self, max_iteraciones: int = 6) -> pd.DataFrame:
        """
        Calcula recursivamente los costes de componentes basándose en las fabricaciones.
        
        Parameters
        ----------
        max_iteraciones : int, optional
            Número máximo de iteraciones para evitar bucles infinitos, por defecto 6
            
        Returns
        -------
        pd.DataFrame
            DataFrame con los costes calculados
        """
        nulos_anterior = float('inf')
        
        for i in range(max_iteraciones):
            nulos_actual = self.fabricaciones['coste_componente_unitario'].isna().sum()
            print(f"\n{i+1}ª iteración:")
            print(f"Registros sin coste: {nulos_actual}")
            
            if nulos_actual == 0:
                print("Todos los costes han sido calculados.")
                break
                
            if nulos_actual >= nulos_anterior:
                print("No se pueden calcular más costes.")
                break
                
            nulos_anterior = nulos_actual
            
            # Identificar productos calculables
            productos_calculables = (
                self.fabricaciones
                .groupby(['articulo', 'lote_articulo'])
                .agg({'coste_componente_unitario': lambda x: x.notna().all()})
                .reset_index()
            )
            
            calculables = productos_calculables[
                productos_calculables['coste_componente_unitario']
            ][['articulo', 'lote_articulo']]
            
            # Calcular costes para productos calculables
            for _, producto in calculables.iterrows():
                self._calcular_coste_producto(producto)
            
            # Actualizar flags
            self.fabricaciones['flag_coste_calculado'] = self.fabricaciones['coste_componente_unitario'].notna()
        
        self._imprimir_resumen_final()
        return self.fabricaciones
    
    def _calcular_coste_producto(self, producto: pd.Series) -> None:
        """
        Calcula el coste de un producto específico y actualiza los registros relacionados.
        
        Parameters
        ----------
        producto : pd.Series
            Serie con el artículo y lote_articulo del producto a calcular
        """
        # Filtrar componentes del producto actual
        mask_producto = (
            (self.fabricaciones['articulo'] == producto['articulo']) & 
            (self.fabricaciones['lote_articulo'] == producto['lote_articulo'])
        )
        
        componentes_producto = self.fabricaciones[mask_producto].copy()
        
        # Calcular coste total del producto
        coste_total = (
            componentes_producto['consumo_unitario'] * 
            componentes_producto['coste_componente_unitario']
        ).sum()
        
        # Identificar dónde este producto es usado como componente
        mask_como_componente = (
            self.fabricaciones['componente'].astype(str) == producto['articulo']
        )
        
        # Actualizar costes donde este producto es usado como componente
        if mask_como_componente.any():
            self.fabricaciones.loc[mask_como_componente, 'coste_componente_unitario'] = coste_total
            self.fabricaciones.loc[mask_como_componente, 'flag_coste_calculado'] = True
    
    def _imprimir_resumen_final(self) -> None:
        """
        Imprime un resumen del estado final del cálculo de costes.
        """
        nulos_final = self.fabricaciones['coste_componente_unitario'].isna().sum()
        print("\nResumen final:")
        print(f"Total registros: {len(self.fabricaciones)}")
        print(f"Registros sin coste: {nulos_final}")
        print(f"Registros con coste calculado: {len(self.fabricaciones) - nulos_final}")