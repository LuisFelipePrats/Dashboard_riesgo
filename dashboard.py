import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
import json
import urllib.request

df = pd.read_excel('temp_excel.xlsx', engine='openpyxl')(url, db_name='panel_riesgo.db'):
    urllib.request.urlretrieve(url, 'temp_excel.xlsx')
    df = pd.read_excel('temp_excel.xlsx')
    df.fillna(0, inplace=True)
    df['id'] = df['Rut'].astype(str)
    df['nombre'] = df['Cliente'].astype(str)
    df['comportamiento'] = df.apply(
        lambda row: json.dumps({
            'dicom': row['Dicom (MM$)'],
            'deuda_tgr': row['Deuda TGR (MM$)'],
            'cumplimiento': row['Cumplimiento de pago (días)'],
            'multas_cte': row['Multas CTE (MM$)']
        }), axis=1
    )
    df['solvencia'] = df.apply(
        lambda row: json.dumps({
            'patrimonio': row['Patrimonio (MM$)'],
            'razon_corriente': row['Razón corriente'],
            'deuda_patrimonio': row['Deuda/ Patrimonio']
        }), axis=1
    )
    df['rentabilidad'] = df.apply(
        lambda row: json.dumps({
            'margen': row['Margen (resultado bruto)'],
            'resultado_antes': row['Resultado antes impuestos'],
            'resultado_despues': row['Resultado dp impuestos'],
            'gastos_financieros': row['Gastos financieros']
        }), axis=1
    )
    df['solidez'] = df.apply(
        lambda row: json.dumps({
            'controladores': row['Controladores reconocidos'],
            'sector': row['Industria o sector económico'],
            'tamano': row['Tamaño de la Empresa'],
            'antiguedad': row['Antigüedad (años)'],
            'bolsas': row['Registro en bolsas internacionales, IPSA o multinacional']
        }), axis=1
    )
    df['calidad_deudores'] = df.apply(
        lambda row: json.dumps({
            'dicom_deudores': row['Dicom deudores (MM$)'],
            'liquidez_deudores': row['Liquidez deudores'],
            'rentabilidad_deudores': row['Rentabilidad de deudores'],
            'solidez_deudores': row['Solidez institucional deudores'],
            'tamano_deudores': row['Tamaño y trayectoria deudores']
        }), axis=1
    )
    columns = ['id', 'nombre', 'grupo', 'sector', 'producto', 'linea_aprobada', 'linea_utilizada',
               'dicom_marzo', 'dicom_abril', 'dicom_mayo', 'dicom_junio', 'dicom_julio', 'promedio_dicom',
               'montos_demandas', 'comportamiento', 'solvencia', 'rentabilidad', 'solidez', 'calidad_deudores']
    for col in columns:
        if col not in df.columns:
            df[col] = 0 if col.startswith('dicom') or col.startswith('linea') or col == 'montos_demandas' else ''
    df = df[columns]
    conn = sqlite3.connect(db_name)
    df.to_sql('clientes', conn, if_exists='replace', index=False)
    conn.close()

# Reemplaza con tu enlace de Google Drive
import os
def load_excel_to_sqlite_from_url(url, db_name='panel_riesgo.db'):
    urllib.request.urlretrieve(url, 'temp_excel.xlsx')
    df = pd.read_excel('temp_excel.xlsx', engine='openpyxl')
    df.fillna(0, inplace=True)
    df['id'] = df['Rut'].astype(str)
    # resto del código...(os.getenv("GOOGLE_DRIVE_URL"))

def calcular_nota_comportamiento(dicom, deuda_tgr, cumplimiento, multas):
    try:
        dicom_val = float(dicom.split(' - ')[-1]) if '-' in dicom else float(dicom.replace('≤ ', ''))
        nota_dicom = 7 if dicom_val <= 10 else 5 if dicom_val <= 50 else 3 if dicom_val <= 200 else 1
    except:
        nota_dicom = 3
    try:
        deuda_val = float(deuda_tgr.split(' - ')[-1]) if '-' in deuda_tgr else float(deuda_tgr.replace('≤ ', ''))
        nota_deuda = 7 if deuda_val <= 10 else 5 if deuda_val <= 50 else 3
    except:
        nota_deuda = 3
    nota_cumplimiento = 7 if cumplimiento == 'Vigente' else 5 if cumplimiento == '1 - 30' else 3 if cumplimiento == '31 - 60' else 1
    try:
        multas_val = float(multas.split(' - ')[-1]) if '-' in multas else float(multas.replace('≤ ', ''))
        nota_multas = 7 if multas_val <= 10 else 5 if multas_val <= 50 else 3
    except:
        nota_multas = 3
    return (nota_dicom * 0.4 + nota_deuda * 0.3 + nota_cumplimiento * 0.2 + nota_multas * 0.1)

def calcular_nota_solvencia(patrimonio, razon_corriente, deuda_patrimonio):
    try:
        patrimonio_val = float(patrimonio.replace('> ', '').replace('< ', '')) if isinstance(patrimonio, str) else patrimonio
        nota_patrimonio = 7 if patrimonio_val >= 30000 else 5 if patrimonio_val >= 5000 else 3
    except:
        nota_patrimonio = 3
    try:
        razon_val = float(razon_corriente.split(' - ')[-1]) if '-' in razon_corriente else float(razon_corriente.replace('≤ ', ''))
        nota_razon = 7 if razon_val >= 1.5 else 5 if razon_val >= 1.0 else 3
    except:
        nota_razon = 3
    try:
        deuda_val = float(deuda_patrimonio.split(' - ')[-1]) if '-' in deuda_patrimonio else float(deuda_patrimonio.replace('≤ ', ''))
        nota_deuda = 7 if deuda_val <= 0.8 else 5 if deuda_val <= 1.4 else 3
    except:
        nota_deuda = 3
    return (nota_patrimonio * 0.4 + nota_razon * 0.3 + nota_deuda * 0.3)

def calcular_nota_rentabilidad(margen, resultado_antes, resultado_despues, gastos):
    try:
        margen_val = float(margen.strip('%').split(' - ')[-1]) if '-' in margen else float(margen.strip('%').replace('> ', ''))
        nota_margen = 7 if margen_val >= 20 else 5 if margen_val >= 10 else 3
    except:
        nota_margen = 3
    try:
        antes_val = float(resultado_antes.strip('%').split(' - ')[-1]) if '-' in resultado_antes else float(resultado_antes.strip('%').replace('< ', ''))
        nota_antes = 7 if antes_val >= 10 else 5 if antes_val >= 5 else 3
    except:
        nota_antes = 3
    try:
        despues_val = float(resultado_despues.strip('%').split(' - ')[-1]) if '-' in resultado_despues else float(resultado_despues.strip('%').replace('< ', ''))
        nota_despues = 7 if despues_val >= 10 else 5 if despues_val >= 5 else 3
    except:
        nota_despues = 3
    try:
        gastos_val = float(gastos.strip('%').split(' - ')[-1]) if '-' in gastos else float(gastos.strip('%').replace('≤ ', ''))
        nota_gastos = 7 if gastos_val <= 5 else 5 if gastos_val <= 10 else 3
    except:
        nota_gastos = 3
    return (nota_margen * 0.4 + nota_antes * 0.3 + nota_despues * 0.2 + nota_gastos * 0.1)

def calcular_nota_solidez(antiguedad, tamano, bolsas):
    nota_antiguedad = 7 if antiguedad == '> 10' else 5 if antiguedad == '5 - 10' else 3
    nota_tamano = 7 if 'Empresa grande' in tamano else 5 if 'Empresa mediana' in tamano else 3
    nota_bolsas = 7 if bolsas == 'Sí' else 4
    return (nota_antiguedad * 0.4 + nota_tamano * 0.3 + nota_bolsas * 0.3)

def calcular_nota_calidad_deudores(dicom_deudores, liquidez_deudores, rentabilidad_deudores):
    try:
        dicom_val = float(dicom_deudores.split(' - ')[-1]) if '-' in dicom_deudores else float(dicom_deudores.replace('> ', ''))
        nota_dicom = 7 if dicom_val <= 50 else 5 if dicom_val <= 200 else 3
    except:
        nota_dicom = 3
    try:
        liquidez_val = float(liquidez_deudores.split(' - ')[-1]) if '-' in liquidez_deudores else float(liquidez_deudores.replace('≤ ', ''))
        nota_liquidez = 7 if liquidez_val >= 1.5 else 5 if liquidez_val >= 1.0 else 3
    except:
        nota_liquidez = 3
    try:
        rentabilidad_val = float(rentabilidad_deudores.strip('%').split(' - ')[-1]) if '-' in rentabilidad_deudores else float(rentabilidad_deudores.strip('%').replace('< ', ''))
        nota_rentabilidad = 7 if rentabilidad_val <= 5 else 5 if rentabilidad_val <= 20 else 3
    except:
        nota_rentabilidad = 3
    return (nota_dicom * 0.4 + nota_liquidez * 0.3 + nota_rentabilidad * 0.3)

def calcular_nota_final(comportamiento, solvencia, rentabilidad, solidez, calidad):
    return (comportamiento * 0.3 + solvencia * 0.25 + rentabilidad * 0.2 + solidez * 0.15 + calidad * 0.1)

def clasificar_nota(nota):
    if nota >= 6.5:
        return 'A1'
    elif nota >= 5.5:
        return 'A2'
    elif nota >= 4.5:
        return 'B1'
    elif nota >= 3.5:
        return 'B2'
    else:
        return 'C'

app = dash.Dash(__name__)

conn = sqlite3.connect('panel_riesgo.db')
df = pd.read_sql_query("SELECT * FROM clientes", conn)
conn.close()

app.layout = html.Div([
    html.H1("Dashboard de Riesgo - Junio 2025", style={'textAlign': 'center'}),
    html.Label("Seleccionar Cliente:"),
    dcc.Dropdown(
        id='cliente-dropdown',
        options=[{'label': nombre, 'value': id} for nombre, id in zip(df['nombre'], df['id'])],
        value=df['id'][0],
        style={'width': '50%', 'margin': 'auto'}
    ),
    html.Br(),
    html.Div(id='resumen-cliente', style={'textAlign': 'center'}),
    dcc.Graph(id='radar-categorias'),
    dash_table.DataTable(
        id='tabla-detalle',
        columns=[
            {'name': 'Categoría', 'id': 'Categoría'},
            {'name': 'Variable', 'id': 'Variable'},
            {'name': 'Valor', 'id': 'Valor'},
            {'name': 'Nota', 'id': 'Nota'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    ),
    html.Div(id='alertas-recomendaciones', style={'margin': '20px', 'color': 'red'}),
    dcc.Graph(id='dicom-evolution', style={'width': '50%', 'margin': 'auto'})
])

@app.callback(
    [Output('resumen-cliente', 'children'),
     Output('radar-categorias', 'figure'),
     Output('tabla-detalle', 'data'),
     Output('alertas-recomendaciones', 'children'),
     Output('dicom-evolution', 'figure')],
    [Input('cliente-dropdown', 'value')]
)
def update_dashboard(cliente_id):
    cliente_data = df[df['id'] == cliente_id].iloc[0]
    comportamiento = json.loads(cliente_data['comportamiento'])
    solvencia = json.loads(cliente_data['solvencia'])
    rentabilidad = json.loads(cliente_data['rentabilidad'])
    solidez = json.loads(cliente_data['solidez'])
    calidad_deudores = json.loads(cliente_data['calidad_deudores'])

    nota_comportamiento = calcular_nota_comportamiento(
        comportamiento['dicom'], comportamiento['deuda_tgr'],
        comportamiento['cumplimiento'], comportamiento['multas_cte']
    )
    nota_solvencia = calcular_nota_solvencia(
        solvencia['patrimonio'], solvencia['razon_corriente'], solvencia['deuda_patrimonio']
    )
    nota_rentabilidad = calcular_nota_rentabilidad(
        rentabilidad['margen'], rentabilidad['resultado_antes'],
        rentabilidad['resultado_despues'], rentabilidad['gastos_financieros']
    )
    nota_solidez = calcular_nota_solidez(
        solidez['antiguedad'], solidez['tamano'], solidez['bolsas']
    )
    nota_calidad = calcular_nota_calidad_deudores(
        calidad_deudores['dicom_deudores'], calidad_deudores['liquidez_deudores'],
        calidad_deudores['rentabilidad_deudores']
    )
    nota_final = calcular_nota_final(nota_comportamiento, nota_solvencia, nota_rentabilidad, nota_solidez, nota_calidad)
    clasificacion = clasificar_nota(nota_final)

    resumen = [
        html.H3(f"Cliente: {cliente_data['nombre']}"),
        html.P(f"Grupo: {cliente_data['grupo']} | Sector: {cliente_data['sector']}"),
        html.P(f"Producto: {cliente_data['producto']}"),
        html.P(f"Puntaje Final: {nota_final:.2f} ({clasificacion})", style={'fontWeight': 'bold'}),
        html.P(f"Dicom Promedio: {cliente_data['promedio_dicom']:,.0f} CLP"),
        html.P(f"Montos Demandados: {cliente_data['montos_demandas']:,.0f} CLP"),
        html.P(f"Línea Utilizada: {cliente_data['linea_utilizada']:,.0f} CLP")
    ]

    radar_data = pd.DataFrame({
        'Categoría': ['Comportamiento', 'Solvencia', 'Rentabilidad', 'Solidez', 'Calidad Deudores'],
        'Nota': [nota_comportamiento, nota_solvencia, nota_rentabilidad, nota_solidez, nota_calidad]
    })
    fig_radar = px.line_polar(radar_data, r='Nota', theta='Categoría', line_close=True, title="Desglose por Categorías")

    tabla_data = [
        {'Categoría': 'Comportamiento', 'Variable': 'Dicom (MM$)', 'Valor': comportamiento['dicom'], 'Nota': f"{nota_comportamiento:.2f}"},
        {'Categoría': 'Comportamiento', 'Variable': 'Cumplimiento', 'Valor': comportamiento['cumplimiento'], 'Nota': f"{nota_comportamiento:.2f}"},
        {'Categoría': 'Solvencia', 'Variable': 'Patrimonio (MM$)', 'Valor': solvencia['patrimonio'], 'Nota': f"{nota_solvencia:.2f}"},
        {'Categoría': 'Solvencia', 'Variable': 'Razón Corriente', 'Valor': solvencia['razon_corriente'], 'Nota': f"{nota_solvencia:.2f}"},
        {'Categoría': 'Rentabilidad', 'Variable': 'Margen', 'Valor': rentabilidad['margen'], 'Nota': f"{nota_rentabilidad:.2f}"},
        {'Categoría': 'Solidez', 'Variable': 'Antigüedad', 'Valor': solidez['antiguedad'], 'Nota': f"{nota_solidez:.2f}"},
        {'Categoría': 'Calidad Deudores', 'Variable': 'Dicom Deudores (MM$)', 'Valor': calidad_deudores['dicom_deudores'], 'Nota': f"{nota_calidad:.2f}"}
    ]

    alertas = []
    if cliente_data['montos_demandas'] > 1000000000:
        alertas.append(html.P(f"ALERTA CRÍTICA: Montos demandados elevados ({cliente_data['montos_demandas']:,.0f} CLP)", style={'color': 'red'}))
    if cliente_data['promedio_dicom'] > 200:
        alertas.append(html.P(f"ALERTA: Dicom promedio elevado ({cliente_data['promedio_dicom']:,.0f} CLP)", style={'color': 'orange'}))
    if nota_final < 4.5:
        alertas.append(html.P("ALERTA: Riesgo alto detectado", style={'color': 'red'}))

    recomendaciones = []
    if cliente_data['montos_demandas'] > 1000000000:
        recomendaciones.append(html.P("Recomendación: Exigir garantías adicionales"))
    elif nota_final < 4.5:
        recomendaciones.append(html.P("Recomendación: Revisar condiciones de crédito"))
    else:
        recomendaciones.append(html.P("Recomendación: Continuar con monitoreo regular"))

    dicom_data = pd.DataFrame({
        'Mes': ['Marzo', 'Abril', 'Mayo', 'Junio', 'Julio'],
        'Dicom': [cliente_data['dicom_marzo'], cliente_data['dicom_abril'], cliente_data['dicom_mayo'],
                  cliente_data['dicom_junio'], cliente_data['dicom_julio']]
    })
    fig_dicom = px.line(dicom_data, x='Mes', y='Dicom', title='Evolución de Dicom (CLP)', markers=True)

    return resumen, fig_radar, tabla_data, alertas + recomendaciones, fig_dicom

if __name__ == '__main__':
    app.run_server(debug=True)
