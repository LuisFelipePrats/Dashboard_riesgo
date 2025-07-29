import pandas as pd

try:
    data = pd.read_excel("Panel_Integral_de_Gestión_Financiera_y_Riesgo.xlsx")
    print("El archivo Excel se abrió correctamente. Número de filas:", len(data))
except FileNotFoundError:
    print("Error: No se encontró el archivo Excel.")
except Exception as e:
    print("Error:", str(e))
    