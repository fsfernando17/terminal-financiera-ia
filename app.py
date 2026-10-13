import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from google import genai
from google.genai import types

# Configuración de la página
st.set_page_config(
    page_title="Terminal Cuantitativa & Fundamental",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales modernos
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #238636;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 12px;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    </style>
""", unsafe_allow_html=True)

# Carga de la API Key desde los secretos del servidor de forma transparente
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None

st.title("⚡ Terminal Financiera Híbrida: Cuantitativa, Fundamental & IA")
st.markdown("Análisis bursátil avanzado integrando datos macro, estados financieros, econometría y proyección visual de precios.")
st.markdown("---")

# --- MENÚ DE SELECCIÓN ---
st.subheader("🌐 Configuración del Activo")
col1, col2, col3 = st.columns(3)

with col1:
    mercado = st.selectbox("🌍 Seleccione Mercado:", ["NYSE / NASDAQ (EE.UU.)", "Bolsa de Valores de Lima (BVL - Perú)", "B3 (Brasil)"])

# Listados de acciones por mercado
if "EE.UU." in mercado:
    acciones = {"AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "MSFT": "Microsoft Corp.", "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com"}
elif "Perú" in mercado:
    acciones = {"BAP": "Credicorp Ltd.", "SCCO": "Southern Copper Corp.", "IFS": "Intercorp Financial Services"}
else:
    acciones = {"PETR4.SA": "Petrobras", "VALE3.SA": "Vale S.A.", "ITUB4.SA": "Itaú Unibanco"}

with col2:
    ticker = st.selectbox("📊 Seleccione la Acción:", list(acciones.keys()), format_func=lambda x: f"{x} - {acciones[x]}")

with col3:
    horizonte = st.selectbox("⏱️ Horizonte de Inversión:", ["Corto Plazo (15 días)", "Mediano Plazo (3 meses)", "Largo Plazo (1 año)"])

col_m1, col_m2 = st.columns(2)
with col_m1:
    capital = st.number_input("💰 Capital a Simular ($ USD):", min_value=50.0, value=2000.0, step=100.0)
with col_m2:
    perfil = st.selectbox("🛡️ Perfil de Riesgo:", ["Conservador", "Moderado", "Agresivo"])

st.markdown("---")

if st.button("🚀 Ejecutar Análisis Financiero Integral y Proyección"):
    if not api_key_oculta or not client:
        st.error("⚠️ Error de configuración en el servidor. Falta la API Key de Gemini.")
    else:
        with st.spinner(f"Recopilando datos fundamentales, técnicos y ejecutando modelos econométricos para {ticker}..."):
            try:
                # Extracción de datos con yfinance (Tanto históricos como fundamentales .info)
                stock = yf.Ticker(ticker)
                df = stock.history(period="1y")
                info = stock.info
                
                if df.empty:
                    st.error("⚠️ No se encontraron registros de precios para este activo.")
                else:
                    precio_actual = df['Close'].iloc[-1]
                    
                    # --- DATOS FUNDAMENTALES ---
                    market_cap = info.get('marketCap', 0)
                    pe_ratio = info.get('trailingPE', 'N/A')
                    pb_ratio = info.get('priceToBook', 'N/A')
                    dividend_yield = info.get('dividendYield', 0)
                    dividend_str = f"{dividend_yield*100:.2f}%" if dividend_yield else "0.00% / No registra"
                    profit_margin = info.get('profitMargins', 0)
                    margin_str = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                    sector = info.get('sector', 'N/A')
                    
                    # --- MODELOS ESTADÍSTICOS Y ECONOMÉTRICOS ---
                    df['Retorno_Diario'] = df['Close'].pct_change()
                    volatilidad_anual = df['Retorno_Diario'].std() * np.sqrt(252)
                    retorno_medio_diario = df['Retorno_Diario'].mean()
                    var_95 = np.percentile(df['Retorno_Diario'].dropna(), 5)
                    
                    sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
                    sma_200 = df['Close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else sma_50
                    
                    # --- VISUALIZACIÓN DE MÉTRICAS CLAVE ---
                    st.markdown("### 📊 Panel Estadístico y Fundamental")
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Precio Actual", f"${precio_actual:.2f}")
                    m2.metric("PER (Price/Earnings)", f"{pe_ratio}")
                    m3.metric("Volatilidad Anual (Riesgo)", f"{volatilidad_anual:.2%}")
                    m4.metric("Margen de Beneficio", f"{margin_str}")
                    
                    m5, m6, m7, m8 = st.columns(4)
                    m5.metric("Capitalización de Mercado", f"${market_cap:,.0f}" if market_cap else "N/A")
                    m6.metric("Ratio P/B", f"{pb_ratio}")
                    m7.metric("Dividend Yield", f"{dividend_str}")
                    m8.metric("VaR 95% Diario", f"{var_95:.2%}")

                    st.markdown("---")

                    # --- GENERACIÓN DE GRÁFICO DE PROYECCIÓN (Simulación de Tendencia) ---
                    st.markdown(f"### 📈 Gráfico de Tendencia Histórica y Proyección a {horizonte}")
                    
                    # Definir número de días a proyectar según el horizonte
                    if "15 días" in horizonte:
                        dias_proyeccion = 15
                    elif "3 meses" in horizonte:
                        dias_proyeccion = 90
                    else:
                        dias_proyeccion = 252
                        
                    # Modelo determinista/estocástico simple basado en retorno medio y volatilidad para la proyección
                    ultimos_precios = df['Close'].tail(60) # Últimos 60 días reales
                    
                    # Crear simulación de precios futuros para graficar
                    np.random.seed(42)
                    cambios_simulados = np.random.normal(retorno_medio_diario, df['Retorno_Diario'].std(), dias_proyeccion)
                    precios_futuros = [precio_actual]
                    for cambio in cambios_simulados:
                        precios_futuros.append(precios_futuros[-1] * (1 + cambio))
                        
                    # Armar DataFrame para el gráfico de Streamlit
                    fechas_futuras = pd.date_range(start=df.index[-1], periods=dias_proyeccion + 1, freq='B')
                    df_proyeccion = pd.DataFrame({'Precio Proyectado ($)': precios_futuros}, index=fechas_futuras)
                    
                    # Mostrar gráfico combinando histórico reciente y proyección
                    st.line_chart(pd.concat([df['Close'].tail(30), df_proyeccion['Precio Proyectado ($)']]))
                    
                    # --- DISCLAIMER LEGAL OBLIGATORIO DEBAJO DEL GRÁFICO ---
                    st.warning("⚠️ **Aviso Legal / Disclaimer:** El modelo pronostica tendencias estadísticas basándose estrictamente en datos históricos y actuales. No es 100% exacto, está sujeto a la volatilidad, cisnes negros y riesgos inherentes del mercado financiero. Toda decisión de inversión es responsabilidad exclusiva del usuario.")

                    st.markdown("---")

                    # --- PAQUETE DE DATOS PARA LA INTELIGENCIA ARTIFICIAL ---
                    paquete_analisis = f"""
                    Activo: {ticker} ({acciones[ticker]}) | Sector: {sector}
                    Precio Actual: ${precio_actual:.2f}
                    Capital del Inversor: ${capital}
                    Horizonte seleccionado: {horizonte}
                    Perfil de Riesgo: {perfil}
                    
                    --- DATOS FUNDAMENTALES (Yahoo Finance) ---
                    - Capitalización Bursátil: ${market_cap:,.0f}
                    - Ratio P/E (PER): {pe_ratio}
                    - Ratio P/B: {pb_ratio}
                    - Dividend Yield: {dividend_str}
                    - Margen de Beneficio Neto: {margin_str}
                    
                    --- DATOS TÉCNICOS Y ESTADÍSTICOS ---
                    - Volatilidad Anualizada: {volatilidad_anual:.2%}
                    - Value at Risk (VaR 95% diario): {var_95:.2%}
                    - Media Móvil 50 ruedas: ${sma_50:.2f}
                    - Media Móvil 200 ruedas: ${sma_200:.2f}
                    """

                    prompt_ia = f"""
                    Actúa como un Director de Inversiones, Analista Fundamental y Quant Senior.
                    Evalúa exhaustivamente la siguiente información financiera y estadística del activo:

                    {paquete_analisis}

                    INSTRUCCIONES DE RESPUESTA:
                    1. **Análisis Fundamental:** Evalúa si la acción está sobrevalorada o infravalorada basándote en su PER, P/B y márgenes de beneficio.
                    2. **Análisis Técnico y Estadístico:** Interpreta la volatilidad, el VaR y las medias móviles para definir el momentum de mercado.
                    3. **Razonamiento Predictivo y Rentabilidad del Capital:** Evalúa si el monto de ${capital} es eficiente para los costos de transacción y el horizonte seleccionado.
                    4. **Conclusión y Recomendación:** Da un veredicto ejecutivo claro (estrategia operativa, riesgos macroeconómicos y niveles de prudencia).
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_ia
                    )

                    st.markdown("### 📋 Informe Ejecutivo de la IA & Analista Financiero")
                    st.markdown(response.text)
                    
                    st.markdown("---")
                    st.caption("Aviso legal: Esta herramienta combina modelos matemáticos y análisis de IA con fines educativos. No constituye asesoría financiera formal.")

            except Exception as e:
                st.error(f"Error procesando los datos financieros: {str(e)}")