import pandas as pd
import re

master_lotes = pd.read_csv('costes.csv',  encoding='UTF-8', sep=';', dtype=str)
master_lotes.info()

master_lotes = master_lotes.drop(columns=[
    'Unnamed: 0',
    'Almacén',
    'Descripción',
    'Stock Unidades',
    'Ubicación',
    'Fecha Entrada',
    'Proveedor',
    'Caducidad',
    'Entradas Previstas',
    'Salidas Previstas',
    'Fecha Salida Prevista'
    ])

master_lotes_renaming_dict = {
    "Artículo": "articulo",
    "Lote/Nº Serie": "lote_proveedor",
    "Lote Interno": "lote_interno"
}

master_lotes = master_lotes.rename(columns=master_lotes_renaming_dict)

master_lotes.dropna(subset=['lote_interno'], inplace=True)
master_lotes = master_lotes.drop_duplicates()

def clasificar_linea(articulo):
    if re.search(r'sem', articulo, re.IGNORECASE):
        return 'SEMIELABORADO'
    elif re.search(r'\b(MAT|MAUX|VAR)\b', articulo, re.IGNORECASE):
        return 'COMPONENTE'
    else:
        return 'PRODUCTO ACABADO'

master_lotes['linea'] = master_lotes['articulo'].apply(clasificar_linea)

master_lotes[master_lotes['linea'] == 'COMPONENTE']['lote_interno'].duplicated().sum()
master_lotes.info()
