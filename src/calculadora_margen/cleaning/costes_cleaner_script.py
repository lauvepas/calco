import pandas as pd
import regex as re
#from files import data_source

costes = pd.read_csv('costes.csv',  encoding='UTF-8', sep=';', dtype=str)

# Eliminamos filas y columnas inncesarias o duplicadas
costes.dropna(subset=['PRCMONEDA'], inplace=True)
costes = costes.drop_duplicates().copy()

costes = costes.drop(columns=[
    'Cód. almacén estructura',
    '% descuento 1',
    'DESCALM',
    'Artículo',
    'FECCADUC',
    'UNIDADES',
    'TIPDOC',
    'NUMDOC',
    'LOTE',
    'REFERENCIA',
    'FECDOC',
    'Cód. proveedor',   # cuando anonimice esta columna no estará
    'NOMPRO'   # cuando anonimice esta columna no estará
    ])

# Renombramos las columnas
costes_renaming_dic = {
    "Cód. artículo": "componente",
    "PRCMONEDA": "coste_componente_unitario",
    "LOTEINTERNO": "lote_interno"
}
costes = costes.rename(columns=costes_renaming_dic)

# Eliminamos puntos de millar y reemplazamos comas por puntos. Definimos como float
costes['coste_componente_unitario'] = costes['coste_componente_unitario'].str.replace('.', '')
costes['coste_componente_unitario'] = costes['coste_componente_unitario'].str.replace(',', '.').astype(float)

# Comprobamos que no tenemos ningún valor nulo
costes.isnull().sum()
costes.info()


######### VOY POR AQUÍ


# Outliers en 'componente'
pattern = re.compile(r'^[\p{L}]+[0-9]{2,3}$')
invalid_rows = costes[~costes['componente'].apply(lambda x: bool(pattern.fullmatch(x)))]
print(invalid_rows)
# Eliminamos códigos mal definidos
costes = costes[costes['componente'].apply(lambda x: bool(pattern.fullmatch(x)))]

# ouliers en 'lote_interno'
pattern = re.compile(r'^[0-9]{4}-[0-9]{3}$')
invalid_rows = costes[~costes['lote_interno'].apply(lambda x: bool(pattern.fullmatch(x)))]
print(invalid_rows.count())
print(invalid_rows['componente'].unique())
# Eliminamos códigos mal definidos
costes = costes[costes['lote_interno'].apply(lambda x: bool(pattern.fullmatch(x)))]


def remove_duplicated_batch(df, columna='lote_interno'):
    """
    Elimina duplicados en la columna especificada, manteniendo la última aparición.
    Muestra cuántos duplicados había antes y después.
    Eliminamos duplicados manteniendo la última aparición (son compras a las que por error se las ha cambiado el precio. El bueno es el último)

    Parámetros:
        df (pd.DataFrame): El DataFrame original (se modifica en el lugar).
        columna (str): Nombre de la columna donde buscar duplicados (por defecto: 'lote_interno').

    Retorna:
        pd.DataFrame: El DataFrame sin duplicados (referencia al mismo, si inplace=True).
    """
    dup_antes = df[columna].duplicated().sum()
    df.drop_duplicates(subset=columna, keep='last', inplace=True)
    dup_despues = df[columna].duplicated().sum()
    print(f"Hemos pasado de {dup_antes} a {dup_despues} duplicados en '{columna}'.")
    return df

costes = remove_duplicated_batch(costes).copy()

def detect_outliers(group, componente):
    group = group.copy()
    group['componente'] = componente  # Restauramos la columna que eliminamos antes

    mean = group['coste_componente_unitario'].mean()
    std = group['coste_componente_unitario'].std()

    if std == 0:
        group['z_score'] = 0
        group['is_outlier'] = False
    else:
        group['z_score'] = (group['coste_componente_unitario'] - mean) / std
        group['is_outlier'] = group['z_score'].abs() > 3

    return group

def detectar_outliers_en_costes(df):
    df = df.copy()

    grupos = []
    for componente, group in df.groupby('componente'):
        group_sin_componente = group.drop(columns='componente')
        grupos.append(detect_outliers(group_sin_componente, componente))

    df_outliers = pd.concat(grupos, ignore_index=True)
    return df_outliers


# Podemos llegar a dejar 0 outliers pero en la vuelta 18. No compensa el tiempo que tarda en realizar la operación.

sum_outliers_3 = 10000
count = 0

while sum_outliers_3 > 5:
    # 1. Detectar outliers sin warning
    costes = detectar_outliers_en_costes(costes)

    sum_outliers_1 = costes['is_outlier'].sum()

    # 2. Separar
    sin_outliers = costes[costes['is_outlier'] == False].copy()
    con_outliers = costes[costes['is_outlier'] == True].copy()

    # 3. Medias limpias
    medias_limpias = sin_outliers.groupby('componente')['coste_componente_unitario'].mean().to_dict()

    # 4. Sustituir
    con_outliers['coste_componente_unitario'] = con_outliers['componente'].map(medias_limpias)

    # 5. Detectar de nuevo
    con_outliers = detectar_outliers_en_costes(con_outliers)

    sum_outliers_2 = con_outliers['is_outlier'].sum()

    # 6. Concatenar
    costes = pd.concat([sin_outliers, con_outliers], ignore_index=True)

    # 7. Detectar final
    costes = detectar_outliers_en_costes(costes)

    sum_outliers_3 = costes['is_outlier'].sum()
    count += 1

print(f"Outliers finales: {sum_outliers_3}. Vuelta: {count}")

costes = costes.drop(columns=[
    'z_score',
    'is_outlier',
    ])

costes.to_csv('costes_clean.csv', index=False, encoding='utf-8')