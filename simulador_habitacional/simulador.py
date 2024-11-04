import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import streamlit as st


def simulador_credito_hipotecario(valor_financiado, tasa_mensual, plazo_meses):
    cuota_mensual = valor_financiado * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
    return cuota_mensual

def simulador_leasing(valor_financiado, tasa_mensual, plazo_meses, valor_residual):
    # Ajuste en la fórmula para considerar la opción de compra
    cuota_mensual = (valor_financiado * tasa_mensual * ((1 + tasa_mensual) ** plazo_meses) - valor_residual * tasa_mensual) / ((1 + tasa_mensual) ** plazo_meses - 1)
    return cuota_mensual

def generar_tabla_credito(valor_inmueble, cuota_inicial, tasa_interes_anual, plazo_anios, referencia, modo='hipotecario', opcion_compra=0):
    # Cálculos iniciales
    valor_residual = valor_inmueble * (opcion_compra / 100) if modo == 'leasing' else 0
    valor_financiado = valor_inmueble - cuota_inicial - valor_residual
    plazo_meses = plazo_anios * 12
    tasa_mensual = tasa_interes_anual / 12 / 100
    seguro_vida = round(valor_inmueble * 14.5e-5)
    seguro_terremoto = round(valor_inmueble * 9.95e-5)

    # Generar las cuotas de acuerdo al modo
    if modo == 'leasing':
        cuota = simulador_leasing(valor_financiado, tasa_mensual, plazo_meses, valor_residual)
    else:
        cuota = simulador_credito_hipotecario(valor_financiado, tasa_mensual, plazo_meses)

    cuota = round(cuota) + seguro_vida + seguro_terremoto

    # Crear la tabla de amortización
    datos = []
    saldo_restante = valor_financiado
    for mes in range(1, plazo_meses + 1):
        interes_mes = round(saldo_restante * tasa_mensual)
        seguros = seguro_vida + seguro_terremoto
        capital_mes = cuota - interes_mes -seguros
        sentido = referencia - interes_mes - seguros
        saldo_restante -= capital_mes
        datos.append({
            'Mes': mes,
            'Cuota': cuota,
            'Interés Pagado': interes_mes,
            'Capital Amortizado': capital_mes,
            'Seguros': seguros,
            'Saldo Restante': max(saldo_restante, valor_residual) if modo == 'leasing' and mes == plazo_meses else max(saldo_restante, 0),
            'Sentido': sentido
        })

    return pd.DataFrame(datos)

# Interfaz en Streamlit
st.title("Simulador de Crédito Hipotecario y Leasing Habitacional")

# Parámetros de entrada
st.sidebar.header("Parámetros del Simulador")
valor_inmueble = st.sidebar.number_input("Valor del Inmueble (COP)", min_value=100_000_000, value=530_000_000, step=5_000_000)
cuota_inicial = st.sidebar.number_input("Cuota Inicial (COP)", min_value=0, value=50_000_000, step=5_000_000)
tasa_interes_anual = st.sidebar.slider("Tasa de Interés Anual (%)", min_value=0.0, max_value=20.0, value=12.0, step=0.1)
plazo_anios = st.sidebar.slider("Plazo del Crédito (Años)", min_value=1, max_value=30, value=20)
arriendo_referencia = st.sidebar.slider("Valor de Arriendo de Referencia (COP)", min_value=1_000_000, max_value=10_000_000, value=3_000_000, step=100_000)
modo_simulador = st.sidebar.selectbox("Modo de Simulación", ("Crédito Hipotecario", "Leasing Habitacional"))

# Opciones adicionales para leasing
tabla = pd.DataFrame()
if modo_simulador == "Leasing Habitacional":
    opcion_compra = st.sidebar.slider("Opcion Compra (%)", min_value=0, max_value=20, value=20)
    tabla = generar_tabla_credito(valor_inmueble, cuota_inicial, tasa_interes_anual, plazo_anios, arriendo_referencia, modo='leasing', opcion_compra=opcion_compra)
else:
    opcion_compra = 0
    tabla = generar_tabla_credito(valor_inmueble, cuota_inicial, tasa_interes_anual, plazo_anios, arriendo_referencia, modo='hipotecario')

# Mostrar tabla y resumen
st.subheader(f"Tabla de Amortización - {modo_simulador}")
st.write(tabla)

cuota_mensual = tabla['Cuota'][0]

# Gráfico de saldo restante
st.subheader("Gráfica de Saldo Restante")
st.line_chart(tabla[['Mes', 'Saldo Restante']].set_index('Mes'))

# Gráfico de división de pagos en Interés y Capital Amortizado
st.subheader("División de Pagos en Interés y Capital Amortizado con Cuota Mensual")
grafico_pagos = tabla[['Mes', 'Interés Pagado', 'Capital Amortizado', 'Cuota']].set_index('Mes')
st.line_chart(grafico_pagos)

# Arriendo de referencia y cálculo de "sentido"
sentido = tabla['Sentido'][0]

st.metric(label="Cuota Mensual", value=f"{cuota_mensual:,.0f} COP")
if sentido > 0:
    st.metric(label="Sentido", value=f"{sentido:,.0f} COP", delta="Positivo", delta_color="normal")
else:
    st.metric(label="Sentido", value=f"{sentido:,.0f} COP", delta="Negativo", delta_color="inverse")

# -------------------------
# Genera los valores de rango para precio del inmueble y cuota inicial
precio_inmueble_range = np.arange(250_000_000, 700_000_000, 10_000_000)
cuota_inicial_range = np.arange(0, 250_000_000, 10_000_000)

# Lista para almacenar los resultados
sentidos_cero = []

# Calcular el sentido para cada combinación de precio del inmueble y cuota inicial
for valor_inmueble in precio_inmueble_range:
    sentido_linea = []
    for cuota_inicial in cuota_inicial_range:
        # Obtener el valor de "sentido" para el primer mes
        tabla = generar_tabla_credito(valor_inmueble, cuota_inicial, tasa_interes_anual, plazo_anios, arriendo_referencia, modo=modo_simulador.lower(), opcion_compra=opcion_compra)

        # Evita valores no válidos asignando 0 a `sentido` cuando es NaN o Inf
        sentido = tabla['Sentido'][0]
        if np.isnan(sentido) or np.isinf(sentido):
            sentido = 0  # Ajusta según prefieras

        sentido_linea.append(sentido)
    sentidos_cero.append(sentido_linea)

# Convertir a numpy array y reemplazar cualquier NaN o Inf remanente
sentidos_cero = np.nan_to_num(np.array(sentidos_cero), nan=0, posinf=0, neginf=0)

# Crear gráfico de línea de contorno donde el "sentido" es 0
plt.figure(figsize=(10, 6))
cp = plt.contourf(cuota_inicial_range, precio_inmueble_range, sentidos_cero, levels=20, cmap="RdYlGn")  # cmap para colores claros y oscuros
cbar = plt.colorbar(cp, label="Sentido")

# Agregar línea de contorno para sentido = 0
contour_zero = plt.contour(cuota_inicial_range, precio_inmueble_range, sentidos_cero, levels=[0], colors='blue', linewidths=2, linestyles='dashed')
plt.clabel(contour_zero, inline=True, fontsize=8, fmt='Sentido = 0')

# Formatear ejes para mostrar valores en millones
plt.title("Línea de Equilibrio del Sentido entre Cuota Inicial y Precio del Inmueble")
plt.xlabel("Cuota Inicial (COP)")
plt.ylabel("Precio del Inmueble (COP)")

# Función para formatear los ejes en millones
def format_millions(x, pos):
    return f'{int(x * 1e-6)}M'

# Aplicar formateo a los ejes
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_millions))
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_millions))

plt.grid(True)

# Mostrar el gráfico en Streamlit
st.pyplot(plt)

# ---------------------
# Rango de valores para el precio del inmueble y la tasa de interés
precio_inmueble_range = np.arange(400_000_000, 700_000_000, 5_000_000)  # 61 valores
tasa_interes_range = np.arange(0.01, 0.15, 0.005)  # 29 valores

# Crear una matriz para almacenar los resultados
sentidos_cero = np.zeros((len(tasa_interes_range), len(precio_inmueble_range)))

# Calcular el sentido para cada combinación de precio del inmueble y tasa de interés
for i, valor_inmueble in enumerate(precio_inmueble_range):
    for j, tasa_interes in enumerate(tasa_interes_range):
        # Obtener el valor de "sentido" para el primer mes
        tabla = generar_tabla_credito(valor_inmueble, cuota_inicial, tasa_interes, plazo_anios, arriendo_referencia, modo=modo_simulador.lower(), opcion_compra=opcion_compra)

        # Evitar valores no válidos asignando 0 a `sentido` cuando es NaN o Inf
        sentido = tabla['Sentido'][0]
        if np.isnan(sentido) or np.isinf(sentido):
            sentido = 0

        # Asignar el valor calculado en la matriz
        sentidos_cero[j, i] = sentido  # Nota: el índice se invierte aquí

# Crear gráfico de línea de contorno donde el "sentido" es 0
plt.figure(figsize=(10, 6))
cp = plt.contour(precio_inmueble_range, tasa_interes_range, sentidos_cero, levels=[0], colors='blue', linewidths=2)

# Etiquetar la línea de contorno para sentido = 0
plt.clabel(cp, inline=True, fontsize=8, fmt='Sentido = 0')

# Formatear ejes para mostrar valores en millones para el precio del inmueble
plt.title("Línea de Equilibrio del Sentido entre Precio del Inmueble y Tasa de Interés")
plt.xlabel("Precio del Inmueble (COP)")
plt.ylabel("Tasa de Interés")

# Función para formatear los ejes en millones
def format_millions(x, pos):
    return f'{int(x * 1e-6)}M'

# Aplicar formateo al eje X (Precio del Inmueble)
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_millions))

plt.grid(True)

# Mostrar el gráfico en Streamlit
st.pyplot(plt)