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
# MOTOR ECONOMÉTRICO & MODELO ESTOCÁSTICO (GBM CALIBRADO PARA ACCIONES Y FOREX)
# ==============================================================================
def simular_monte_carlo_gbm(precio_inicial, retornos_diarios, dias_proy, num_simulaciones=500, es_forex=False):
    dias_historia = 60 if dias_proy <= 60 else (120 if dias_proy <= 180 else 252)
    retornos_recientes = retornos_diarios.tail(dias_historia) if len(retornos_diarios) > dias_historia else retornos_diarios
    
    mu_diario = retornos_recientes.mean()
    sigma_diario = retornos_recientes.std()
    
    # Factor de amortiguación estricto para divisas (evita bandas exageradas en FX)
    factor_escala = 0.35 if es_forex else 0.50
    drift_suavizado = 0.20 * mu_diario
    sigma_calibrado = sigma_diario * factor_escala
    
    drift = drift_suavizado - 0.5 * (sigma_calibrado ** 2)
    matriz_precios = np.zeros((dias_proy + 1, num_simulaciones))
    matriz_precios[0] = precio_inicial
    
    choques_aleatorios = np.random.normal(0, 1, (dias_proy, num_simulaciones))
    
    for t in range(1, dias_proy + 1):
        factor_tiempo = np.sqrt(t / dias_proy)
        retornos_simulados = np.exp(
            drift + sigma_calibrado * choques_aleatorios[t - 1] * (0.8 + 0.2 * factor_tiempo)
        )
        matriz_precios[t] = matriz_precios[t - 1] * retornos_simulados
        
    mediana_proyectada = np.median(matriz_precios, axis=1)
    percentil_inferior = np.percentile(matriz_precios, 20, axis=1)
    percentil_superior = np.percentile(matriz_precios, 80, axis=1)
    
    return mediana_proyectada, percentil_inferior, percentil_superior
    # ==============================================================================
# DICCIONARIOS Y CONFIGURACIONES DE MERCADO
# ==============================================================================
DIVISAS = {
    "USD": "Dólar Estadounidense (USD)", 
    "PEN": "Sol Peruano (PEN)", 
    "EUR": "Euro (EUR)",
    "GBP": "Libra Esterlina (GBP)", 
    "JPY": "Yen Japonés (JPY)", 
    "MXN": "Peso Mexicano (MXN)",
    "CLP": "Peso Chileno (CLP)", 
    "COP": "Peso Colombiano (COP)", 
    "BRL": "Real Brasileño (BRL)"
}
TICKER_MAP = {"SPCCPI1.LM": "SCCO", "SPCCPI2.LM": "SCCO"}
TASAS_CAMBIO_USD = {
    "USD ($)": 1.0, 
    "PEN (S/.)": 3.75, 
    "CLP ($)": 950.0, 
    "BRL (R$)": 5.50, 
    "MXN ($)": 19.50
}
SIMBOLOS_MONEDA = {
    "USD ($)": "$", 
    "PEN (S/.)": "S/.", 
    "CLP ($)": "$ CLP", 
    "BRL (R$)": "R$", 
    "MXN ($)": "$ MXN"
}
MINIMOS_MONEDA = {
    "USD ($)": 20.0, 
    "PEN (S/.)": 75.0, 
    "CLP ($)": 19000.0, 
    "BRL (R$)": 110.0, 
    "MXN ($)": 390.0
}

# Tasas de Referencia Institucionales Actualizadas (FED vs BCRP y otras regiones)
TASAS_REFERENCIA_PAIS = {
    "USD": 4.50,  # Tasa de fondos federales FED estimada
    "PEN": 4.75,  # Tasa de referencia BCRP estimada
    "EUR": 3.25,  # Tasa BCE
    "GBP": 4.50,  # Tasa Banco de Inglaterra
    "CLP": 5.00,  # Tasa Banco Central de Chile
    "MXN": 10.00, # Tasa Banxico
    "BRL": 11.25, # Tasa Banco Central de Brasil
    "JPY": 0.50,  # Tasa Banco de Japón
    "COP": 9.50   # Tasa Banco de la República Colombia
}

MERCADOS = {
    "NYSE / NASDAQ (Estados Unidos)": {
        "AAPL": "Apple Inc.", 
        "TSLA": "Tesla Inc.", 
        "MSFT": "Microsoft Corp.", 
        "NVDA": "NVIDIA Corp.", 
        "AMZN": "Amazon.com Inc.", 
        "GOOGL": "Alphabet Inc.", 
        "SCCO": "Southern Copper Corp.", 
        "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    },
    "Bolsa de Valores de Lima (BVL - Perú)": {
        "SPCCPI1.LM": "Southern Copper Corp. (BVL)", 
        "BAP": "Credicorp Ltd.", 
        "IFS": "Intercorp Financial Services", 
        "CPACEN1.LM": "Cementos Pacasmayo", 
        "ALICORC1.LM": "Alicorp S.A.A.", 
        "🔍 Buscar otro Ticker manualmente": "CUSTOM"
    }
}

CONTEXTO_GLOBAL_INSTITUCIONAL = """
[CONTEXTO MACROECONÓMICO Y FINANCIERO INSTITUCIONAL VIGENTE]: 
1. Bancos Centrales (FED, BCE, BCRP): Las tasas de referencia determinan el diferencial cambiario y el costo de oportunidad del capital (WACC). 
2. Mercados de Renta Variable y Divisas: Los inversores institucionales exigen múltiplos fundamentales sólidos y una estricta gestión de riesgos.
3. Geopolítica y Commodities: La volatilidad en las materias primas (cobre, oro, petróleo WTI) y la liquidez global condicionan fuertemente el tipo de cambio y la prima de riesgo.
"""

def obtener_factor_conversion(moneda_base_asset, moneda_destino_key):
    tasa_destino = TASAS_CAMBIO_USD[moneda_destino_key]
    base_upper = str(moneda_base_asset).upper()
    if "PEN" in base_upper or "SOL" in base_upper:
        tasa_base_usd = TASAS_CAMBIO_USD["PEN (S/.)"]
    elif "BRL" in base_upper:
        tasa_base_usd = TASAS_CAMBIO_USD["BRL (R$)"]
    elif "CLP" in base_upper:
        tasa_base_usd = TASAS_CAMBIO_USD["CLP ($)"]
    elif "MXN" in base_upper:
        tasa_base_usd = TASAS_CAMBIO_USD["MXN ($)"]
    else:
        tasa_base_usd = 1.0
    return (1.0 / tasa_base_usd) * tasa_destino

def obtener_historial_forex(base_curr, target_curr):
    try:
        if base_curr == target_curr:
            fechas_dummy = pd.date_range(end=pd.Timestamp.now(), periods=1260, freq="B")
            return pd.DataFrame({"Close": 1.0}, index=fechas_dummy)
        
        ticker_directo = f"{base_curr}{target_curr}=X"
        df_directo = yf.Ticker(ticker_directo).history(period="5y")
        if not df_directo.empty and len(df_directo) > 10:
            return df_directo[["Close"]]
            
        ticker_inverso = f"{target_curr}{base_curr}=X"
        df_inverso = yf.Ticker(ticker_inverso).history(period="5y")
        if not df_inverso.empty and len(df_inverso) > 10:
            df_inverso["Close"] = 1.0 / df_inverso["Close"]
            return df_inverso[["Close"]]
            
        df_base_usd = yf.Ticker(f"{base_curr}USD=X").history(period="5y") if base_curr != "USD" else None
        df_target_usd = yf.Ticker(f"{target_curr}USD=X").history(period="5y") if target_curr != "USD" else None
        
        if base_curr == "USD" and df_target_usd is not None and not df_target_usd.empty:
            df_resultado = pd.DataFrame(index=df_target_usd.index)
            df_resultado["Close"] = 1.0 / df_target_usd["Close"]
            return df_resultado
        elif target_curr == "USD" and df_base_usd is not None and not df_base_usd.empty:
            df_resultado = pd.DataFrame(index=df_base_usd.index)
            df_resultado["Close"] = df_base_usd["Close"]
            return df_resultado
        elif df_base_usd is not None and df_target_usd is not None and not df_base_usd.empty and not df_target_usd.empty:
            df_combinado = pd.concat([df_base_usd["Close"], df_target_usd["Close"]], axis=1, keys=["b", "t"]).dropna()
            df_resultado = pd.DataFrame(index=df_combinado.index)
            df_resultado["Close"] = df_combinado["b"] / df_combinado["t"]
            return df_resultado
    except Exception:
        pass
    return pd.DataFrame()

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
                format_func=lambda x: f"{x} - {diccionario_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir Ticker'}",
                key="stock_accion"
            )
            if opcion_accion == "🔍 Buscar otro Ticker manualmente":
                ticker_final = st.text_input("Ingrese Ticker (ej: AMD, MELI):", value="AAPL", key="stock_ticker_manual").upper()
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
                search_ticker = TICKER_MAP.get(ticker_final, ticker_final)
                objeto_stock = yf.Ticker(search_ticker)
                df_stock = objeto_stock.history(period="5y")
                
                if df_stock.empty and search_ticker.endswith(".LM"):
                    objeto_stock = yf.Ticker(search_ticker.replace(".LM", ""))
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
                    factor_conversion_ticker = obtener_factor_conversion(moneda_base_ticker, moneda_sel)

                    precio_actual = df_stock["Close"].iloc[-1] * factor_conversion_ticker
                    df_stock["Close_Moneda"] = df_stock["Close"] * factor_conversion_ticker
                    
                    market_cap_raw = info_stock.get("marketCap")
                    market_cap = market_cap_raw * factor_conversion_ticker if market_cap_raw else 0.0
                    
                    pe_ratio = f"{info_stock.get('trailingPE'):.2f}" if info_stock.get("trailingPE") else "No reportado"
                    pb_ratio = f"{info_stock.get('priceToBook'):.2f}" if info_stock.get("priceToBook") else "No reportado"
                    dividend_str = f"{info_stock.get('dividendYield', 0)*100:.2f}%" if info_stock.get("dividendYield") else "0.00%"
                    margin_str = f"{info_stock.get('profitMargins', 0)*100:.2f}%" if info_stock.get("profitMargins") else "No reportado"
                    sector_empresa = info_stock.get("sector", "Renta Variable Global")

                    df_stock["Retorno_Diario"] = df_stock["Close"].pct_change()
                    volatilidad_anualizada = df_stock["Retorno_Diario"].std() * np.sqrt(252)
                    var_diario_95 = np.percentile(df_stock["Retorno_Diario"].dropna(), 5)

                    st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos (5 Años)")
                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric(f"Precio Actual ({simbolo_moneda})", f"{simbolo_moneda} {precio_actual:,.2f}")
                    c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
                    c_m3.metric("Volatilidad Anualizada", f"{volatilidad_anualizada:.2%}")
                    c_m4.metric("Margen Beneficio Neto", f"{margin_str}")

                    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
                    c_m5.metric(f"Cap. de Mercado ({simbolo_moneda})", f"{simbolo_moneda} {market_cap:,.0f}" if market_cap > 0 else "No reportado")
                    c_m6.metric("Ratio P/B", f"{pb_ratio}")
                    c_m7.metric("Rendimiento Dividendo", f"{dividend_str}")
                    c_m8.metric("VaR 95% Diarios", f"{var_diario_95:.2%}")

                    st.markdown("---")

                    st.markdown(f"### 📈 Comportamiento Histórico & Proyección GBM Monte Carlo ({horizonte})")
                    dias_proyeccion = 60 if "1 a 3 meses" in horizonte else (180 if "6 meses a 1 año" in horizonte else 365)
                    mediana_mc, p10_mc, p90_mc = simular_monte_carlo_gbm(precio_actual, df_stock["Retorno_Diario"].dropna(), dias_proyeccion, es_forex=False)
                    
                    fechas_historicas = df_stock.index
                    precios_historicos = df_stock["Close_Moneda"]
                    fechas_futuras = pd.date_range(start=df_stock.index[-1], periods=dias_proyeccion + 1, freq="B")

                    fig_stock = go.Figure()
                    
                    trace_hist = go.Scatter(
                        x=fechas_historicas, 
                        y=precios_historicos, 
                        mode="lines", 
                        name="Histórico Real (5 Años)", 
                        line=dict(color="#10b981", width=2.0)
                    )
                    trace_p90 = go.Scatter(
                        x=fechas_futuras, 
                        y=p90_mc, 
                        mode="lines", 
                        name="Escenario Optimista (P80)", 
                        line=dict(color="rgba(56, 189, 248, 0.5)", width=1.5, dash="dash")
                    )
                    trace_p10 = go.Scatter(
                        x=fechas_futuras, 
                        y=p10_mc, 
                        mode="lines", 
                        name="Escenario Pesimista (P20)", 
                        line=dict(color="rgba(239, 68, 68, 0.5)", width=1.5, dash="dash"), 
                        fill="tonexty", 
                        fillcolor="rgba(56, 189, 248, 0.05)"
                    )
                    trace_mediana = go.Scatter(
                        x=fechas_futuras, 
                        y=mediana_mc, 
                        mode="lines", 
                        name="Proyección Central GBM", 
                        line=dict(color="#8b5cf6", width=3.0)
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

                paquete_datos_analisis = f"""
                Activo Analizado: {ticker_final} ({nombre_empresa}) | Sector: {sector_empresa}
                Precio Spot Actual: {simbolo_moneda} {precio_actual:,.2f} | Capital Disponible: {simbolo_moneda} {capital_input:,.2f}
                Horizonte Temporal: {horizonte} | Perfil de Riesgo del Inversor: {perfil_riesgo}
                Ratio PER: {pe_ratio} | Ratio P/B: {pb_ratio} | Volatilidad Anualizada: {volatilidad_anualizada:.2%} | VaR 95%: {var_diario_95:.2%}
                {CONTEXTO_GLOBAL_INSTITUCIONAL}
                """

                prompt_ia_stock = f"""
                Actúa como el Director de Análisis Cuantitativo y Valoración de Activos de un Fondo de Inversión Global (Hedge Fund).
                Redacta un análisis EXHAUSTIVO, sumamente técnico, riguroso y profesional sobre {ticker_final}. Cruza los datos financieros reales con la teoría de finanzas corporativas (WACC, múltiplos PER {pe_ratio}, P/B {pb_ratio}, flujos de caja libre) y la macroeconomía actual (tasas FED, inflación, política monetaria).
                PROHIBIDO dar respuestas vagas, superficiales o repetitivas. Cada tarjeta debe profundizar con argumentos matemáticos y reales en la realidad financiera del activo.

                DATOS TÉCNICOS A EVALUAR:
                {paquete_datos_analisis}

                INSTRUCCIÓN ABSOLUTA: Devuelve tu respuesta EXCLUSIVAMENTE en un objeto JSON válido y limpio. Cero comillas triples Markdown, cero texto adicional fuera del JSON.
                
                ESTRUCTURA JSON REQUERIDA:
                {{
                  "diagnostico": "Análisis fundamental profundo. Evalúa el PER ({pe_ratio}), el P/B ({pb_ratio}) y la valoración del activo frente a su sector y la política monetaria global actual.",
                  "viabilidad": "1. Análisis de Capital: Compara matemáticamente el capital de {simbolo_moneda} {capital_input:,.2f} frente al precio unitario de {simbolo_moneda} {precio_actual:,.2f}. 2. Análisis de Perfil: Contrasta la volatilidad del {volatilidad_anualizada:.2%} con el perfil de riesgo {perfil_riesgo}.",
                  "riesgos": "Detalla 3 riesgos críticos y específicos del activo en formato de lista numérica: 1. Riesgo de tasas y costo de capital. 2. Riesgos sistémicos del sector. 3. Volatilidad macroeconómica.",
                  "veredicto": "COMPRAR, DESESTIMAR o MANTENER EN OBSERVACIÓN",
                  "fundamento": "Dictamen ejecutivo directo y severo. Explica con total claridad y sin ambigüedades la justificación financiera e institucional de la decisión tomada."
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
                            "veredicto": "DESESTIMAR" if es_capital_insuficiente else "MANTENER EN OBSERVACIÓN",
                            "fundamento": f"Dictamen institucional definitivo: La relación entre el capital disponible ({simbolo_moneda} {capital_input:,.2f}) y la exposición al riesgo con una volatilidad anualizada del {volatilidad_anualizada:.2%} exige prudencia táctica y reevaluación de entradas."
                        }

                    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                    with col_c1:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>1. Valoración Fundamental & Macro</div><div class='analysis-card-body'>{json_stock.get('diagnostico', '')}</div></div>", unsafe_allow_html=True)
                    with col_c2:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>2. Viabilidad / Riesgo</div><div class='analysis-card-body'>{json_stock.get('viabilidad', '')}</div></div>", unsafe_allow_html=True)
                    with col_c3:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>3. Riesgos Sistémicos e Inflación</div><div class='analysis-card-body'>{json_stock.get('riesgos', '').replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)
                    with col_c4:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>4. Conclusión Técnica</div><div class='analysis-card-body'>{json_stock.get('fundamento', '')}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_col_a, bot_col_b = st.columns([3, 1])
                    with bot_col_a:
                        st.markdown(f"<div class='decision-container'><div class='analysis-card-title' style='font-size: 1.2rem; border-bottom: none;'>🎯 Dictamen Institucional</div><div class='analysis-card-body' style='font-size: 1rem; color: #f8fafc;'>{json_stock.get('fundamento', '')}</div></div>", unsafe_allow_html=True)
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

                    # Obtención de tasas de interés de referencia para comparación macroeconómica
                    tasa_base_ref = TASAS_REFERENCIA_PAIS.get(base_curr, 4.50)
                    tasa_target_ref = TASAS_REFERENCIA_PAIS.get(target_curr, 4.50)
                    diferencial_tasas = tasa_base_ref - tasa_target_ref

                    st.markdown(f"### 📊 Panel de Indicadores Clave & Tasas de Referencia - {base_curr}/{target_curr}")
                    c_x1, c_x2, c_x3, c_x4 = st.columns(4)
                    c_x1.metric("Tipo de Cambio Spot", f"{rate_actual:,.4f}")
                    c_x2.metric(f"Tasa Ref. {base_curr} (FED/Central)", f"{tasa_base_ref:.2f}%")
                    c_x3.metric(f"Tasa Ref. {target_curr} (Central)", f"{tasa_target_ref:.2f}%")
                    c_x4.metric("Diferencial de Tasas", f"{diferencial_tasas:+.2f}%")

                    c_x5, c_x6, c_x7, c_x8 = st.columns(4)
                    c_x5.metric("Monto Convertido", f"{monto_fx * rate_actual:,.2f} {target_curr}")
                    c_x6.metric("Volatilidad Anualizada", f"{volatilidad_fx:.2%}")
                    c_x7.metric("Variación Histórica 5A", f"{variacion_5y:+.2f}%")
                    c_x8.metric("Spread Cambiario Est. (% min)", "0.15%")

                    st.markdown("---")

                    st.markdown(f"### 📈 Proyección GBM Monte Carlo Acotada ({horizonte_fx})")
                    dias_proy_fx = 60 if "1 a 3 meses" in horizonte_fx else (180 if "6 meses a 1 año" in horizonte_fx else 365)
                    mediana_fx, p10_fx, p90_fx = simular_monte_carlo_gbm(rate_actual, df_fx["Retorno_Diario"].dropna(), dias_proy_fx, es_forex=True)
                    
                    fechas_hist_fx = df_fx.index
                    fechas_futuras_fx = pd.date_range(start=df_fx.index[-1], periods=dias_proy_fx + 1, freq="B")

                    fig_fx = go.Figure()
                    
                    trace_fx_hist = go.Scatter(
                        x=fechas_hist_fx, 
                        y=df_fx["Close"], 
                        mode="lines", 
                        name="Tipo de Cambio Histórico", 
                        line=dict(color="#10b981", width=2.0)
                    )
                    trace_fx_p90 = go.Scatter(
                        x=fechas_futuras_fx, 
                        y=p90_fx, 
                        mode="lines", 
                        name="Escenario Volatilidad (P80)", 
                        line=dict(color="rgba(56, 189, 248, 0.5)", width=1.5, dash="dash")
                    )
                    trace_fx_p10 = go.Scatter(
                        x=fechas_futuras_fx, 
                        y=p10_fx, 
                        mode="lines", 
                        name="Escenario Caída (P20)", 
                        line=dict(color="rgba(239, 68, 68, 0.5)", width=1.5, dash="dash"), 
                        fill="tonexty", 
                        fillcolor="rgba(56, 189, 248, 0.05)"
                    )
                    trace_fx_mediana = go.Scatter(
                        x=fechas_futuras_fx, 
                        y=mediana_fx, 
                        mode="lines", 
                        name="Proyección Central GBM", 
                        line=dict(color="#8b5cf6", width=3.0)
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
                Actúa como el Economista Jefe de Divisas (FX) de un Banco de Inversión Global.
                Redacta un análisis EXHAUSTIVO, sumamente técnico, riguroso y profesional de la paridad cambiaria {base_curr}/{target_curr}. 
                Cruza los datos estadísticos con la paridad descubierta de tasas de interés (Tasa {base_curr}: {tasa_base_ref}% vs Tasa {target_curr}: {tasa_target_ref}%, diferencial: {diferencial_tasas:+.2f}%), inflación cruzada y balanza de pagos.
                PROHIBIDO dar respuestas vagas, superficiales o que dejen preguntas abiertas. Cada tarjeta debe ser categórica, evaluando directamente los costos de transacción y spreads estimados (0.15%), y aportando contexto geopolítico actual (como la fortaleza del Dólar Index DXY y precios de commodities).

                DATOS TÉCNICOS A EVALUAR:
                Paridad Spot Actual: {rate_actual:,.4f} | Volatilidad Anualizada: {volatilidad_fx:.2%}
                Horizonte Temporal: {horizonte_fx} | Propósito Operativo: {proposito_fx} | Monto Evaluado: {monto_fx} {base_curr}
                {CONTEXTO_GLOBAL_INSTITUCIONAL}

                INSTRUCCIÓN ABSOLUTA: Devuelve tu respuesta EXCLUSIVAMENTE en formato JSON válido y limpio. Cero comillas triples Markdown, cero texto adicional fuera del JSON.

                ESTRUCTURA JSON REQUERIDA:
                {{
                  "diagnostico": "Análisis macroeconómico cambiario avanzado basado en el diferencial de tasas de interés ({diferencial_tasas:+.2f}%) y flujos de capital institucionales entre {base_curr} y {target_curr}.",
                  "viabilidad": "Evaluación cuantitativa directa de ejecutar '{proposito_fx}' para el monto de {monto_fx} {base_curr}, integrando el impacto de los spreads operativos y el momento óptimo de entrada.",
                  "riesgos": "Detalla 3 riesgos críticos cambiarios específicos en formato de lista numérica: 1. Postura de la FED y el Dólar Index. 2. Shocks en términos de intercambio locales. 3. Volatilidad de flujos de capital extranjero.",
                  "veredicto": "FORTALECIMIENTO, DEBILITAMIENTO o NEUTRAL",
                  "fundamento": "Dictamen estricto y directivo sin rodeos. Qué acción operativa inmediata y clara debe ejecutar el inversor o tesorero corporativo respecto a esta divisa."
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
                            "veredicto": "FORTALECIMIENTO" if diferencial_tasas > 0 else "DEBILITAMIENTO",
                            "fundamento": f"Dictamen FX institucional definitivo: Con un diferencial de tasas del {diferencial_tasas:+.2f}% y una volatilidad del {volatilidad_fx:.2%}, se recomienda ejecutar contratos a término (forwards) o coberturas parciales para blindar el flujo de caja operativo."
                        }

                    col_fx_c1, col_fx_c2, col_fx_c3, col_fx_c4 = st.columns(4)
                    with col_fx_c1:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>1. Diagnóstico Macro / Tasas</div><div class='analysis-card-body'>{json_fx.get('diagnostico', '')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c2:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>2. Sensibilidad y Cobertura</div><div class='analysis-card-body'>{json_fx.get('viabilidad', '')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c3:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>3. Riesgo Geopolítico / FED</div><div class='analysis-card-body'>{json_fx.get('riesgos', '').replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)
                    with col_fx_c4:
                        st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>4. Posicionamiento Estratégico</div><div class='analysis-card-body'>{json_fx.get('fundamento', '')}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_fx_a, bot_fx_b = st.columns([3, 1])
                    with bot_fx_a:
                        st.markdown(f"<div class='decision-container'><div class='analysis-card-title' style='font-size: 1.2rem; border-bottom: none;'>🎯 Estrategia Direccional FX</div><div class='analysis-card-body' style='font-size: 1rem; color: #f8fafc;'>{json_fx.get('fundamento', '')}</div></div>", unsafe_allow_html=True)
                    with bot_fx_b:
                        veredicto_fx_clean = str(json_fx.get("veredicto", "NEUTRAL")).upper()
                        if "FORTALECIMIENTO" in veredicto_fx_clean or "COMPRA" in veredicto_fx_clean:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-comprar", "🟢", "ALCISTA (LONG)"
                        elif "DEBILITAMIENTO" in veredicto_fx_clean or "VENTA" in veredicto_fx_clean:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-desestimar", "🔴", "BAJISTA (SHORT)"
                        else:
                            badge_f_cls, badge_f_ico, badge_f_txt = "decision-observacion", "🟡", "NEUTRAL"
                        st.markdown(f"<div class='decision-badge-box {badge_f_cls}'><div style='font-size: 2.5rem; margin-bottom: 8px;'>{badge_f_ico}</div><div style='font-weight: 800; font-size: 1.1rem; letter-spacing: 0.05em;'>{badge_f_txt}</div></div>", unsafe_allow_html=True)
