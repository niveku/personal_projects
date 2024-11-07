import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def simulador_credito_hipotecario(valor_financiado, tasa_mensual, plazo_meses):
    cuota_mensual = valor_financiado * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
    return cuota_mensual

def simulador_leasing(valor_financiado, tasa_mensual, plazo_meses, valor_residual):
    cuota_mensual = (valor_financiado * tasa_mensual * ((1 + tasa_mensual) ** plazo_meses) - valor_residual * tasa_mensual) / ((1 + tasa_mensual) ** plazo_meses - 1)
    return cuota_mensual

def generar_tabla_credito(valor_financiado, tasa_mensual, plazo_meses, valor_residual, referencia, seguros, modo='hipotecario'):

    # Generar las cuotas de acuerdo al modo
    if modo == 'leasing':
        cuota = simulador_leasing(valor_financiado, tasa_mensual, plazo_meses, valor_residual)
    else:
        cuota = simulador_credito_hipotecario(valor_financiado, tasa_mensual, plazo_meses)

    cuota = round(cuota) + seguros

    # Crear la tabla de amortización
    datos = []
    saldo_restante = valor_financiado
    for mes in range(1, plazo_meses + 1):
        interes_mes = round(saldo_restante * tasa_mensual)
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
modo_diccionario = {"Crédito Hipotecario": "hipotecario", "Leasing Habitacional": "leasing"}
modo_simple = modo_diccionario.get(modo_simulador)

# Opciones adicionales para leasing
tabla = pd.DataFrame()
if modo_simple == "leasing":
    opcion_compra = st.sidebar.slider("Opcion Compra (%)", min_value=0, max_value=20, value=20)
else:
    opcion_compra = 0

# Parámetros Calculados
valor_residual = valor_inmueble * (opcion_compra / 100) if modo_simple == "leasing" else 0
valor_financiado = valor_inmueble - cuota_inicial - valor_residual
plazo_meses = plazo_anios * 12
tasa_mensual = tasa_interes_anual / 12 / 100
seguro_vida = round(valor_inmueble * 14.5e-5)
seguro_terremoto = round(valor_inmueble * 9.95e-5)
seguros = seguro_vida + seguro_terremoto
tabla = generar_tabla_credito(valor_financiado, tasa_mensual, plazo_meses, valor_residual, arriendo_referencia, seguros, modo=modo_simple)

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
precio_inmueble_range = np.arange(250_000_000, 750_000_000, 10_000_000)
cuota_inicial_range = np.arange(0, 250_000_000, 5_000_000)

# Lista para almacenar los resultados
sentidos_cero = []

# Calcular el sentido para cada combinación de precio del inmueble y cuota inicial
for valor_inmueble in precio_inmueble_range:
    sentido_linea = []
    for cuota_inicial in cuota_inicial_range:
        # Obtener el valor de "sentido" para el primer mes
        financiado = valor_inmueble - cuota_inicial
        tabla = generar_tabla_credito(financiado, tasa_mensual, plazo_meses, valor_residual, arriendo_referencia, seguros, modo=modo_simple)
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

# --------------------- Ganancias ------------------
# Rango de cuota inicial
cuota_inicial_range = np.linspace(50000000, valor_inmueble * 0.8, 100)

# Cálculo de la ganancia y retorno
ganancias = []
retornos_anuales = []

for cuota_inicial in cuota_inicial_range:
    monto_financiado = valor_inmueble - cuota_inicial
    if modo_simple == 'leasing':
        cuota = simulador_leasing(monto_financiado, tasa_mensual, plazo_meses, valor_residual)
    else:
        cuota = simulador_credito_hipotecario(monto_financiado, tasa_mensual, plazo_meses)

    ganancia = arriendo_referencia - (cuota + seguros)
    ganancias.append(ganancia)

    # Cálculo del retorno efectivo anual
    inversion_total = cuota_inicial + valor_residual
    retorno_anual = (ganancia * 12 / inversion_total) * 100
    retornos_anuales.append(retorno_anual)

# Gráfico interactivo de Ganancia vs. Cuota Inicial
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=cuota_inicial_range / 1e6,
    y=ganancias,
    mode="lines+markers",
    name="Ganancia Mensual (COP)",
    hovertemplate="Cuota Inicial: %{x:.1f}M<br>Ganancia: %{y:.0f} COP"
))

fig1.add_trace(go.Scatter(
    x=cuota_inicial_range / 1e6,
    y=retornos_anuales,
    mode="lines+markers",
    name="Retorno E.A (%)",
    yaxis="y2",
    hovertemplate="Cuota Inicial: %{x:.1f}M<br>Retorno E.A: %{y:.2f}%"
))

fig1.update_layout(
    title="Ganancia y Retorno E.A en función de la Cuota Inicial",
    xaxis=dict(title="Cuota Inicial (Millones de COP)", tickformat=".1f"),
    yaxis=dict(title="Ganancia Mensual (COP)", tickformat=".1f"),
    yaxis2=dict(
        title="Retorno E.A (%)",
        overlaying="y",
        side="right",
    ),
    legend=dict(x=0.01, y=0.99),
    hovermode="x unified",
)

# Línea horizontal en y=0
fig1.add_shape(type="line", x0=cuota_inicial_range[0] / 1e6, x1=cuota_inicial_range[-1] / 1e6, y0=0, y1=0,
               line=dict(color="red", width=2, dash="dash"))

st.plotly_chart(fig1)

# Gráfico interactivo de Ganancia vs. Tiempo
meses = np.arange(1, plazo_meses + 1)
ganancias_tiempo = []
arriendo_ajustado = arriendo_referencia  # Valor inicial del arriendo
ipc_anual = st.number_input("Porcentaje de crecimiento anual del arriendo (IPC)", value=4.0, step=0.5) / 100

for mes in meses:
    if mes % 12 == 1 and mes > 1:  # Ajuste anual cada 12 meses
        arriendo_ajustado *= (1 + ipc_anual)

    cuota_inicial = cuota_inicial_range[0]  # Ejemplo con una cuota inicial fija
    monto_financiado = valor_inmueble - cuota_inicial
    if modo_simple == 'leasing':
        cuota = simulador_leasing(monto_financiado, tasa_mensual, plazo_meses, valor_residual)
    else:
        cuota = simulador_credito_hipotecario(monto_financiado, tasa_mensual, plazo_meses)

    ganancia = arriendo_ajustado - (cuota + seguros)
    ganancias_tiempo.append(ganancia)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=meses,
    y=ganancias_tiempo,
    mode="lines+markers",
    name="Ganancia Mensual en el Tiempo",
    hovertemplate="Mes: %{x}<br>Ganancia: %{y:.0f} COP"
))

fig2.update_layout(
    title="Ganancia en función del Tiempo con Ajuste por IPC",
    xaxis=dict(
        title="Tiempo (Meses)",
        tickvals=np.arange(0, plazo_meses + 1, 12),
        ticktext=[f"Año {i}" for i in range(0, plazo_meses // 12 + 1)]
    ),
    yaxis=dict(title="Ganancia Mensual (COP)", tickformat=".1f"),
)

# Línea horizontal en y=0
fig2.add_shape(type="line", x0=1, x1=plazo_meses, y0=0, y1=0,
               line=dict(color="red", width=2, dash="dash"))

st.plotly_chart(fig2)