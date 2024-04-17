import pandas as pd
from unidecode import unidecode
import requests
import sqlite3
import os

def limpieza(df):
    try:
        for columna in list(df.columns):
            df.rename(columns={columna: unidecode(columna.replace(" ", "_").lower())}, inplace=True)
        df.drop(['id', 'tipo_moneda.1'], axis=1, inplace=True)
        df["dispositivo_legal"] = df["dispositivo_legal"].replace({',':''}, regex=True)
    except:
        print("Ocurrió un error mientras se limpiaba los nombres unas columnas")

def cambiar_nombre(df):
    columnas = list(df.columns)
    while True:
        opcion = input("""¿Desea cambiar el nombre a alguna columna?
1) Sí
2) No
Opción: """)
        if opcion == '1':
            print(columnas)
            columna = input("¿Qué columna desea cambiar?: ")
            if columna in columnas:
                df.rename(columns={columna: input("Ingrese el nuevo nombre: ")}, inplace=True)
                print("¡NOMBRE CAMBIADO!")
            else:
                print("EL NOMBRE DE LA COLUMNA NO EXISTE")
        elif opcion == '2':
            break
        else:
            print("Opción inválida")

def sunat(df):
    try:
        response = requests.get(url='https://api.apis.net.pe/v1/tipo-cambio-sunat')
        data = response.json()
        venta = data['venta']
        df['monto_inversion_usd'] = df['monto_de_inversion'] / venta
        df['monto_transferencia_usd'] = df['monto_de_transferencia_2020'] / venta
        return df
    except:
        print("El API no funciona")

def reemplazo(df):
    try:
        df['estado'] = df['estado'].replace({'En Ejecución': 'Ejecución', 'Convenio y/o Contrato Resuelto': 'Resuelto'})
        df['estado_puntuacion'] = df['estado'].replace({'Actos Previos': 1, 'Resuelto': 0, 'Ejecución': 2, 'Concluido': 3})
        return df
    except:
        print("Hubo un problema con las columnas: estado, estado_puntuacion")

def reporte_1(df):
    try:
        with sqlite3.connect("./data/ubigeo.db") as conn:
            reporte_1 = df[['ubigeo', 'region', 'provincia', 'distrito']].drop_duplicates().sort_values(by='ubigeo', ascending=True)
            reporte_1.to_sql("ubigeo", conn, index=False, if_exists="replace")
    except:
        print("Ocurrió un problema al intentar crear el archivo .db")

def reporte_2(df):
    try:
        os.mkdir("./data/top_5")
    except:
        print("La carpeta ya existe")
    finally:
        try:
            regiones = df['region'].unique()
            for region in regiones:
                condicion = (df['region'] == region) & (df['ambito'] == 'URBANO') & (df['estado'].isin(['En ejecución', 'Actos Previos', 'Concluido']))
                df_filtro = df[condicion]
                top_obras = df_filtro.sort_values('monto_de_inversion', ascending=False).head(5)
                top_obras.to_excel(f'./data/top_5/{region}_top_obras.xlsx', index=False)
        except:
            print("Ocurrió un error cuando se intentó crear el top 5 por Regiones")

if __name__ == '__main__':
    df = pd.read_excel("./data/reactiva.xlsx", 'TRANSFERENCIAS 2020')
    limpieza(df)
    cambiar_nombre(df)
    df = sunat(df)
    df = reemplazo(df)
    #El reporte 1 se guarda en la carpeta 'data' como ubigeo.db
    reporte_1(df)
    #El reporte 2 crea una carpeta dentro de 'data' donde guardará todos los top 5 por regiones
    reporte_2(df)
    #SUELE OCURRIR UN MENSAJE EN LA TERMINAL, ESTE DICE QUE PRONTO YA NO SE PODRÁ USAR LA FUNCIÓN 'replace()' EN PANDAS, PERO POR AHORA NO INTERFIERE CON EL CÓDIGO