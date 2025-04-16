import pandas as pd
import regex as re

class CostesCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.costes = None

    def load_data(self):
        self.costes = pd.read_csv(self.file_path, encoding='UTF-8', sep=';', dtype=str)
        return self

    def initial_cleaning(self):
        self.costes.dropna(subset=['PRCMONEDA'], inplace=True)
        self.costes = self.costes.drop_duplicates()

        self.costes.drop(columns=[
            'Cód. almacén estructura', '% descuento 1', 'DESCALM', 'Artículo',
            'FECCADUC', 'UNIDADES', 'TIPDOC', 'NUMDOC', 'LOTE', 'REFERENCIA',
            'FECDOC', 'Cód. proveedor', 'NOMPRO'
        ], inplace=True, errors='ignore')

        self.costes.rename(columns={
            "Cód. artículo": "componente",
            "PRCMONEDA": "coste_componente_unitario",
            "LOTEINTERNO": "lote_interno"
        }, inplace=True)

        self.costes['coste_componente_unitario'] = (
            self.costes['coste_componente_unitario']
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

        return self

    def validate_columns(self):
        # Validación de 'componente'
        pattern_comp = re.compile(r'^[\p{L}]+[0-9]{2,3}$')
        self.costes = self.costes[self.costes['componente'].apply(lambda x: bool(pattern_comp.fullmatch(x)))]

        # Validación de 'lote_interno'
        pattern_lote = re.compile(r'^[0-9]{4}-[0-9]{3}$')
        self.costes = self.costes[self.costes['lote_interno'].apply(lambda x: bool(pattern_lote.fullmatch(x)))]

        return self

    def remove_duplicate_batches(self):
        self.costes.drop_duplicates(subset='lote_interno', keep='last', inplace=True)
        return self

    def detect_outliers(self, group, componente):
        group = group.copy()
        group['componente'] = componente
        mean = group['coste_componente_unitario'].mean()
        std = group['coste_componente_unitario'].std()
        group['z_score'] = 0
        group['is_outlier'] = False
        if std != 0:
            group['z_score'] = (group['coste_componente_unitario'] - mean) / std
            group['is_outlier'] = group['z_score'].abs() > 3
        return group

    def detectar_outliers_en_costes(self, df):
        grupos = []
        for componente, group in df.groupby('componente'):
            group_sin_componente = group.drop(columns='componente')
            grupos.append(self.detect_outliers(group_sin_componente, componente))
        return pd.concat(grupos, ignore_index=True)

    def corregir_outliers_iterativo(self, umbral=5):
        costes = self.costes.copy()
        sum_outliers = 10000
        count = 0

        while sum_outliers > umbral:
            costes = self.detectar_outliers_en_costes(costes)

            sin_outliers = costes[costes['is_outlier'] == False].copy()
            con_outliers = costes[costes['is_outlier'] == True].copy()

            medias_limpias = sin_outliers.groupby('componente')['coste_componente_unitario'].mean().to_dict()
            con_outliers['coste_componente_unitario'] = con_outliers['componente'].map(medias_limpias)

            con_outliers = self.detectar_outliers_en_costes(con_outliers)
            costes = pd.concat([sin_outliers, con_outliers], ignore_index=True)

            costes = self.detectar_outliers_en_costes(costes)
            sum_outliers = costes['is_outlier'].sum()
            count += 1

        self.costes = costes.drop(columns=['z_score', 'is_outlier'])
        print(f"Outliers finales: {sum_outliers}. Vuelta: {count}")
        return self

    def save_cleaned(self, output_path='costes_clean.csv'):
        self.costes.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Archivo guardado como {output_path}")
        return self


