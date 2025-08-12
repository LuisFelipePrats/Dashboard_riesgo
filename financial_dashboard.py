import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import urllib.request
import os
import sys

print("Iniciando el script...")

# Variable global para almacenar el DataFrame
df_global = None

# URL de Google Drive (ya proporcionada)
url = "https://drive.google.com/uc?export=download&id=1YfTmNvqU88XT7_ArGHC0YVlm9dgLVy1z"

try:
    # Descargar el archivo desde la URL
    urllib.request.urlretrieve(url, 'temp_excel.xlsx')
    print("Archivo descargado correctamente.")

    # Leer el Excel
    df = pd.read_excel('temp_excel.xlsx', sheet_name='Ratios financieros')
    print("Excel leído correctamente. Columnas:", df.columns.tolist())
    df.fillna(0, inplace=True)

    # Guardar en SQLite
    db_name = 'panel_riesgo.db'
    conn = sqlite3.connect(db_name)
    df.to_sql('datos_riesgo', conn, if_exists='replace', index=False)
    conn.close()
    print("Datos guardados en", db_name)

    # Cargar datos desde SQLite y almacenar globalmente
    conn = sqlite3.connect(db_name)
    df_global = pd.read_sql_query("SELECT * FROM datos_riesgo", conn)
    conn.close()
    print("Datos cargados desde SQLite. Filas:", len(df_global))

    # Verificar datos antes de configurar Dash
    if df_global.empty:
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
            options=[{'label': row['Cliente (Ordenado por colocación)'], 'value': idx} for idx, row in df_global.iterrows()],
            value=df_global.index[0] if not df_global.empty else None,
            style={'width': '50%', 'margin': 'auto'}
        ),
        html.Div(id='output-div', style={'padding': '20px'}),
        dcc.Graph(id='ventas-graph', style={'width': '100%', 'height': '400px'}),
        dcc.Graph(id='deuda-graph', style={'width': '100%', 'height': '400px'})
    ])

    @app.callback(
        [Output('output-div', 'children'),
         Output('ventas-graph', 'figure'),
         Output('deuda-graph', 'figure')],
        Input('cliente-dropdown', 'value')
    )
    def update_output(value):
        if df_global is None or df_global.empty or value is None:
            return html.Div("No hay datos para mostrar o error en el callback."), px.bar(), px.pie()
        try:
            selected = df_global.iloc[value]
            # Convertir a float, manejando valores no numéricos
            ventas_anuales = float(str(selected['Ventas anuales']).replace('$', '').replace(',', '').strip() or 0)
            deuda_patrimonio = float(str(selected['Deuda/Patrimonio']).replace(',', '').strip() or 0)
            patrimonio = float(str(selected['Patrimonio']).replace(',', '').strip() or 0)
            razon_corriente = float(str(selected['Razón corriente']).replace(',', '').strip() or 0)
            margen = float(str(selected['Margen (resultado bruto)']).replace(',', '').strip() or 0)
            resultado_antes = float(str(selected['Resultado antes de impuestos']).replace(',', '').strip() or 0)
            resultado_despues = float(str(selected['Resultado después de impuestos']).replace(',', '').strip() or 0)
            gastos_financieros = float(str(selected['Gastos financieros']).replace(',', '').strip() or 0)
            liquidez_inmediata = float(str(selected['Liquidez Inmediata']).replace(',', '').strip() or 0)

            # Resumen con todos los indicadores
            resumen = html.Div([
                html.H3(f"Cliente: {selected['Cliente (Ordenado por colocación)']}"),
                html.P(f"Ventas anuales: ${ventas_anuales:.2f}"),
                html.P(f"Deuda/Patrimonio: {deuda_patrimonio:.2f}"),
                html.P(f"Patrimonio: ${patrimonio:.2f}"),
                html.P(f"Razón corriente: {razon_corriente:.2f}"),
                html.P(f"Margen (resultado bruto): {margen:.2f}"),
                html.P(f"Resultado antes de impuestos: ${resultado_antes:.2f}"),
                html.P(f"Resultado después de impuestos: ${resultado_despues:.2f}"),
                html.P(f"Gastos financieros: ${gastos_financieros:.2f}"),
                html.P(f"Liquidez Inmediata: {liquidez_inmediata:.2f}")
            ], style={'columnCount': 2, 'padding': '10px'})

            # Gráfico de ventas por cliente
            fig_sales = px.bar(df_global, x='Cliente (Ordenado por colocación)', y='Ventas anuales',
                               title='Ventas Anuales por Cliente', height=400)

            # Gráfico de torta para Deuda/Patrimonio
            fig_debt = px.pie(df_global, names='Cliente (Ordenado por colocación)', values='Deuda/Patrimonio',
                              title='Relación Deuda/Patrimonio por Cliente', height=400)

            return resumen, fig_sales, fig_debt
        except Exception as e:
            return html.Div(f"Error en callback: {str(e)}"), px.bar(), px.pie()

    print("Intentando iniciar el servidor en 0.0.0.0:PORT...")
    port = int(os.environ.get('PORT', 10000))
    print(f"Iniciando servidor en 0.0.0.0:{port}...")
    app.run(debug=True, host='0.0.0.0', port=port)

except Exception as e:
    print(f"Error crítico: {e}", file=sys.stderr)
    sys.exit(1)

print("Script terminado (esto no debería aparecer si Dash se ejecuta).")
