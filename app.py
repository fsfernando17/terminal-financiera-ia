import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from google import genai
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA FINTECH PROFESIONAL ---
st.set_page_config(
    page_title="Asistente Inteligente de Inversiones Bursátiles",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados con Alta Legibilidad y Contraste
st.markdown("""
    <style>
    /* Estilo General Dark Mode */
    .stApp {
        background-color: #0b0f17;
        color: #e5e7eb;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* CORRECCIÓN DE CONTRASTE: Forzar color blanco/brillante en todas las etiquetas de entrada */
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stWidgetLabel p {
        color: #f3f4f6 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Estilo de cajas de selección e inputs */
    div[data-baseweb="select"] > div, input {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-color: #374151 !important;
        border-radius: 8px !important;
    }

    /* Tarjeta para Veredicto Final de IA */
    .dictamen-card {
        background-color: #111827;
        border-left: 5px solid #10b981;
        border: 1px solid #1f2937;
        border-left-width: 5px;
        border-radius: 10px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }

    /* Títulos y Subtítulos */
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
    }
    h2, h3 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* Métricas KPI */
    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.88rem !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.45rem !important;
        font-weight: 700;
    }

    /* Botón de Ejecución Principal */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 17px;
        border-radius: 10px;
        border: none;
        padding: 14px 28px;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }

    /* Cajas de Aviso Legal */
    .disclaimer-box {
        background-color: #17120a;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        color: #f3f4f6;
        padding: 16px 20px;
        font-size: 0.88rem;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Carga transparente de la API Key desde los secretos del servidor
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None


# CONEXIÓN DIRECTA A MODELOS ACTIVOS DE GOOGLE AI STUDIO
def generar_respuesta_ia_rapida(client, prompt):
    """
    Utiliza estrictamente los modelos habilitados en la consola de Google AI Studio:
    gemini-3.8-flash -> gemini-3.7-flash -> gemini-3.6-flash
    """
    modelos_validos = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]
    
    for modelo in modelos_validos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception:
            continue
            
    raise Exception("No se pudo obtener respuesta de la API de Gemini. Verifique la clave GEMINI_API_KEY en los secretos.")


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
st.markdown("<p style='color: #9ca3af; font-size: 1.05rem; margin-bottom: 25px;'>Terminal cuantitativa, fundamental y econométrica para la evaluación estratégica de activos financieros globales.</p>", unsafe_allow_html=True)

# --- PANEL DE CONFIGURACIÓN LIMPIO (SIN BARRAS HUÉRFANAS) ---
with st.container(border=True):
    st.subheader("⚙️ Parámetros Operativos de Inversión")

    col1, col2, col3 = st.columns(3)

    with col1:
        mercado_sel = st.selectbox("🌍 Mercado de Origen:", list(MERCADOS.keys()))

    dic_acciones = MERCADOS[mercado_sel]

    with col2:
        opcion_accion = st.selectbox(
            "📊 Selección de Acción / Ticker:",
            list(dic_acciones.keys()),
            format_func=lambda x: f"{x} - {dic_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir Ticker'}"
        )
        
        if opcion_accion == "🔍 Buscar otro Ticker manualmente":
            ticker_final = st.text_input("Ingrese Ticker oficial de Yahoo Finance (ej: AMD, MELI, PBR):", value="NVDA").upper()
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
            f"💰 Capital Disponible ({conf_moneda['simbolo']}):",
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

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

# --- BOTÓN PRINCIPAL DE EJECUCIÓN ---
if st.button("🚀 Ejecutar Análisis Multidimensional y Proyección", use_container_width=True):
    if not api_key_oculta or not client:
        st.error("⚠️ El servicio de Inteligencia Artificial no está configurado en el servidor (Falta la clave GEMINI_API_KEY en Secrets).")
    else:
        with st.spinner(f"Procesando métricas cuantitativas, econométricas y de riesgo para {ticker_final}..."):
            try:
                # Descarga de datos
                stock = yf.Ticker(ticker_final)
                df = stock.history(period="1y")
                info = stock.info
                
                if df.empty:
                    st.error(f"⚠️ No se encontraron registros financieros para el símbolo '{ticker_final}'. Verifique el ticker en Yahoo Finance.")
                else:
                    tasa = conf_moneda["factor"]
                    simb = conf_moneda["simbolo"]
                    
                    # Precios convertidos a la divisa seleccionada
                    precio_actual_raw = df['Close'].iloc[-1]
                    precio_actual = precio_actual_raw * tasa
                    df['Close_Moneda'] = df['Close'] * tasa
                    
                    # Fundamental Data
                    market_cap = info.get('marketCap', 0) * tasa if info.get('marketCap') else 0
                    pe_ratio_raw = info.get('trailingPE', 'N/A')
                    pe_ratio = f"{pe_ratio_raw:.2f}" if isinstance(pe_ratio_raw, (int, float)) else str(pe_ratio_raw)
                    
                    pb_ratio_raw = info.get('priceToBook', 'N/A')
                    pb_ratio = f"{pb_ratio_raw:.2f}" if isinstance(pb_ratio_raw, (int, float)) else str(pb_ratio_raw)
                    
                    dividend_yield = info.get('dividendYield', 0)
                    dividend_str = f"{dividend_yield*100:.2f}%" if dividend_yield else "0.00%"
                    profit_margin = info.get('profitMargins', 0)
                    margin_str = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                    sector = info.get('sector', 'General / No especificado')
                    
                    # Econometric & Quantitative Calculations
                    df['Retorno_Diario'] = df['Close'].pct_change()
                    volatilidad_anual = df['Retorno_Diario'].std() * np.sqrt(252)
                    retorno_medio_diario = df['Retorno_Diario'].mean()
                    var_95 = np.percentile(df['Retorno_Diario'].dropna(), 5)
                    
                    sma_50 = df['Close_Moneda'].rolling(window=50).mean().iloc[-1]
                    sma_200 = df['Close_Moneda'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else sma_50
                    
                    # --- PANEL EJECUTIVO DE INDICADORES (KPIS) ---
                    st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos")
                    
                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric(f"Precio Actual ({simb})", f"{simb} {precio_actual:,.2f}")
                    c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
                    c_m3.metric("Volatilidad Anualizada", f"{volatilidad_anual:.2%}")
                    c_m4.metric("Margen Beneficio Neto", f"{margin_str}")
                    
                    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
                    c_m5.metric(f"Cap. de Mercado ({simb})", f"{simb} {market_cap:,.0f}" if market_cap else "N/A")
                    c_m6.metric("Ratio P/B", f"{pb_ratio}")
                    c_m7.metric("Rendimiento Dividendo", f"{dividend_str}")
                    c_m8.metric("VaR 95% (Pérdida Máx. Diaria)", f"{var_95:.2%}")

                    st.markdown("---")

                    # --- GRÁFICO PLOTLY BURSÁTIL ---
                    st.markdown(f"### 📈 Comportamiento Histórico & Proyección Econométrica ({horizonte})")
                    
                    if "1 a 3 meses" in horizonte:
                        dias_proy = 60
                    elif "6 meses a 1 año" in horizonte:
                        dias_proy = 180
                    else:
                        dias_proy = 365

                    # Simulación Estocástica
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
                        mode='lines', name='Histórico Reciente (Real)',
                        line=dict(color='#00e676', width=2.5)
                    ))

                    fig.add_trace(go.Scatter(
                        x=fechas_futuras, y=precios_futuros,
                        mode='lines', name='Proyección Econométrica',
                        line=dict(color='#e040fb', width=2.5, dash='dash')
                    ))

                    fig.update_layout(
                        title=dict(text=f"Trayectoria de Cotización Estimada - {ticker_final}", font=dict(size=16, color='#f9fafb')),
                        xaxis=dict(title="Fecha / Periodo de Proyección", gridcolor='#1f2937'),
                        yaxis=dict(title=f"Precio del Activo ({simb})", gridcolor='#1f2937'),
                        template="plotly_dark",
                        paper_bgcolor="#111827",
                        plot_bgcolor="#111827",
                        height=480,
                        hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(17,24,39,0.8)")
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # --- AVISO LEGAL ---
                    st.markdown("""
                        <div class="disclaimer-box">
                            <strong>⚠️ Aviso Legal / Descargo de Responsabilidad:</strong> 
                            Este modelo genera pronósticos estadísticos basándose estrictamente en datos pasados y condiciones actuales de mercado. 
                            No es 100% exacto y está expuesto a la volatilidad implícita, eventos macroeconómicos imprevistos y riesgos sistémicos. 
                            Las proyecciones no constituyen una garantía de rendimiento ni una recomendación directa de compra o venta.
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

                    # --- PROMPT DIRECTO Y ESTRUCTURADO PARA IA ---
                    paquete_analisis = f"""
                    Activo: {ticker_final} ({nombre_empresa}) | Sector: {sector}
                    Precio Actual: {simb} {precio_actual:,.2f}
                    Capital disponible: {simb} {capital_input:,.2f}
                    Moneda: {moneda_sel} | Horizonte: {horizonte} | Perfil: {perfil_riesgo}
                    
                    FUNDAMENTALES:
                    - Ratio P/E (PER): {pe_ratio} | Ratio P/B: {pb_ratio}
                    - Dividend Yield: {dividend_str} | Margen Beneficio: {margin_str}
                    
                    CUANTITATIVOS & RIESGO:
                    - Volatilidad Anualizada: {volatilidad_anual:.2%}
                    - Value at Risk (VaR 95%): {var_95:.2%}
                    - Media Móvil 50d: {simb} {sma_50:,.2f} | Media Móvil 200d: {simb} {sma_200:,.2f}
                    """

                    prompt_ia = f"""
                    Actúa como un Director de Análisis Cuantitativo y Gestor de Inversiones Senior.
                    Proporciona un informe estratégico bien formateado con las siguientes secciones en Markdown:

                    {paquete_analisis}

                    ESTRUCTURA OBLIGATORIA:
                    ### 1. Diagnóstico Fundamental y Técnico
                    (Breve evaluación de la valoración y posición de medias móviles).

                    ### 2. Viabilidad del Capital y Horizonte
                    (Analiza si el capital de {simb} {capital_input:,.2f} es suficiente y adecuado para la estrategia en {horizonte}).

                    ### 3. Factores de Riesgo Macro
                    (Tres puntos clave a vigilar).

                    ### 4. Veredicto Estratégico
                    - **Recomendación:** [COMPRAR / DESESTIMAR / MANTENER EN OBSERVACIÓN]
                    - **Fundamento:** Breve justificación ejecutiva.
                    """

                    # Generación inmediata
                    informe_ia = generar_respuesta_ia_rapida(client, prompt_ia)

                    # --- TARJETA VISUAL PARA EL DICTAMEN FINAL ---
                    st.markdown("<div class='dictamen-card'>", unsafe_allow_html=True)
                    st.markdown("## 📋 Dictamen Estratégico del Asistente")
                    st.markdown(informe_ia)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error al procesar el análisis financiero: {str(e)}")
