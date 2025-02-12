# Simulador de Inversión Habitacional

Este proyecto es una herramienta interactiva de simulación para evaluar la viabilidad financiera de invertir en un inmueble frente a pagar arriendo. Utilizando **Streamlit**, **Matplotlib** y **Plotly**, la aplicación calcula indicadores financieros y genera gráficos para ayudar a tomar decisiones de inversión en bienes raíces.

## Funcionalidades

- **Simulación de Leasing o Crédito Hipotecario**: Compara diferentes opciones de financiamiento con base en una cuota inicial, tasa de interés y plazo de pago.
- **Gráficos Interactivos**: Visualiza la ganancia mensual en función de la cuota inicial, evolución de pagos a lo largo del tiempo, y el "sentido" de la inversión con una métrica que evalúa el beneficio de comprar vs. arrendar.
- **Ajuste por IPC Anual**: Simula el crecimiento del valor de arriendo de referencia usando un índice de inflación (IPC) anual.
- **Análisis de Métrica de "Sentido"**: Indica cuándo es más rentable invertir en una propiedad comparado con alquilar.

## Instalación

1. Clona este repositorio:

    ```bash
    git clone https://github.com/tuusuario/simulador_inmobiliario.git
    cd simulador_inmobiliario
    ```

2. Instala las dependencias usando el archivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

3. Ejecuta la aplicación con el siguiente comando:

    ```bash
    streamlit run simulador.py
    ```

## Uso

1. **Configuración de Parámetros**: Utiliza la barra lateral para ingresar:
    - Valor del inmueble
    - Cuota inicial
    - Valor de referencia del arriendo
    - Tasa de interés
    - Plazo en meses
    - IPC anual (para el ajuste del arriendo)

2. **Visualización de Resultados**:
    - Gráficos de ganancia y sentido en función de la cuota inicial.
    - Evolución de pagos y ahorro en el tiempo.
    - Métrica de "Sentido", que evalúa el momento ideal para preferir la compra vs. arriendo.

## Requisitos

- **Python 3.8+**
- Librerías necesarias (ver `requirements.txt`):
  - Streamlit
  - Matplotlib
  - Numpy
  - Pandas
  - Plotly

## Ejemplo de Código

```python
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Ejemplo de cálculo simple de ganancia
def calcular_ganancia(cuota_inicial, tasa_mensual, plazo_meses, valor_inmueble):
    # Tu código de cálculo aquí
    pass

# Gráfico de ganancia en función de cuota inicial
plt.plot(...)
st.pyplot(plt)
