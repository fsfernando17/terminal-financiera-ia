import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from google import genai
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA FINTECH ---
st.set_page_config(
    page_title="Asistente Inteligente de Inversiones Bursátiles",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
    }
    .stAppHeader {
        background-color: #0d1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #238636;
        color: #ffffff;
        font-weight: 600;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.3);
    }
    .disclaimer-box {
        background-color: #1f1a0f;
        border-left: 4px solid #d97706;
        color: #f3f4f6;
        padding: 14px;
        border-radius: 6px;
        font-size: 13px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Carga transparente de la API Key desde los secretos del servidor
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None


# LLAMADA ULTRA RÁPIDA EXCLUSIVA A MODELOS ACTIVOS EN TU PANEL DE GOOGLE AI STUDIO
def generar_respuesta_ia_rapida(client, prompt):
    """
    Utiliza exactamente los modelos habilitados en tu consola de Google AI Studio:
    gemini-3.8-flash -> gemini-3.7-flash -> gemini-3.6-flash
    Sin esperas ni retardos innecesarios.
    """
    modelos_activos = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]
    ultimo_error = None

    for modelo in modelos_activos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt
            )
            return response.text
        except Exception as e:
            ultimo_error = e
            continue  # Conmuta de inmediato sin pausas

    raise Exception(f"Detalle de conexión API: {str(ultimo_error)}")


# --- DICCIONARIOS MULTIMONEDA Y MERCADOS ---
TASAS_CAMBIO_APROX = {
    "USD ($)": {"factor": 1.0, "simbolo": "$", "min": 20.0},
    "PEN (S/.)": {"factor": 3.75, "simbolo": "S/.", "min": 75.0},
    "CLP ($)": {"factor": 950.0, "simbolo": "$ CLP", "min": 19000.0},
    "BRL (R$)": {"factor": 5.50, "simbolo": "R$", "min": 110.0},
    "MXN ($)": {"factor": 19.50, "simbolo": "$ MXN", "min": 390.0}
}

MERCADOS = {
    "NYSE / NASDAQ (Estados Unidos)": {
        "AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "MSFT": "Microsoft Corp.",
        "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com Inc.", "GOOGL": "Alphabet Inc.",
        "META": "Meta Platforms", "NFLX": "Netflix Inc.", "AMD": "Advanced Micro Devices",
        "INTC": "Intel Corp.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Bolsa de Valores de Lima (BVL - Perú)": {
        "BAP": "Credicorp Ltd.", "SCCO": "Southern Copper Corp.", "IFS": "Intercorp Financial Services",
        "BVN": "Compañía de Minas Buenaventura", "CPACEN1.LM": "Cementos Pacasmayo", "VOLCABC1.LM": "Volcan Compañía Minera",
        "ALICORC1.LM": "Alicorp S.A.A.", "FERREYC1.LM": "Ferreycorp S.A.A.",
        "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "B3 (Bolsa de Brasil)": {
        "PETR4.SA": "Petrobras", "VALE3.SA": "Vale S.A.", "ITUB4.SA": "Itaú Unibanco",
        "BBDC4.SA": "Banco Bradesco", "ABEV3.SA": "Ambev S.A.", "WEGE3.SA": "WEG S.A.",
        "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    }
}

# --- ENCABEZADO PRINCIPAL ---
st.title("📈 Asistente Inteligente de Inversiones Bursátiles")
st.markdown("Plataforma cuantitativa, fundamental y predictiva para el análisis estratégico de activos en mercados internacionales.")
st.markdown("---")

# --- PANEL DE CONFIGURACIÓN ---
st.subheader("⚙️ Parámetros del Análisis")

col1, col2, col3 = st.columns(3)

with col1:
    mercado_sel = st.selectbox("🌍 Mercado de Origen:", list(MERCADOS.keys()))

dic_acciones = MERCADOS[mercado_sel]

with col2:
    opcion_accion = st.selectbox(
        "📊 Selección de Acción:",
        list(dic_acciones.keys()),
        format_func=lambda x: f"{x} - {dic_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir código'}"
    )
    
    if opcion_accion == "🔍 Buscar otro Ticker manualmente":
        ticker_final = st.text_input("Ingrese Ticker de Yahoo Finance (ej: AMD, MELI, PBR):", value="NVDA").upper()
        nombre_empresa = ticker_final
    else:
        ticker_final = opcion_accion
        nombre_empresa = dic_acciones[opcion_accion]

with col3:
    moneda_sel = st.selectbox("💵 Moneda de Operación:", list(TASAS_CAMBIO_APROX.keys()))

conf_moneda = TASAS_CAMBIO_APROX[moneda_sel]

col4, col5, col6 = st.columns(3)

with col4:
    monto_min = conf_moneda["min"]
    capital_input = st.number_input(
        f"💰 Capital a Invertir ({conf_moneda['simbolo']}):",
        min_value=monto_min,
        value=monto_min * 10,
        step=monto_min
    )

with col5:
    horizonte = st.selectbox(
        "⏱️ Horizonte Temporal:",
        ["Corto Plazo (1 a 3 meses)", "Mediano Plazo (6 meses a 1 año)", "Largo Plazo (1 año a más)"]
    )

with col6:
    perfil_riesgo = st.selectbox("🛡️ Perfil del Inversor:", ["Conservador", "Moderado", "Agresivo"])

st.markdown("---")

# --- EJECUCIÓN DEL ANÁLISIS ---
if st.button("🚀 Ejecutar Análisis Multidimensional y Proyección", use_container_width=True):
    if not api_key_oculta or not client:
        st.error("⚠️ El servicio de Inteligencia Artificial no está configurado en el servidor (Falta GEMINI_API_KEY en Secrets).")
    else:
        with st.spinner(f"Procesando métricas financieras y conectando con IA para {ticker_final}..."):
            try:
                # Descarga de datos bursátiles
                stock = yf.Ticker(ticker_final)
                df = stock.history(period="1y")
                info = stock.info
                
                if df.empty:
                    st.error(f"⚠️ No se encontraron datos para el símbolo '{ticker_final}'. Verifique que el ticker sea válido.")
                else:
                    tasa = conf_moneda["factor"]
                    simb = conf_moneda["simbolo"]
                    
                    # Ajuste de precios a la divisa seleccionada
                    precio_actual_raw = df['Close'].iloc[-1]
                    precio_actual = precio_actual_raw * tasa
                    df['Close_Moneda'] = df['Close'] * tasa
                    
                    # Métricas Fundamentales
                    market_cap = info.get('marketCap', 0) * tasa if info.get('marketCap') else 0
                    pe_ratio = info.get('trailingPE', 'N/A')
                    pb_ratio = info.get('priceToBook', 'N/A')
                    dividend_yield = info.get('dividendYield', 0)
                    dividend_str = f"{dividend_yield*100:.2f}%" if dividend_yield else "0.00%"
                    profit_margin = info.get('profitMargins', 0)
                    margin_str = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                    sector = info.get('sector', 'General / No especificado')
                    
                    # Métricas Cuantitativas y Estadísticas
                    df['Retorno_Diario'] = df['Close'].pct_change()
                    volatilidad_anual = df['Retorno_Diario'].std() * np.sqrt(252)
                    retorno_medio_diario = df['Retorno_Diario'].mean()
                    var_95 = np.percentile(df['Retorno_Diario'].dropna(), 5)
                    
                    sma_50 = df['Close_Moneda'].rolling(window=50).mean().iloc[-1]
                    sma_200 = df['Close_Moneda'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else sma_50
                    
                    # PANEL DE MÉTRICAS VISUALES
                    st.markdown("### 📊 Indicadores Clave de Rendimiento y Fundamentos")
                    
                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric(f"Precio Actual ({simb})", f"{simb} {precio_actual:,.2f}")
                    c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
                    c_m3.metric("Volatilidad Anualizada", f"{volatilidad_anual:.2%}")
                    c_m4.metric("Margen de Beneficio", f"{margin_str}")
                    
                    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
                    c_m5.metric(f"Cap. de Mercado ({simb})", f"{simb} {market_cap:,.0f}" if market_cap else "N/A")
                    c_m6.metric("Ratio P/B", f"{pb_ratio}")
                    c_m7.metric("Rendimiento por Dividendo", f"{dividend_str}")
                    c_m8.metric("VaR 95% (Pérdida Máx. Diaria)", f"{var_95:.2%}")

                    st.markdown("---")

                    # GRÁFICO INTERACTIVO PLOTLY
                    st.markdown(f"### 📈 Comportamiento Histórico y Proyección a {horizonte}")
                    
                    if "1 a 3 meses" in horizonte:
                        dias_proy = 60
                    elif "6 meses a 1 año" in horizonte:
                        dias_proy = 180
                    else:
                        dias_proy = 365

                    # Simulación econométrica estocástica
                    np.random.seed(42)
                    cambios_simulados = np.random.normal(retorno_medio_diario, df['Retorno_Diario'].std(), dias_proy)
                    precios_futuros = [precio_actual]
                    for cambio in cambios_simulados:
                        precios_futuros.append(precios_futuros[-1] * (1 + cambio))
                        
                    fechas_hist = df.index[-90:]
                    precios_hist = df['Close_Moneda'].tail(90)
                    fechas_futuras = pd.date_range(start=df.index[-1], periods=dias_proy + 1, freq='B')

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=fechas_hist, y=precios_hist,
                        mode='lines', name='Histórico Reciente',
                        line=dict(color='#29b6f6', width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=fechas_futuras, y=precios_futuros,
                        mode='lines', name='Proyección Econométrica',
                        line=dict(color='#ab47bc', width=2, dash='dash')
                    ))

                    fig.update_layout(
                        title=f"Evolución del Precio y Pronóstico Estimado - {ticker_final}",
                        xaxis_title="Fecha / Periodo de Proyección",
                        yaxis_title=f"Precio del Activo ({simb})",
                        template="plotly_dark",
                        height=480,
                        hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # DISCLAIMER LEGAL
                    st.markdown("""
                        <div class="disclaimer-box">
                            <strong>⚠️ Aviso Legal / Descargo de Responsabilidad:</strong> 
                            Este modelo genera pronósticos estadísticos basándose estrictamente en datos pasados y condiciones actuales de mercado. 
                            No es 100% exacto y está expuesto a la volatilidad implícita, eventos macroeconómicos imprevistos y riesgos sistémicos. 
                            Las proyecciones no constituyen una garantía de rendimiento ni una recomendación directa de compra o venta.
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

                    # PROMPT EJECUTIVO Y RESUMIDO PARA MÁXIMA VELOCIDAD
                    paquete_analisis = f"""
                    Activo: {ticker_final} ({nombre_empresa}) | Sector: {sector}
                    Precio Actual: {simb} {precio_actual:,.2f}
                    Capital disponible del inversor: {simb} {capital_input:,.2f}
                    Moneda seleccionada: {moneda_sel}
