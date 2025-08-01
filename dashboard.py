import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3
import urllib.request
import sys

print("Iniciando el script...")

try:
    # Descargar el archivo desde la URL
    url = "https://drive.google.com/uc?export=download&id=1YfTmNvqU88XT7_ArGHC0YVlm9dgLVy1z"  # Tu URL
    urllib.request.urlretrieve(url, 'temp_excel.xlsx')
    print("Archivo descargado correctamente.")

    # Leer el Excel
    df = pd.read_excel('temp_excel.xlsx', engine='openpyxl')
    print("Excel leído correctamente. Columnas:", df.columns.tolist())
    df.fillna(0, inplace=True)

    # Guardar en SQLite
    db_name = 'panel_riesgo.db'
    conn = sqlite3.connect(db_name)
    df.to_sql('clientes', conn, if_exists='replace', index=False)
    conn.close()
    print("Datos guardados en", db_name)

    # Cargar datos desde SQLite
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    print("Datos cargados desde SQLite. Filas:", len(df), "Columnas:", df.columns.tolist())

    if df.empty:
        print("Error: El DataFrame está vacío.")
        sys.exit(1)
    print("Datos verificados. Preparando dashboard...")

    # Configurar el dashboard
    app = dash.Dash(__name__)
    print("Dashboard configurado.")

    app.layout = html.Div([
        html.H1("Dashboard Financiero", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='cliente-dropdown',
            options=[{'label': row['Cliente (Ordenado por colocación)'], 'value': idx} for idx, row in df.iterrows()],
            value=df.index[0] if not df.empty else None,
            style={'width': '50%', 'margin': 'auto'}
        ),
        html.Div(id='output-div')
    ])

    @app.callback(
        Output('output-div', 'children'),
        Input('cliente-dropdown', 'value')
    )
    def update_output(value):
        if df.empty or value is None:
            return html.Div("No hay datos para mostrar.")
        selected = df.iloc[value]
        return html.Div([
            html.H3(f"Cliente: {selected['Cliente (Ordenado por colocación)']}"),
            html.P(f"Ventas anuales: ${selected['Ventas anuales']:,.2f}"),
            html.P(f"Deuda/Patrimonio: {selected['Deuda/Patrimonio']:.2f}")
        ])

    print("Iniciando el servidor Dash...")
    app.run(debug=True)

except Exception as e:
    print(f"Error crítico: {e}", file=sys.stderr)
    sys.exit(1)

print("Script terminado (esto no debería aparecer si Dash se ejecuta).")
