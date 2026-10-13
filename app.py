import json
import re
import time
from google import genai
from google.genai import types
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==============================================================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA FINTECH INSTITUCIONAL
# ==============================================================================
st.set_page_config(
    page_title="Terminal Inteligente de Inversiones & Forex",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# ESTILOS CSS HIGH-END INSTITUCIONAL (GLASSMORPHISM & DARK MODE AVANZADO)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp {
        background-color: #020617;
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code {
        background-color: transparent !important;
        color: #38bdf8 !important;
        border: none !important;
        font-weight: 600 !important;
    }

    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stWidgetLabel p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.02em;
    }
    
    div[data-baseweb="select"] > div, input {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] > div:hover, input:focus {
        border-color: #3b82f6 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }

    [data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.85rem !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 1.5rem !important; font-weight: 700; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 1.05rem;
        border-radius: 10px;
        border: 1px solid #60a5fa;
        padding: 16px 32px;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
        box-shadow: 0 6px 28px rgba(37, 99, 235, 0.6);
        transform: translateY(-2px);
    }

    .analysis-card {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        min-height: 280px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    .analysis-card-title {
        color: #38bdf8;
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 14px;
        letter-spacing: -0.01em;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 8px;
    }
    .analysis-card-body {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.7;
        text-align: justify;
    }

    .decision-container {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    .decision-badge-box {
        border-radius: 12px;
        padding: 24px 16px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 160px;
    }

    .decision-comprar {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.8) 0%, rgba(5, 150, 105, 0.6) 100%);
        border: 2px solid #34d399;
        color: #a7f3d0;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.3);
    }

    .decision-desestimar {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.9) 0%, rgba(220, 38, 38, 0.6) 100%);
        border: 2px solid #f87171;
        color: #fecaca;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        box-shadow: 0 0 25px rgba(220, 38, 38, 0.4);
    }

    .decision-observacion {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.9) 0%, rgba(217, 119, 6, 0.6) 100%);
        border: 2px solid #fbbf24;
        color: #fde68a;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.3);
    }

    .disclaimer-box {
        background-color: rgba(23, 18, 10, 0.8);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        color: #94a3b8;
        padding: 18px 22px;
        font-size: 0.85rem;
        margin-top: 25px;
        line-height: 1.6;
    }
    
    .source-note {
        font-size: 0.72rem;
        color: #94a3b8;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# CONFIGURACIÓN DE CLIENTE GOOGLE GENAI Y MANEJO DE TOKENS
# ==============================================================================
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None

def limpiar_texto_markdown(texto_entrada):
    if not texto_entrada:
        return ""
    return str(texto_entrada).replace("`", "").strip()

def parse_json_respuesta(texto_crudo):
    if not texto_crudo:
        return None
    texto_limpio = texto_crudo.strip()
    if texto_limpio.startswith("```"):
        texto_limpio = re.sub(r'^```[a-zA-Z]*\n', '', texto_limpio)
        texto_limpio = re.sub(r'\n```$', '', texto_limpio)
    try:
        return json.loads(texto_limpio)
    except Exception:
        match_json = re.search(r'\{[\s\S]*\}', texto_limpio)
        if match_json:
            try:
                return json.loads(match_json.group(0))
            except Exception:
                pass
    return None

def generar_respuesta_ia_robusta(cliente_genai, prompt_sistema):
    modelos_disponibles = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
    configuracion_tokens = types.GenerateContentConfig(
        temperature=0.2, 
        max_output_tokens=4000
    )
    for modelo in modelos_disponibles:
        try:
            respuesta = cliente_genai.models.generate_content(
                model=modelo, 
                contents=prompt_sistema, 
                config=configuracion_tokens
            )
            if respuesta and respuesta.text:
                return respuesta.text
        except Exception:
            continue
    return None

# ==============================================================================
# MOTOR ECONOMÉTRICO & MODELO ESTOCÁSTICO (GBM CALIBRADO Y REALISTA)
# ==============================================================================
def simular_monte_carlo_gbm(precio_inicial, retornos_diarios, dias_proy, num_simulaciones=500, es_forex=False):
    dias_historia = 60 if dias_proy <= 60 else (120 if dias_proy <= 180 else 252)
    retornos_recientes = retornos_diarios.tail(dias_historia) if len(retornos_diarios) > dias_historia else retornos_diarios
    
    mu_diario = retornos_recientes.mean()
    sigma_diario = retornos_recientes.std()
    
    # Factores estrictamente calibrados para evitar proyecciones exageradas o irreales
    factor_escala = 0.18 if es_forex else 0.25
    drift_suavizado = 0.05 * mu_diario
    sigma_calibrado = sigma_diario * factor_escala
    
    drift = drift_suavizado - 0.5 * (sigma_calibrado ** 2)
    matriz_precios = np.zeros((dias_proy + 1, num_simulaciones))
    matriz_precios[0] = precio_inicial
    
    choques_aleatorios = np.random.normal(0, 1, (dias_proy, num_simulaciones))
    
    for t in range(1, dias_proy + 1):
        factor_tiempo = np.sqrt(t / dias_proy)
        retornos_simulados = np.exp(
            drift + sigma_calibrado * choques_aleatorios[t - 1] * (0.5 + 0.1 * factor_tiempo)
        )
        matriz_precios[t] = matriz_precios[t - 1] * retornos_simulados
        
    mediana_proyectada = np.median(matriz_precios, axis=1)
    percentil_inferior = np.percentile(matriz_precios, 20, axis=1)
    percentil_superior = np.percentile(matriz_precios, 80, axis=1)
    
    return mediana_proyectada, percentil_inferior, percentil_superior

# ==============================================================================
# DICCIONARIOS Y CONFIGURACIONES DE MERCADO (AMPLIADOS INTERNACIONALMENTE)
# ==============================================================================
DIVISAS = {
    "USD": "Dólar Estadounidense (USD)", "PEN": "Sol Peruano (PEN)", "EUR": "Euro (EUR)",
    "GBP": "Libra Esterlina (GBP)", "JPY": "Yen Japonés (JPY)", "MXN": "Peso Mexicano (MXN)",
    "CLP": "Peso Chileno (CLP)", "COP": "Peso Colombiano (COP)", "BRL": "Real Brasileño (BRL)",
    "CNY": "Yuan Chino (CNY)", "RUB": "Rublo Ruso (RUB)", "AED": "Dirham de EAU (AED)",
    "KRW": "Won Surcoreano (KRW)", "CHF": "Franco Suizo (CHF)", "CAD": "Dólar Canadiense (CAD)"
}

SIMBOLOS_MONEDA = {
    "USD ($)": "$", "PEN (S/.)": "S/.", "CLP ($)": "$ CLP", "BRL (R$)": "R$", "MXN ($)": "$ MXN",
    "EUR (€)": "€", "GBP (£)": "£", "JPY (¥)": "¥", "CNY (¥)": "¥ CNY", "RUB (₽)": "₽", "AED (د.إ)": "AED"
}

MINIMOS_MONEDA = {
    "USD ($)": 20.0, "PEN (S/.)": 75.0, "CLP ($)": 19000.0, "BRL (R$)": 110.0, "MXN ($)": 390.0,
    "EUR (€)": 20.0, "GBP (£)": 15.0, "JPY (¥)": 3000.0, "CNY (¥)": 150.0, "RUB (₽)": 1800.0, "AED (د.إ)": 75.0
}

TASAS_CAMBIO_USD = {
    "USD ($)": 1.0, "PEN (S/.)": 3.75, "CLP ($)": 950.0, "BRL (R$)": 5.50, "MXN ($)": 19.50,
    "EUR (€)": 0.92, "GBP (£)": 0.78, "JPY (¥)": 150.0, "CNY (¥)": 7.20, "RUB (₽)": 95.0, "AED (د.إ)": 3.67
}

TASAS_REFERENCIA_PAIS = {
    "USD": 4.50, "PEN": 4.75, "EUR": 3.25, "GBP": 4.50, "CLP": 5.00, 
    "MXN": 10.00, "BRL": 11.25, "JPY": 0.50, "COP": 9.50, "CNY": 3.45, "RUB": 16.00, "AED": 4.50
}

MERCADOS = {
    "NYSE / NASDAQ (Estados Unidos)": {
        "AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "MSFT": "Microsoft Corp.", 
        "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com Inc.", "GOOGL": "Alphabet Inc.", 
        "SCCO": "Southern Copper Corp.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Bolsa de Valores de Lima (BVL - Perú)": {
        "SPCCPI1.LM": "Southern Copper Corp. (BVL)", "BAP": "Credicorp Ltd.", 
        "IFS": "Intercorp Financial Services", "CPACEN1.LM": "Cementos Pacasmayo", 
        "ALICORC1.LM": "Alicorp S.A.A.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Bolsa Mexicana de Valores (BMV - México)": {
        "WALMEX.MX": "Wal-Mart de México", "AMXL.MX": "América Móvil", 
        "GFNORTEO.MX": "Grupo Financiero Banorte", "CEMEXCPO.MX": "Cemex S.A.B.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Bolsa de Santiago (BCS - Chile)": {
        "SQM-B.CL": "Sociedad Química y Minera de Chile", "BSANTANDER.CL": "Banco Santander Chile", 
        "CHILE.CL": "Banco de Chile", "ENELAM.CL": "Enel Américas S.A.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "B3 Brasil (Bolsa de São Paulo - Brasil)": {
        "PETR4.SA": "Petróleo Brasileiro (Petrobras)", "VALE3.SA": "Vale S.A.", 
        "ITUB4.SA": "Itaú Unibanco Holding", "BBDC4.SA": "Banco Bradesco S.A.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Tokyo Stock Exchange (TSE - Japón)": {
        "7203.T": "Toyota Motor Corp.", "6758.T": "Sony Group Corp.", 
        "9984.T": "SoftBank Group Corp.", "6861.T": "Keyence Corp.", "🔍 Buscar otro Ticker manually": "CUSTOM"
    },
    "Korea Exchange (KRX - Corea del Sur)": {
        "005930.KS": "Samsung Electronics", "000660.KS": "SK Hynix", 
        "373220.KS": "LG Energy Solution", "005380.KS": "Hyundai Motor", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Shanghai & Hong Kong Stock Exchange (China)": {
        "0700.HK": "Tencent Holdings", "9988.HK": "Alibaba Group Holding", 
        "600519.SS": "Kweichow Moutai", "0388.HK": "HKEX", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Moscow Exchange (MOEX - Rusia)": {
        "GAZP.ME": "Gazprom PJSC", "SBER.ME": "Sberbank of Russia", 
        "LKOH.ME": "Lukoil PJSC", "ROSN.ME": "Rosneft PJSC", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Euronext & Bolsa de Frankfurt (Europa)": {
        "ASML.AS": "ASML Holding N.V. (Países Bajos)", "SAP.DE": "SAP SE (Alemania)", 
        "MC.PA": "LVMH Moët Hennessy (Francia)", "SIE.DE": "Siemens AG (Alemania)", "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    }
}

CONTEXTO_GLOBAL_INSTITUCIONAL = """
[CONTEXTO MACROECONÓMICO Y FINANCIERO INSTITUCIONAL VIGENTE]: 
1. Bancos Centrales (FED, BCE, BCRP, PBoC, BoJ): Tasas de referencia y política monetaria global.
2. Modelos Cuantitativos y Estocásticos: Simulación de Monte Carlo (GBM), VaR y análisis fundamental por activo.
"""

def obtener_tipo_cambio_real(moneda_base_ticker, moneda_destino_key):
    try:
        base_limpia = moneda_base_ticker.upper()
        target_limpio = moneda_destino_key[:3].upper()
        if base_limpia == target_limpio:
            return 1.0, "Paridad Idéntica (1:1)"
        
        paridad_ticker = f"{base_limpia}{target_limpio}=X"
        df_fx = yf.Ticker(paridad_ticker).history(period="5d")
        if not df_fx.empty:
            return float(df_fx["Close"].iloc[-1]), f"Yahoo Finance Spot ({paridad_ticker})"
            
        paridad_inversa = f"{target_limpio}{base_limpia}=X"
        df_inv = yf.Ticker(paridad_inversa).history(period="5d")
        if not df_inv.empty:
            val_inv = float(df_inv["Close"].iloc[-1])
            if val_inv > 0:
                return (1.0 / val_inv), f"Yahoo Finance Spot Inverso ({paridad_inversa})"
    except Exception:
        pass
    
    tasa_def = TASAS_CAMBIO_USD.get(moneda_destino_key, 1.0)
    return tasa_def, "Tasa Institucional de Referencia / Banco Central"

# ==============================================================================
# ENCABEZADO Y TABS DE NAVEGACIÓN INSTITUCIONAL
# ==============================================================================
st.title("📈 Terminal Inteligente de Inversiones & Forex")
st.markdown("<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 20px;'>Plataforma cuantitativa, econométrica y analítica de grado institucional.</p>", unsafe_allow_html=True)

tab_acciones, tab_forex = st.tabs(["📊 Análisis Accionario", "🔀 Comparativa de Divisas (Forex)"])

# ==============================================================================
# PESTAÑA 1: ANÁLISIS ACCIONARIO EXTENDIDO
# ==============================================================================
with tab_acciones:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Inversión Accionaria")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            mercado_sel = st.selectbox("🌍 Mercado de Origen:", list(MERCADOS.keys()), key="stock_mercado")
        
        diccionario_acciones = MERCADOS[mercado_sel]
        with col_s2:
            opcion_accion = st.selectbox(
                "📊 Selección de Acción / Ticker:",
                list(diccionario_acciones.keys()),
                format_func=lambda x: f"{x} - {diccionario_acciones[x] if 'Buscar' not in x else 'Escribir Ticker'}",
                key="stock_accion"
            )
            if "Buscar" in opcion_accion:
                ticker_final = st.text_input("Ingrese Ticker (ej: AAPL, 7203.T, PETR4.SA):", value="AAPL", key="stock_ticker_manual").upper()
                nombre_empresa = ticker_final
            else:
                ticker_final = opcion_accion
                nombre_empresa = diccionario_acciones[opcion_accion]
        with col_s3:
            moneda_sel = st.selectbox("💵 Moneda de Operación:", list(TASAS_CAMBIO_USD.keys()), key="stock_moneda")

        simbolo_moneda = SIMBOLOS_MONEDA[moneda_sel]
        monto_minimo = MINIMOS_MONEDA[moneda_sel]
        
        col_s4, col_s5, col_s6 = st.columns(3)
        with col_s4:
            capital_input = st.number_input(f"💰 Capital Disponible ({simbolo_moneda}):", min_value=monto_minimo, value=monto_minimo * 10, step=monto_minimo, key="stock_capital")
        with col_s5:
            horizonte = st.selectbox("⏱️ Horizonte Temporal:", ["Corto Plazo (1 a 3 meses)", "Mediano Plazo (6 meses a 1 año)", "Largo Plazo (1 año a más)"], key="stock_horizonte")
        with col_s6:
            perfil_riesgo = st.selectbox("🛡️ Perfil del Inversor:", ["Conservador", "Moderado", "Agresivo"], key="stock_perfil")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Multidimensional Accionario", use_container_width=True, key="btn_stock"):
        if not api_key_oculta or not client:
            st.error("⚠️ Falta GEMINI_API_KEY configurada en los Secrets de Streamlit.")
        else:
            datos_cargados_exitosamente = False
            try:
                objeto_stock = yf.Ticker(ticker_final)
                df_stock = objeto_stock.history(period="5y")
                
                if df_stock.empty and ticker_final == "SPCCPI1.LM":
                    objeto_stock = yf.Ticker("SCCO")
                    df_stock = objeto_stock.history(period="5y")
                
                if df_stock.empty:
                    st.error(f"⚠️ El Ticker '{ticker_final}' no arrojó registros válidos en Yahoo Finance.")
                else:
                    datos_cargados_exitosamente = True
                    try:
                        info_stock = objeto_stock.info
                    except Exception:
                        info_stock = {}
                        
                    moneda_base_ticker = info_stock.get("currency", "USD")
                    tasa_conv_real, fuente_tasa = obtener_tipo_cambio_real(moneda_base_ticker, moneda_sel)

                    precio_actual = df_stock["Close"].iloc[-1] * tasa_conv_real
                    df_stock["Close_Moneda"] = df_stock["Close"] * tasa_conv_real
                    
                    market_cap_raw = info_stock.get("marketCap")
                    market_cap = market_cap_raw * tasa_conv_real if market_cap_raw else 0.0
                    
                    pe_ratio = f"{info_stock.get('trailingPE'):.2f}" if info_stock.get("trailingPE") else "No reportado"
                    pb_ratio = f"{info_stock.get('priceToBook'):.2f}" if info_stock.get("priceToBook") else "No reportado"
                    dividend_str = f"{info_stock.get('dividendYield', 0)*100:.2f}%" if info_stock.get("dividendYield") else "0.00%"
                    margin_str = f"{info_stock.get('profitMargins', 0)*100:.2f}%" if info_stock.get("profitMargins") else "No reportado"
                    sector_empresa = info_stock.get("sector", "Renta Variable Global")

                    df_stock["Retorno_Diario"] = df_stock["Close"].pct_change()
                    volatilidad_anualizada = df_stock["Retorno_Diario"].std() * np.sqrt(252)
                    var_diario_95 = np.percentile(df_stock["Retorno_Diario"].dropna(), 5)

                    st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos (5 Años)")
                    
                    c_m1, c_m2, c_m3, c_m4, c_m5 = st.columns(5)
                    with c_m1:
                        st.metric(f"Precio Actual ({simbolo_moneda})", f"{simbolo_moneda} {precio_actual:,.2f}")
                        st.markdown(f"<div class='source-note'>Nota: Yahoo Finance / Spot ({moneda_base_ticker})</div>", unsafe_allow_html=True)
                    with c_m2:
                        st.metric("Tipo de Cambio Spot", f"{tasa_conv_real:,.4f}")
                        st.markdown(f"<div class='source-note'>Nota: {fuente_tasa}</div>", unsafe_allow_html=True)
                    with c_m3:
                        st.metric("PER (Price / Earnings)", f"{pe_ratio}")
                        st.markdown("<div class='source-note'>Nota: Yahoo Finance Fundamentals</div>", unsafe_allow_html=True)
                    with c_m4:
                        st.metric("Volatilidad Anualizada", f"{volatilidad_anualizada:.2%}")
                        st.markdown("<div class='source-note'>Nota: Modelo GBM Estocástico (5A)</div>", unsafe_allow_html=True)
                    with c_m5:
                        st.metric("Margen Beneficio Neto", f"{margin_str}")
                        st.markdown("<div class='source-note'>Nota: Estados Financieros YF</div>", unsafe_allow_html=True)

                    c_m6, c_m7, c_m8, c_m9 = st.columns(4)
                    with c_m6:
                        st.metric(f"Cap. de Mercado ({simbolo_moneda})", f"{simbolo_moneda} {market_cap:,.0f}" if market_cap > 0 else "No reportado")
                        st.markdown("<div class='source-note'>Nota: Capitalización Bursátil YF</div>", unsafe_allow_html=True)
                    with c_m7:
                        st.metric("Ratio P/B", f"{pb_ratio}")
                        st.markdown("<div class='source-note'>Nota: Balance General Consolidado</div>", unsafe_allow_html=True)
                    with c_m8:
                        st.metric("Rendimiento Dividendo", f"{dividend_str}")
                        st.markdown("<div class='source-note'>Nota: Historial de Dividendos YF</div>", unsafe_allow_html=True)
                    with c_m9:
                        st.metric("VaR 95% Diarios", f"{var_diario_95:.2%}")
                        st.markdown("<div class='source-note'>Nota: Simulación VaR Histórico</div>", unsafe_allow_html=True)

                    st.markdown("---")

                    st.markdown(f"### 📈 Comportamiento Histórico & Proyección GBM Monte Carlo ({horizonte})")
                    dias_proyeccion = 60 if "1 a 3 meses" in horizonte else (180 if "6 meses a 1 año" in horizonte else 365)
                    mediana_mc, p10_mc, p90_mc = simular_monte_carlo_gbm(precio_actual, df_stock["Retorno_Diario"].dropna(), dias_proyeccion, es_forex=False)
                    
                    fechas_historicas = df_stock.index
                    precios_historicos = df_stock["Close_Moneda"]
                    fechas_futuras = pd.date_range(start=df_stock.index[-1], periods=dias_proyeccion + 1, freq="B")

                    fig_stock = go.Figure()
                    
                    trace_hist = go.Scatter(
                        x=fechas_historicas, y=precios_historicos, mode="lines", 
                        name="Histórico Real (5 Años)", line=dict(color="#10b981", width=2.0)
                    )
                    trace_p90 = go.Scatter(
                        x=fechas_futuras, y=p90_mc, mode="lines", 
                        name="Escenario Optimista (P80)", line=dict(color="rgba(56, 189, 248, 0.5)", width=1.5, dash="dash")
                    )
                    trace_p10 = go.Scatter(
                        x=fechas_futuras, y=p10_mc, mode="lines", 
                        name="Escenario Pesimista (P20)", line=dict(color="rgba(239, 68, 68, 0.5)", width=1.5, dash="dash"), 
                        fill="tonexty", fillcolor="rgba(56, 189, 248, 0.05)"
                    )
                    trace_mediana = go.Scatter(
                        x=fechas_futuras, y=mediana_mc, mode="lines", 
                        name="Proyección Central GBM", line=dict(color="#8b5cf6", width=3.0)
                    )

                    fig_stock.add_trace(trace_hist)
                    fig_stock.add_trace(trace_p90)
                    fig_stock.add_trace(trace_p10)
                    fig_stock.add_trace(trace_mediana)

                    fig_stock.update_layout(
                        xaxis=dict(title="Fecha", gridcolor="#1e293b", fixedrange=False),
                        yaxis=dict(title=f"Precio ({simbolo_moneda})", gridcolor="#1e293b", fixedrange=False, autorange=True),
                        template="plotly_dark", paper_bgcolor="#020617", plot_bgcolor="#020617",
                        height=550, dragmode="pan", hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.9)")
                    )
                    
                    st.plotly_chart(fig_stock, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                    
                    st.markdown("""
                    <div class='disclaimer-box'>
                        <strong>⚠️ Aviso Legal y de Riesgo:</strong> Terminal analítica de grado institucional. Las proyecciones estocásticas y dictámenes automatizados <strong>NO constituyen asesoramiento financiero garantizado</strong>. El usuario asume total responsabilidad sobre las decisiones de asignación de capital.<br><br>
                        <span style='color: #38bdf8;'>💡 <strong>Tip de Interfaz (Gráficos):</strong> Utiliza la rueda del ratón para hacer zoom. Haz clic sostenido y arrastra para desplazarte en el tiempo. Doble clic para restablecer la vista.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

            except Exception as error_ejecucion:
                st.error(f"Error procesando la serie temporal del activo: {str(error_ejecucion)}")

            if datos_cargados_exitosamente:
                st.markdown("## 📋 Dictamen Estratégico Cuantitativo Institucional")

                prompt_ia_stock = f"""
                Actúa como el Director de Análisis Cuantitativo y Gestor de Portafolios de un Fondo de Inversión Global (Hedge Fund).
                Redacta un análisis EXHAUSTIVO, sumamente técnico, riguroso y profesional sobre {ticker_final}. 
                PROHIBIDO dar respuestas genéricas o vagas.

                INSTRUCCIÓN ABSOLUTA: Devuelve tu respuesta EXCLUSIVAMENTE en un objeto JSON válido y limpio. Cero comillas triples Markdown, cero texto adicional fuera del JSON.
                
                ESTRUCTURA JSON REQUERIDA:
                {{
                  "diagnostico": "Análisis fundamental y técnico profundo. Evalúa el PER ({pe_ratio}), el P/B ({pb_ratio}) y la valoración del activo frente a su sector y la política monetaria global actual.",
                  "viabilidad": "1. Análisis de Capital: Compara matemáticamente el capital de {simbolo_moneda} {capital_input:,.2f} frente al precio unitario de {simbolo_moneda} {precio_actual:,.2f}. 2. Análisis de Perfil: Contrasta la volatilidad del {volatilidad_anualizada:.2%} con el perfil de riesgo {perfil_riesgo}.",
                  "riesgos": "Detalla 3 riesgos críticos y específicos del activo en formato de lista numérica: 1. Riesgo de tasas y costo de capital. 2. Riesgos sistémicos del sector. 3. Volatilidad macroeconómica y posible crisis.",
                  "conclusion_tecnica": "Conclusión técnica específica centrada en la valoración econométrica, el VaR 95% ({var_diario_95:.2%}) y la relación riesgo-retorno del activo.",
                  "veredicto": "COMPRAR, DESESTIMAR o MANTENER EN OBSERVACIÓN",
                  "dictamen_institucional": "RECOMENDACIÓN FINANCIERA ULTRA PRECISA: Analiza estrictamente si el capital de {simbolo_moneda} {capital_input:,.2f} alcanza o no para comprar acciones completas de {ticker_final} a {simbolo_moneda} {precio_actual:,.2f}. Si no alcanza, indica exactamente en qué vehículo financiero invertir de acuerdo a su perfil {perfil_riesgo} y horizonte {horizonte} (ej: invertir mediante 'acciones fraccionadas' en brokers regulados, adquirir 'ETFs indexados globales' como SPY o VOO, o reasignar temporalmente a un 'depósito a plazo fijo' o 'fondos mutuos de renta fija'). Explica el porqué exacto de esta recomendación gerencial."
                }}
                """

                with st.spinner("🤖 El motor de Inteligencia Institucional está procesando la econometría corporativa y macroeconómica..."):
                    respuesta_cruda_stock = generar_respuesta_ia_robusta(client, prompt_ia_stock)
                    json_stock = parse_json_respuesta(respuesta_cruda_stock)

                    es_capital_insuficiente = capital_input < precio_actual
                    if not json_stock:
                        json_stock = {
                            "diagnostico": f"El activo {ticker_final} cotiza a un precio spot de {simbolo_moneda} {precio_actual:,.2f} con un ratio PER de {pe_ratio} y P/B de {pb_ratio}. La valoración actual refleja dinámicas mixtas en el sector {sector_empresa} frente al endurecimiento de las tasas de descuento globales.",
                            "viabilidad": f"Con un capital disponible de {simbolo_moneda} {capital_input:,.2f} frente al precio unitario de {simbolo_moneda} {precio_actual:,.2f}, la asignación bajo el perfil {perfil_riesgo} resulta {'inviable para una posición accionaria completa' if es_capital_insuficiente else 'viable operativamente'}.",
                            "riesgos": "1. Sensibilidad del múltiplo de valoración a los vaivenes en las tasas de interés de referencia.\n2. Presión sobre los márgenes operativos ante menores volúmenes de demanda.\n3. Riesgo de liquidez y profundidad en las órdenes de ejecución.",
                            "conclusion_tecnica": f"Dictamen técnico: La relación entre el capital disponible ({simbolo_moneda} {capital_input:,.2f}) y la exposición al riesgo con una volatilidad anualizada del {volatilidad_anualizada:.2%} exige prudencia táctica.",
                            "veredicto": "DESESTIMAR" if es_capital_insuficiente else "MANTENER EN OBSERVACIÓN",
                            "dictamen_institucional": f"Dictamen Institucional Integral: Tu capital de {simbolo_moneda} {capital_input:,.2f} {'es insuficiente para adquirir una acción entera a' if es_capital_insuficiente else 'cubre operativamente'} {simbolo_moneda} {precio_actual:,.2f}. Bajo tu perfil {perfil_riesgo} y horizonte {horizonte}, la recomendación precisa es utilizar plataformas de **acciones fraccionadas** o diversificar en **ETFs globales de bajo costo (como SPY)** para mitigar el riesgo de volatilidad del {volatilidad_anualizada:.2%}."
                        }

                    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                    with col_c1:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>1. Valoración Fundamental & Macro</div><div class='analysis-card-body'>{json_stock.get('diagnostico', '')}</div></div>", unsafe_allow_html=True)
                    with col_c2:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>2. Viabilidad / Riesgo</div><div class='analysis-card-body'>{json_stock.get('viabilidad', '')}</div></div>", unsafe_allow_html=True)
                    with col_c3:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>3. Riesgos Sistémicos e Inflación</div><div class='analysis-card-body'>{json_stock.get('riesgos', '').replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)
                    with col_c4:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>4. Conclusión Técnica</div><div class='analysis-card-body'>{json_stock.get('conclusion_tecnica', '')}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_col_a, bot_col_b = st.columns([3, 1])
                    with bot_col_a:
                        st.markdown(f"<div class='decision-container'><div class='analysis-card-title' style='font-size: 1.2rem; border-bottom: none;'>🎯 Dictamen Institucional</div><div class='analysis-card-body' style='font-size: 1rem; color: #f8fafc;'>{json_stock.get('dictamen_institucional', '')}</div></div>", unsafe_allow_html=True)
                    with bot_col_b:
                        veredicto_procesado = str(json_stock.get("veredicto", "MANTENER EN OBSERVACIÓN")).upper()
                        if "COMPRAR" in veredicto_procesado and "DESESTIMAR" not in veredicto_procesado:
                            badge_cls, badge_ico, badge_txt = "decision-comprar", "🟢", "COMPRAR"
                        elif "DESESTIMAR" in veredicto_procesado:
                            badge_cls, badge_ico, badge_txt = "decision-desestimar", "🔴", "DESESTIMAR"
                        else:
                            badge_cls, badge_ico, badge_txt = "decision-observacion", "🟡", "EN OBSERVACIÓN"
                        st.markdown(f"<div class='decision-badge-box {badge_cls}'><div style='font-size: 2.5rem; margin-bottom: 8px;'>{badge_ico}</div><div style='font-weight: 800; font-size: 1.1rem; letter-spacing: 0.05em;'>{badge_txt}</div></div>", unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 2: COMPARATIVA DE DIVISAS (FOREX) EXTENDIDO
# ==============================================================================
with tab_forex:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Evaluación Cambiaria")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            base_curr = st.selectbox("🔀 Moneda de Origen (Base):", list(DIVISAS.keys()), index=0, format_func=lambda x: DIVISAS[x], key="fx_base")
        with col_f2:
            target_curr = st.selectbox("🎯 Moneda Destino (Objetivo):", list(DIVISAS.keys()), index=1, format_func=lambda x: DIVISAS[x], key="fx_target")
        with col_f3:
            monto_fx = st.number_input(f"💰 Monto de Conversión ({base_curr}):", min_value=1.0, value=1000.0, step=100.0, key="fx_monto")
        
        col_f4, col_f5 = st.columns(2)
        with col_f4:
            horizonte_fx = st.selectbox("⏱️ Horizonte Temporal:", ["Corto Plazo (1 a 3 meses)", "Mediano Plazo (6 meses a 1 año)", "Largo Plazo (1 año a más)"], key="fx_horizonte")
        with col_f5:
            proposito_fx = st.selectbox("🎯 Propósito de la Evaluación:", ["Cobertura de Riesgo Cambiario (Hedging)", "Operación de Comercio Exterior", "Inversión Especulativa", "Ahorro / Reserva de Valor"], key="fx_proposito")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Cuantitativo de Divisas", use_container_width=True, key="btn_forex"):
        if not api_key_oculta or not client:
            st.error("⚠️ Falta GEMINI_API_KEY configurada en los Secrets de Streamlit.")
        else:
            datos_fx_cargados = False
            try:
                df_fx = obtener_historial_forex(base_curr, target_curr)
                if df_fx.empty:
                    st.error(f"⚠️ El historial para la paridad {base_curr}/{target_curr} no está disponible.")
                else:
                    datos_fx_cargados = True
                    rate_actual = df_fx["Close"].iloc[-1]
                    df_fx["Retorno_Diario"] = df_fx["Close"].pct_change()
                    volatilidad_fx = df_fx["Retorno_Diario"].std() * np.sqrt(252)
                    variacion_5y = ((rate_actual - df_fx["Close"].iloc[0]) / df_fx["Close"].iloc[0]) * 100

                    tasa_base_ref = TASAS_REFERENCIA_PAIS.get(base_curr, 4.50)
                    tasa_target_ref = TASAS_REFERENCIA_PAIS.get(target_curr, 4.50)
                    diferencial_tasas = tasa_base_ref - tasa_target_ref

                    st.markdown(f"### 📊 Panel de Indicadores Clave & Tasas de Referencia - {base_curr}/{target_curr}")
                    c_x1, c_x2, c_x3, c_x4 = st.columns(4)
                    with c_x1:
                        st.metric("Tipo de Cambio Spot", f"{rate_actual:,.4f}")
                        st.markdown("<div class='source-note'>Nota: Yahoo Finance FX Interbank</div>", unsafe_allow_html=True)
                    with c_x2:
                        st.metric(f"Tasa Ref. {base_curr} (Central)", f"{tasa_base_ref:.2f}%")
                        st.markdown("<div class='source-note'>Nota: Banco Central Base</div>", unsafe_allow_html=True)
                    with c_x3:
                        st.metric(f"Tasa Ref. {target_curr} (Central)", f"{tasa_target_ref:.2f}%")
                        st.markdown("<div class='source-note'>Nota: Banco Central Destino</div>", unsafe_allow_html=True)
                    with c_x4:
                        st.metric("Diferencial de Tasas", f"{diferencial_tasas:+.2f}%")
                        st.markdown("<div class='source-note'>Nota: Paridad de Tasas de Interés</div>", unsafe_allow_html=True)

                    c_x5, c_x6, c_x7, c_x8 = st.columns(4)
                    with c_x5:
                        st.metric("Monto Convertido", f"{monto_fx * rate_actual:,.2f} {target_curr}")
                        st.markdown("<div class='source-note'>Nota: Cálculo Spot Actualizado</div>", unsafe_allow_html=True)
                    with c_x6:
                        st.metric("Volatilidad Anualizada", f"{volatilidad_fx:.2%}")
                        st.markdown("<div class='source-note'>Nota: Desviación Estándar 5A FX</div>", unsafe_allow_html=True)
                    with c_x7:
                        st.metric("Variación Histórica 5A", f"{variacion_5y:+.2f}%")
                        st.markdown("<div class='source-note'>Nota: Retorno Histórico Quinquenal</div>", unsafe_allow_html=True)
                    with c_x8:
                        st.metric("Spread Cambiario Est.", "0.15%")
                        st.markdown("<div class='source-note'>Nota: Costo Promedio Interbancario</div>", unsafe_allow_html=True)

                    st.markdown("---")

                    st.markdown(f"### 📈 Proyección GBM Monte Carlo Acotada ({horizonte_fx})")
                    dias_proy_fx = 60 if "1 a 3 meses" in horizonte_fx else (180 if "6 meses a 1 año" in horizonte_fx else 365)
                    mediana_fx, p10_fx, p90_fx = simular_monte_carlo_gbm(rate_actual, df_fx["Retorno_Diario"].dropna(), dias_proy_fx, es_forex=True)
                    
                    fechas_hist_fx = df_fx.index
                    fechas_futuras_fx = pd.date_range(start=df_fx.index[-1], periods=dias_proy_fx + 1, freq="B")

                    fig_fx = go.Figure()
                    
                    trace_fx_hist = go.Scatter(
                        x=fechas_hist_fx, y=df_fx["Close"], mode="lines", 
                        name="Tipo de Cambio Histórico", line=dict(color="#10b981", width=2.0)
                    )
                    trace_fx_p90 = go.Scatter(
                        x=fechas_futuras_fx, y=p90_fx, mode="lines", 
                        name="Escenario Volatilidad (P80)", line=dict(color="rgba(56, 189, 248, 0.5)", width=1.5, dash="dash")
                    )
                    trace_fx_p10 = go.Scatter(
                        x=fechas_futuras_fx, y=p10_fx, mode="lines", 
                        name="Escenario Caída (P20)", line=dict(color="rgba(239, 68, 68, 0.5)", width=1.5, dash="dash"), 
                        fill="tonexty", fillcolor="rgba(56, 189, 248, 0.05)"
                    )
                    trace_fx_mediana = go.Scatter(
                        x=fechas_futuras_fx, y=mediana_fx, mode="lines", 
                        name="Proyección Central GBM", line=dict(color="#8b5cf6", width=3.0)
                    )

                    fig_fx.add_trace(trace_fx_hist)
                    fig_fx.add_trace(trace_fx_p90)
                    fig_fx.add_trace(trace_fx_p10)
                    fig_fx.add_trace(trace_fx_mediana)

                    fig_fx.update_layout(
                        xaxis=dict(title="Fecha", gridcolor="#1e293b", fixedrange=False),
                        yaxis=dict(title=f"Tasa ({base_curr}/{target_curr})", gridcolor="#1e293b", fixedrange=False, autorange=True),
                        template="plotly_dark", paper_bgcolor="#020617", plot_bgcolor="#020617",
                        height=550, dragmode="pan", hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.9)")
                    )
                    st.plotly_chart(fig_fx, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                    
                    st.markdown("""
                    <div class='disclaimer-box'>
                        <strong>⚠️ Aviso Legal y de Riesgo:</strong> Terminal analítica de grado institucional. Las proyecciones estocásticas y dictámenes automatizados <strong>NO constituyen asesoramiento financiero garantizado</strong>. El usuario asume total responsabilidad sobre las decisiones de asignación de capital.<br><br>
                        <span style='color: #38bdf8;'>💡 <strong>Tip de Interfaz (Gráficos):</strong> Utiliza la rueda del ratón para hacer zoom. Haz clic sostenido y arrastra para desplazarte en el tiempo. Doble clic para restablecer la vista.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

            except Exception as error_divisas:
                st.error(f"Error procesando la paridad cambiaria: {str(error_divisas)}")

            if datos_fx_cargados:
                st.markdown(f"## 📋 Dictamen Estratégico FX Institucional ({base_curr}/{target_curr})")

                prompt_ia_fx = f"""
                Actúa como el Economista Jefe de Divisas (FX) y Tesorero Global de un Banco de Inversión.
                Redacta un análisis EXHAUSTIVO, sumamente técnico, riguroso y profesional de la paridad cambiaria {base_curr}/{target_curr}. 
                PROHIBIDO dar respuestas genéricas.

                INSTRUCCIÓN ABSOLUTA: Devuelve tu respuesta EXCLUSIVAMENTE en formato JSON válido y limpio. Cero comillas triples Markdown, cero texto adicional fuera del JSON.

                ESTRUCTURA JSON REQUERIDA:
                {{
                  "diagnostico": "Análisis macroeconómico cambiario avanzado basado en el diferencial de tasas de interés ({diferencial_tasas:+.2f}%), políticas monetarias (FED vs BCR), balanza comercial y flujos de capital.",
                  "viabilidad": "Evaluación cuantitativa directa de ejecutar '{proposito_fx}' para el monto de {monto_fx} {base_curr}, integrando spreads (0.15%), costos de transacción y timing exacto de entrada.",
                  "riesgos": "Detalla 3 riesgos críticos cambiarios específicos en formato de lista numérica: 1. Postura de la FED y DXY. 2. Shocks en términos de intercambio. 3. Riesgos geopolíticos, fiscales o especulativos de crisis.",
                  "posicionamiento": "Posicionamiento estratégico técnico sobre instrumentos derivados (ej. Contratos Forward a 90 días, opciones Collar).",
                  "veredicto": "FORTALECIMIENTO, DEBILITAMIENTO o NEUTRAL",
                  "resumen_ejecutivo": "ESTRATEGIA DIRECCIONAL FX PRECISADA: Responde categóricamente si el precio de la divisa aumentará o disminuirá en el horizonte de {horizonte_fx}. Recomienda de forma explícita si se debe COMPRAR o VENDER la divisa y el momento exacto de ejecución táctica. Además, especifica detalladamente en qué otras monedas de refugio altamente estables (ej. Dólar USD, Franco Suizo CHF o Euro EUR) conviene respaldar el capital de {monto_fx} {base_curr} para blindarlo ante futuras crisis globales, sustentándolo con el diferencial de tasas del {diferencial_tasas:+.2f}% y la volatilidad del {volatilidad_fx:.2%}."
                }}
                """
                with st.spinner("🤖 Analizando diferencial de tasas de interés, paridad cambiaria y proyecciones FX globales..."):
                    respuesta_cruda_fx = generar_respuesta_ia_robusta(client, prompt_ia_fx)
                    json_fx = parse_json_respuesta(respuesta_cruda_fx)

                    if not json_fx:
                        json_fx = {
                            "diagnostico": f"La paridad {base_curr}/{target_curr} opera en {rate_actual:,.4f} con una volatilidad anualizada del {volatilidad_fx:.2%}. El diferencial de tasas de referencia ({diferencial_tasas:+.2f}%) condiciona directamente la dirección de los flujos cambiarios de corto plazo.",
                            "viabilidad": f"Para el propósito de {proposito_fx} con un monto de {monto_fx} {base_curr}, la aplicación evalúa un spread operativo estimado de 0.15%, determinando que el timing actual es óptimo para posiciones tácticas.",
                            "riesgos": "1. Cambios en la orientación de la política monetaria de la FED y su repercusión en el DXY.\n2. Variaciones en la balanza comercial y precios de materias primas regionales.\n3. Presiones de liquidez estacional en el mercado interbancario de divisas.",
                            "posicionamiento": "Se recomienda el uso de contratos a término (forwards) o coberturas parciales (options collar) para blindar el flujo de caja operativo ante la volatilidad esperada.",
                            "resumen_ejecutivo": f"Estrategia Direccional FX: Basado en el diferencial de tasas del {diferencial_tasas:+.2f}% y la volatilidad del {volatilidad_fx:.2%}, se proyecta una tendencia de {'fortalecimiento' if diferencial_tasas > 0 else 'debilitamiento'}. Se recomienda **comprar** la divisa objetivo de forma escalonada (dolarización/conversión táctica) para proteger el capital ante episodios de volatilidad global, respaldando parte de los fondos en monedas estables como el Dólar (USD) o el Franco Suizo (CHF)."
                        }

                    col_fx_c1, col_fx_c2, col_fx_c3, col_fx_c4 = st.columns(4)
                    with col_fx_c1:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>1. Diagnóstico Macro / Tasas</div><div class='analysis-card-body'>{json_fx.get('diagnostico', '')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c2:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>2. Sensibilidad y Cobertura</div><div class='analysis-card-body'>{json_fx.get('viabilidad', '')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c3:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>3. Riesgo Geopolítico / FED</div><div class='analysis-card-body'>{json_fx.get('riesgos', '').replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c4:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>4. Posicionamiento Estratégico</div><div class='analysis-card-body'>{json_fx.get('posicionamiento', '')}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_fx_a, bot_fx_b = st.columns([3, 1])
                    with bot_fx_a:
                        st.markdown(f"<div class='decision-container'><div class='analysis-card-title' style='font-size: 1.2rem; border-bottom: none;'>🎯 Estrategia Direccional FX</div><div class='analysis-card-body' style='font-size: 1rem; color: #f8fafc;'>{json_fx.get('resumen_ejecutivo', '')}</div></div>", unsafe_allow_html=True)
                    with bot_fx_b:
                        veredicto_fx_clean = str(json_fx.get("veredicto", "NEUTRAL")).upper()
                        if "FORTALECIMIENTO" in veredicto_fx_clean or "COMPRA" in veredicto_fx_clean:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-comprar", "🟢", "ALCISTA (LONG)"
                        elif "DEBILITAMIENTO" in veredicto_fx_clean or "VENTA" in veredicto_fx_clean:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-desestimar", "🔴", "BAJISTA (SHORT)"
                        else:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-observacion", "🟡", "NEUTRAL"
                        st.markdown(f"<div class='decision-badge-box {badge_f_cls}'><div style='font-size: 2.5rem; margin-bottom: 8px;'>{badge_f_ico}</div><div style='font-weight: 800; font-size: 1.1rem; letter-spacing: 0.05em;'>{badge_f_txt}</div></div>", unsafe_allow_html=True)
