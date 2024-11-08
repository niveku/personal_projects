import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Función para formatear los ejes en millones
def format_millions(x, _pos):
    return f'{int(x * 1e-6)}M$'

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

    cuota = round(cuota)

    # Crear la tabla de amortización
    datos = []
    saldo_restante = valor_financiado
    arriendo_ajustado = referencia
    for mes in range(1, plazo_meses + 1):
        year = ((mes - 1) // 12) +1

        if mes % 12 == 1 and year > 1:  # Ajuste anual cada 12 meses
            arriendo_ajustado = round(arriendo_ajustado*(1 + ipc_anual))

        interes_mes = round(saldo_restante * tasa_mensual)
        capital_mes = cuota - interes_mes
        cuota_real = cuota + seguros
        ganancia = arriendo_ajustado - cuota_real

        # Factor de Equilibrio de Costos (FEC)
        FEC = (1 - (cuota / (arriendo_ajustado * 1.1))) * 100  # Va de -100 a 0 en relación a la cuota

        # Factor de Eficiencia de Capital (FECap)
        FECap = min(1, capital_mes / (cuota * 0.5)) * 100  # Asegura máximo de 100%

        # Cálculo de "Sentido" combinando ambos factores
        sentido = round(FEC + FECap*0.6, 1)

        equilibrio = arriendo_ajustado - interes_mes - seguros
        saldo_restante -= capital_mes

        datos.append({
            'Año': year,
            'Mes': mes,
            'Cuota': cuota_real,
            'Interés Pagado': interes_mes,
            'Capital Amortizado': capital_mes,
            'Seguros': seguros,
            'Saldo Restante': max(saldo_restante, valor_residual) if modo == 'leasing' and mes == plazo_meses else max(saldo_restante, 0),
            'Arriendo': arriendo_ajustado,
            'Ganancia': ganancia,
            'Equilibrio': equilibrio,
            'Sentido': sentido
        })

    return pd.DataFrame(datos)

def calcular_equilibrio_interes(valor_financiado, tasa, seguros):
    intereses = (valor_financiado) * tasa
    sentido_cal = arriendo_referencia - intereses - seguros
    return sentido_cal

# Interfaz en Streamlit
st.title("Simulador de Crédito Hipotecario y Leasing Habitacional (Colombia)")

# Parámetros de entrada
st.sidebar.header("Parámetros del Simulador")
modo_simulador = st.sidebar.selectbox("Modo de Simulación", ("Crédito Hipotecario", "Leasing Habitacional"))
modo_diccionario = {"Crédito Hipotecario": "hipotecario", "Leasing Habitacional": "leasing"}
modo_simple = modo_diccionario.get(modo_simulador)

valor_inmueble = st.sidebar.number_input("Valor del Inmueble (Millones de COP)", min_value=150, value=570, step=5)*1e6
min_cuota = round(valor_inmueble*3e-7) if modo_simple == "hipotecario" else round(valor_inmueble*1e-7)
standard_cuota = 50 if 50>min_cuota else min_cuota
cuota_inicial = st.sidebar.number_input("Cuota Inicial (Millones de COP)", min_value=min_cuota, value=standard_cuota, step=5)*1e6
arriendo_referencia = round(st.sidebar.number_input("Arriendo de Referencia (Millones de COP)", min_value=0.8, value=3.5, step=0.1)*1e6)

max_year = 30 if modo_simple == "hipotecario" else 20
tasa_interes_anual = st.sidebar.slider("Tasa de Interés Anual (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.1)
plazo_anios = st.sidebar.slider("Plazo del Crédito (Años)", min_value=1, max_value=max_year, value=20)

# Opciones adicionales para leasing
tabla = pd.DataFrame()
if modo_simple == "leasing":
    opcion_compra = st.sidebar.slider("Opcion Compra (%)", min_value=0, max_value=20, value=20)
else:
    opcion_compra = 0

ipc_anual = st.sidebar.number_input("Porcentaje de crecimiento anual (IPC)", value=4.0, step=0.5) / 100

# Información en el sidebar
st.sidebar.markdown("## Dashboard por Kevin Henao 👤")
st.sidebar.markdown("[🔗 GitHub](https://github.com/niveku)")

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

# Gráfico de saldo restante
st.subheader("Gráfica de Saldo Restante")
st.line_chart(tabla[['Mes', 'Saldo Restante']].set_index('Mes'))

# Gráfico de división de pagos en Interés y Capital Amortizado
st.subheader("División de Pagos en Interés y Capital Amortizado con Cuota Mensual")
grafico_pagos = tabla[['Mes', 'Interés Pagado', 'Capital Amortizado', 'Cuota']].set_index('Mes')
st.line_chart(grafico_pagos)

# Arriendo de referencia y cálculo de "sentido"
mes_visto = st.slider(label="Mes #", min_value=0, max_value=plazo_meses, value=0)
arriendo_mensual = tabla['Arriendo'][mes_visto]
cuota_mensual = tabla['Cuota'][mes_visto]
abono_mensual = tabla['Capital Amortizado'][mes_visto]
interes_mensual = tabla['Interés Pagado'][mes_visto]
seguros_mensual = tabla['Seguros'][mes_visto]
sentido = tabla['Sentido'][mes_visto]

st.metric(label="Arriendo", value=f"{arriendo_mensual:,} COP")
st.metric(label="Cuota Mensual", value=f"{cuota_mensual:,} COP")
st.metric(label="Interés Pagado", value=f"{interes_mensual:,} COP")
st.metric(label="Capital Amortizado", value=f"{abono_mensual:,} COP")
st.metric(label="Seguros Pagado", value=f"{seguros_mensual:,} COP")

sentido_title = "Sentido"
if sentido < 0:
    st.metric(label=sentido_title, value=f"{sentido:,.1f}%", delta="-Terrible", delta_color="normal")
elif sentido < 20:
    st.metric(label=sentido_title, value=f"{sentido:,.1f}%", delta="-Malo", delta_color="normal")
elif sentido < 50:
    st.metric(label=sentido_title, value=f"{sentido:,.1f}%", delta="+Decente", delta_color="normal")
elif sentido < 80:
    st.metric(label=sentido_title, value=f"{sentido:,.1f}%", delta="+Bueno", delta_color="normal")
else:
    st.metric(label=sentido_title, value=f"{sentido:,.1f}%", delta="+Increible", delta_color="normal")

# --------------------- Ganancias ------------------
# Rango de cuota inicial
cuota_inicial_range = np.linspace(cuota_inicial, valor_inmueble, 100)

# Cálculo de la ganancia y retorno
ganancias = []
retornos_anuales = []

for c_inicial in cuota_inicial_range:
    monto_financiado = valor_inmueble - c_inicial
    if modo_simple == 'leasing':
        cuota = simulador_leasing(monto_financiado, tasa_mensual, plazo_meses, valor_residual)
    else:
        cuota = simulador_credito_hipotecario(monto_financiado, tasa_mensual, plazo_meses)

    ganancia = round(arriendo_referencia - (cuota + seguros))
    ganancias.append(ganancia)

    # Cálculo del retorno efectivo anual
    inversion_total = c_inicial
    retorno_anual = (ganancia * 12 / inversion_total) * 100
    retornos_anuales.append(retorno_anual)

# Gráfico interactivo de Ganancia vs. Cuota Inicial
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=cuota_inicial_range / 1e6,
    y=ganancias,
    mode="lines+markers",
    name="Ganancia Mensual (COP)",
    hovertemplate="%{y:,} COP"
))

fig1.add_trace(go.Scatter(
    x=cuota_inicial_range / 1e6,
    y=retornos_anuales,
    mode="lines+markers",
    name="Retorno E.A (%)",
    yaxis="y2",
    hovertemplate="%{y:.2f}%"
))

fig1.update_layout(
    title=f"Ganancia y Retorno E.A Inicial en función de la Cuota Inicial Y Arriendo",
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
# fig1.add_shape(type="line", x0=cuota_inicial_range[0] / 1e6, x1=cuota_inicial_range[-1] / 1e6, y0=0, y1=0,
#                line=dict(color="red", width=2, dash="dash"))

st.plotly_chart(fig1)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=tabla["Mes"],
    y=tabla["Ganancia"],
    mode="lines+markers",
    name="Ganancia Mensual en el Tiempo",
    hovertemplate="Mes: %{x}<br>Ganancia: %{y:,} COP"
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

# ------------- Gráfico de Sentido ----------------
# Genera los valores de rango para precio del inmueble y cuota inicial
precio_inmueble_range = np.arange(250_000_000, 750_000_000, 10_000_000)
cuota_inicial_range = np.arange(0, 250_000_000, 5_000_000)

# Lista para almacenar los resultados
equilibrio_cero = []

# Calcular el sentido para cada combinación de precio del inmueble y cuota inicial
for v_inmueble in precio_inmueble_range:
    equilibrio_linea = []
    for c_inicial in cuota_inicial_range:
        # Obtener el valor del equilibrio para el primer mes
        financiado = v_inmueble - c_inicial
        equilibrio = calcular_equilibrio_interes(financiado, tasa_mensual, seguros)

        equilibrio_linea.append(equilibrio)
    equilibrio_cero.append(equilibrio_linea)

# Convertir a numpy array y reemplazar cualquier NaN o Inf remanente
equilibrio_cero = np.nan_to_num(np.array(equilibrio_cero), nan=0, posinf=0, neginf=0)

# Crear gráfico de línea de contorno donde el "sentido" es 0
plt.figure(figsize=(10, 6))
cp = plt.contourf(cuota_inicial_range, precio_inmueble_range, equilibrio_cero, levels=20, cmap="RdYlGn")  # cmap para colores claros y oscuros
cbar = plt.colorbar(cp, label="Equilibrio")

# Agregar línea de contorno para sentido = 0
contour_zero = plt.contour(cuota_inicial_range, precio_inmueble_range, equilibrio_cero, levels=[0], colors='blue', linewidths=2, linestyles='dashed')
plt.clabel(contour_zero, inline=True, fontsize=8, fmt='Equilibrio = Arr - Int - Seg')

# Formatear ejes para mostrar valores en millones
plt.title("Línea de Equilibrio del Interés entre Cuota Inicial y Precio del Inmueble")
plt.xlabel("Cuota Inicial (COP)")
plt.ylabel("Precio del Inmueble (COP)")

# Aplicar formateo a los ejes
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_millions))
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_millions))

plt.grid(True)

# Mostrar el gráfico en Streamlit
st.pyplot(plt)

# Información de créditos al final de la página principal
st.markdown("---")  # Línea separadora
st.markdown("**Creado por [Kevin Henao](https://github.com/tu_usuario)**")
st.markdown("Desarrollado en Bogotá, Colombia 🇨🇴")
