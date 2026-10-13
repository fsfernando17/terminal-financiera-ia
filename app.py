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
# CONFIGURACIÓN INICIAL DE LA PÁGINA FINTECH
# ==============================================================================
st.set_page_config(
    page_title="Terminal Inteligente de Inversiones & Forex",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS CSS HIGH-END INSTITUCIONAL (GLASSMORPHISM & DARK MODE)
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
        min-height: 270px;
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
        min-height: 150px;
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
# CONFIGURACIÓN DE CLIENTE GOOGLE GENAI
# ==============================================================================
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None

def limpiar_texto_markdown(texto):
    if not texto: return ""
    return str(texto).replace("`", "").strip()

def parse_json_respuesta(text):
    if not text: return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```[a-zA-Z]*\n', '', text)
        text = re.sub(r'\n```$', '', text)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try: return json.loads(match.group(0))
            except Exception: pass
    return None

def generar_respuesta_ia_robusta(client, prompt):
    modelos_validos = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
    config = types.GenerateContentConfig(temperature=0.2, max_output_tokens=3000)
    for modelo in modelos_validos:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt, config=config)
            if response and response.text: return response.text
        except Exception:
            continue
    return None

# ==============================================================================
# MOTOR ECONOMÉTRICO & MONTE CARLO GBM (RÉGIMEN AJUSTADO)
# ==============================================================================
def simular_monte_carlo_gbm(precio_inicial, retornos_diarios, dias_proy, num_simulaciones=500):
    # Uso de ventana deslizante para evitar volatilidad extrema de años pasados
    dias_historia = 90 if dias_proy <= 60 else (180 if dias_proy <= 180 else 252)
    retornos_recientes = retornos_diarios.tail(dias_historia) if len(retornos_diarios) > dias_historia else retornos_diarios
    
    mu_diario = retornos_recientes.mean()
    sigma_diario = retornos_recientes.std()
    
    drift = mu_diario - 0.5 * (sigma_diario ** 2)
    matriz_precios = np.zeros((dias_proy + 1, num_simulaciones))
    matriz_precios[0] = precio_inicial
    
    choques = np.random.normal(0, 1, (dias_proy, num_simulaciones))
    retornos_simulados = np.exp(drift + sigma_diario * choques)
    
    for t in range(1, dias_proy + 1):
        matriz_precios[t] = matriz_precios[t - 1] * retornos_simulados[t - 1]
        
    mediana = np.median(matriz_precios, axis=1)
    percentil_10 = np.percentile(matriz_precios, 10, axis=1)
    percentil_90 = np.percentile(matriz_precios, 90, axis=1)
    
    return mediana, percentil_10, percentil_90

# ==============================================================================
# DICCIONARIOS Y MAPAS DE MERCADO
# ==============================================================================
DIVISAS = {
    "USD": "Dólar Estadounidense (USD)", "PEN": "Sol Peruano (PEN)", "EUR": "Euro (EUR)",
    "GBP": "Libra Esterlina (GBP)", "JPY": "Yen Japonés (JPY)", "MXN": "Peso Mexicano (MXN)",
    "CLP": "Peso Chileno (CLP)", "COP": "Peso Colombiano (COP)", "BRL": "Real Brasileño (BRL)"
}
TICKER_MAP = {"SPCCPI1.LM": "SCCO", "SPCCPI2.LM": "SCCO"}
TASAS_CAMBIO_USD = {"USD ($)": 1.0, "PEN (S/.)": 3.75, "CLP ($)": 950.0, "BRL (R$)": 5.50, "MXN ($)": 19.50}
SIMBOLOS_MONEDA = {"USD ($)": "$", "PEN (S/.)": "S/.", "CLP ($)": "$ CLP", "BRL (R$)": "R$", "MXN ($)": "$ MXN"}
MINIMOS_MONEDA = {"USD ($)": 20.0, "PEN (S/.)": 75.0, "CLP ($)": 19000.0, "BRL (R$)": 110.0, "MXN ($)": 390.0}

MERCADOS = {
    "NYSE / NASDAQ (Estados Unidos)": {"AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "MSFT": "Microsoft Corp.", "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com Inc.", "GOOGL": "Alphabet Inc.", "SCCO": "Southern Copper Corp.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"},
    "Bolsa de Valores de Lima (BVL - Perú)": {"SPCCPI1.LM": "Southern Copper Corp. (BVL)", "BAP": "Credicorp Ltd.", "IFS": "Intercorp Financial Services", "CPACEN1.LM": "Cementos Pacasmayo", "ALICORC1.LM": "Alicorp S.A.A.", "🔍 Buscar otro Ticker manualmente": "CUSTOM"}
}

CONTEXTO_GLOBAL_AMPLIO = """
[CONTEXTO MACROECONÓMICO INSTITUCIONAL 2026]: 
1. Política Monetaria Global: La Reserva Federal (FED) y el Banco Central Europeo (BCE) calibran sus tasas de interés reales frente a una inflación persistente y datos de empleo mixtos. El Banco Central de Reserva del Perú (BCRP) mantiene estabilidad monetaria con un enfoque estricto en la tasa de referencia.
2. Finanzas Corporativas y Valoración: Los mercados exigen tasas de descuento ajustadas al riesgo (WACC elevados) y análisis rigurosos de VAN y TIR para proyectos de inversión y asignación de capital. Los ratios PER y P/B se evalúan frente al ciclo histórico de beneficios por acción (EPS).
3. Geopolítica y Commodities: La volatilidad en los precios de las materias primas (cobre, oro, petróleo WTI) impacta directamente en las economías emergentes y divisas de la región. El Banco Mundial y el FMI alertan sobre primas de riesgo soberano y corporativo en contextos de alta tensión internacional.
"""

def obtener_factor_conversion(moneda_base_asset, moneda_destino_key):
    tasa_destino = TASAS_CAMBIO_USD[moneda_destino_key]
    base_upper = str(moneda_base_asset).upper()
    if "PEN" in base_upper or "SOL" in base_upper: tasa_base_usd = TASAS_CAMBIO_USD["PEN (S/.)"]
    elif "BRL" in base_upper: tasa_base_usd = TASAS_CAMBIO_USD["BRL (R$)"]
    elif "CLP" in base_upper: tasa_base_usd = TASAS_CAMBIO_USD["CLP ($)"]
    elif "MXN" in base_upper: tasa_base_usd = TASAS_CAMBIO_USD["MXN ($)"]
    else: tasa_base_usd = 1.0
    return (1.0 / tasa_base_usd) * tasa_destino

def obtener_historial_forex(base_curr, target_curr):
    try:
        if base_curr == target_curr:
            dates = pd.date_range(end=pd.Timestamp.now(), periods=1260, freq="B")
            return pd.DataFrame({"Close": 1.0}, index=dates)
        ticker_direct = f"{base_curr}{target_curr}=X"
        df = yf.Ticker(ticker_direct).history(period="5y")
        if not df.empty and len(df) > 10: return df[["Close"]]
        ticker_inverse = f"{target_curr}{base_curr}=X"
        df_inv = yf.Ticker(ticker_inverse).history(period="5y")
        if not df_inv.empty and len(df_inv) > 10:
            df_inv["Close"] = 1.0 / df_inv["Close"]
            return df_inv[["Close"]]
        df_base = yf.Ticker(f"{base_curr}USD=X").history(period="5y") if base_curr != "USD" else None
        df_target = yf.Ticker(f"{target_curr}USD=X").history(period="5y") if target_curr != "USD" else None
        if base_curr == "USD" and df_target is not None:
            df_res = pd.DataFrame(index=df_target.index)
            df_res["Close"] = 1.0 / df_target["Close"]
            return df_res
        elif target_curr == "USD" and df_base is not None:
            df_res = pd.DataFrame(index=df_base.index)
            df_res["Close"] = df_base["Close"]
            return df_res
        elif df_base is not None and df_target is not None:
            df_comb = pd.concat([df_base["Close"], df_target["Close"]], axis=1, keys=["b", "t"]).dropna()
            df_res = pd.DataFrame(index=df_comb.index)
            df_res["Close"] = df_comb["b"] / df_comb["t"]
            return df_res
    except Exception: pass
    return pd.DataFrame()


# ==============================================================================
# ENCABEZADO Y TABS DE LA TERMINAL
# ==============================================================================
st.title("📈 Terminal Inteligente de Inversiones & Forex")
st.markdown("<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 20px;'>Plataforma cuantitativa, econométrica y analítica de grado institucional.</p>", unsafe_allow_html=True)

tab_acciones, tab_forex = st.tabs(["📊 Análisis Accionario", "🔀 Comparativa de Divisas (Forex)"])

# ==============================================================================
# PESTAÑA 1: ANÁLISIS ACCIONARIO
# ==============================================================================
with tab_acciones:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Inversión Accionaria")
        col1, col2, col3 = st.columns(3)
        with col1: mercado_sel = st.selectbox("🌍 Mercado de Origen:", list(MERCADOS.keys()), key="stock_mercado")
        dic_acciones = MERCADOS[mercado_sel]
        with col2:
            opcion_accion = st.selectbox("📊 Selección de Acción / Ticker:", list(dic_acciones.keys()), format_func=lambda x: f"{x} - {dic_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir Ticker'}", key="stock_accion")
            if opcion_accion == "🔍 Buscar otro Ticker manualmente":
                ticker_final = st.text_input("Ingrese Ticker (ej: AMD, MELI):", value="AAPL", key="stock_ticker_manual").upper()
                nombre_empresa = ticker_final
            else:
                ticker_final = opcion_accion
                nombre_empresa = dic_acciones[opcion_accion]
        with col3: moneda_sel = st.selectbox("💵 Moneda de Operación:", list(TASAS_CAMBIO_USD.keys()), key="stock_moneda")

        simb = SIMBOLOS_MONEDA[moneda_sel]
        monto_min = MINIMOS_MONEDA[moneda_sel]
        col4, col5, col6 = st.columns(3)
        with col4: capital_input = st.number_input(f"💰 Capital Disponible ({simb}):", min_value=monto_min, value=monto_min * 10, step=monto_min, key="stock_capital")
        with col5: horizonte = st.selectbox("⏱️ Horizonte Temporal:", ["Corto Plazo (1 a 3 meses)", "Mediano Plazo (6 meses a 1 año)", "Largo Plazo (1 año a más)"], key="stock_horizonte")
        with col6: perfil_riesgo = st.selectbox("🛡️ Perfil del Inversor:", ["Conservador", "Moderado", "Agresivo"], key="stock_perfil")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Multidimensional Accionario", use_container_width=True, key="btn_stock"):
        if not api_key_oculta or not client:
            st.error("⚠️ Falta GEMINI_API_KEY en los Secrets.")
        else:
            datos_cargados = False
            try:
                search_ticker = TICKER_MAP.get(ticker_final, ticker_final)
                stock = yf.Ticker(search_ticker)
                df = stock.history(period="5y")
                
                if df.empty and search_ticker.endswith(".LM"):
                    stock = yf.Ticker(search_ticker.replace(".LM", ""))
                    df = stock.history(period="5y")
                
                if df.empty:
                    st.error(f"⚠️ Ticker '{ticker_final}' no encontrado en Yahoo Finance.")
                else:
                    datos_cargados = True
                    try: info = stock.info
                    except: info = {}
                        
                    currency_base = info.get("currency", "USD")
                    factor_conv = obtener_factor_conversion(currency_base, moneda_sel)

                    precio_actual = df["Close"].iloc[-1] * factor_conv
                    df["Close_Moneda"] = df["Close"] * factor_conv
                    
                    market_cap = info.get("marketCap", 0) * factor_conv
                    pe_ratio = f"{info.get('trailingPE'):.2f}" if info.get("trailingPE") else "Evaluación Cualitativa"
                    pb_ratio = f"{info.get('priceToBook'):.2f}" if info.get("priceToBook") else "Evaluación Cualitativa"
                    dividend_str = f"{info.get('dividendYield', 0)*100:.2f}%" if info.get("dividendYield") else "0.00%"
                    margin_str = f"{info.get('profitMargins', 0)*100:.2f}%" if info.get("profitMargins") else "Sector Promedio"
                    sector = info.get("sector", "Sector Corporativo General")

                    df["Retorno_Diario"] = df["Close"].pct_change()
                    volatilidad_anual = df["Retorno_Diario"].std() * np.sqrt(252)
                    var_95 = np.percentile(df["Retorno_Diario"].dropna(), 5)

                    st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos (5 Años)")
                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric(f"Precio Actual ({simb})", f"{simb} {precio_actual:,.2f}")
                    c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
                    c_m3.metric("Volatilidad Anualizada", f"{volatilidad_anual:.2%}")
                    c_m4.metric("Margen Beneficio Neto", f"{margin_str}")

                    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
                    c_m5.metric(f"Cap. de Mercado ({simb})", f"{simb} {market_cap:,.0f}" if market_cap else "Dato Proxy")
                    c_m6.metric("Ratio P/B", f"{pb_ratio}")
                    c_m7.metric("Rendimiento Dividendo", f"{dividend_str}")
                    c_m8.metric("VaR 95% Diarios", f"{var_95:.2%}")

                    st.markdown("---")

                    st.markdown(f"### 📈 Comportamiento Histórico & Proyección GBM Monte Carlo ({horizonte})")
                    dias_proy = 60 if "1 a 3 meses" in horizonte else (180 if "6 meses a 1 año" in horizonte else 365)
                    mediana, p10, p90 = simular_monte_carlo_gbm(precio_actual, df["Retorno_Diario"].dropna(), dias_proy)
                    
                    fechas_hist = df.index
                    precios_hist = df["Close_Moneda"]
                    fechas_futuras = pd.date_range(start=df.index[-1], periods=dias_proy + 1, freq="B")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=fechas_hist, y=precios_hist, mode="lines", name="Histórico Real (5 Años)", line=dict(color="#10b981", width=2.0)))
                    fig.add_trace(go.Scatter(x=fechas_futuras, y=p90, mode="lines", name="Escenario Optimista (P90)", line=dict(color="rgba(56, 189, 248, 0.5)", width=1.5, dash="dash")))
                    fig.add_trace(go.Scatter(x=fechas_futuras, y=p10, mode="lines", name="Escenario Pesimista (P10)", line=dict(color="rgba(239, 68, 68, 0.5)", dash="dash"), fill="tonexty", fillcolor="rgba(56, 189, 248, 0.05)"))
                    fig.add_trace(go.Scatter(x=fechas_futuras, y=mediana, mode="lines", name="Proyección Central GBM", line=dict(color="#8b5cf6", width=3.0)))

                    fig.update_layout(
                        xaxis=dict(title="Fecha", gridcolor="#1e293b", fixedrange=False),
                        yaxis=dict(title=f"Precio ({simb})", gridcolor="#1e293b", fixedrange=False, autorange=True),
                        template="plotly_dark", paper_bgcolor="#020617", plot_bgcolor="#020617",
                        height=550, dragmode="pan", hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.9)")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                    
                    st.markdown("""
                    <div class='disclaimer-box'>
                        <strong>⚠️ Aviso Legal y de Riesgo:</strong> Esta plataforma es una herramienta avanzada de análisis cuantitativo e inteligencia artificial. Las proyecciones estocásticas (Monte Carlo) y los dictámenes automatizados <strong>NO constituyen asesoramiento financiero garantizado ni recomendaciones formales de inversión</strong>. El rendimiento histórico no garantiza resultados futuros. El usuario asume total responsabilidad por las decisiones tomadas con capital real.<br><br>
                        <span style='color: #38bdf8;'>💡 <strong>Tip de Interfaz (Gráficos):</strong> Utiliza la rueda del ratón para hacer zoom. Haz clic sostenido y arrastra para moverte a lo largo del tiempo. Haz doble clic en el gráfico para resetear la vista original.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

            except Exception as e:
                st.error(f"Error procesando datos financieros: {str(e)}")

            if datos_cargados:
                st.markdown("## 📋 Dictamen Estratégico Cuantitativo Institucional")

                paquete_analisis = f"""
                Activo Analizado: {ticker_final} ({nombre_empresa}) | Sector: {sector}
                Precio Actual: {simb} {precio_actual:,.2f} | Capital Disponible: {simb} {capital_input:,.2f}
                Horizonte Temporal: {horizonte} | Perfil de Riesgo: {perfil_riesgo}
                Ratio PER: {pe_ratio} | Volatilidad Anualizada: {volatilidad_anual:.2%} | VaR 95%: {var_95:.2%}
                {CONTEXTO_GLOBAL_AMPLIO}
                """

                prompt_ia = f"""
                Actúa como el Director de Análisis Cuantitativo y Macroeconomía de un Fondo de Inversión Global.
                Tu tarea es realizar un análisis EXHAUSTIVO, profundo, técnico y certero. Debes cruzar la información del activo con la teoría corporativa (valoración por múltiplos PER/PB, flujos descontados, VAN y TIR implícita), la econometría de la serie y el contexto macroeconómico global (FED, BCRP, Banco Mundial, geopolítica). No des respuestas evasivas ni cortas; redacta con alto nivel técnico y rigor financiero.

                DATOS A EVALUAR:
                {paquete_analisis}

                INSTRUCCIÓN ABSOLUTA: Devuelve tu respuesta EXCLUSIVAMENTE en formato JSON válido, sin comillas triples Markdown, sin texto adicional fuera del JSON.
                
                ESTRUCTURA JSON REQUERIDA:
                {{
                  "diagnostico": "Análisis fundamental y macroeconómico denso. Evalúa el PER, la posición de mercado de {nombre_empresa} dentro del sector {sector}, y cómo las tasas de interés globales y la política del BCRP/FED afectan su valoración actual.",
                  "viabilidad": "1. Análisis de Capital: Evalúa si el capital disponible de {simb} {capital_input:,.2f} es suficiente para adquirir al menos 1 acción entera valorizada en {simb} {precio_actual:,.2f}. 2. Análisis de Riesgo/Perfil: Explica si la volatilidad anualizada del {volatilidad_anual:.2%} es compatible con el perfil {perfil_riesgo}.",
                  "riesgos": "Detalla 3 riesgos críticos y sistémicos en formato numerado: 1. Riesgo de tasas de interés y costo de capital. 2. Riesgos geopolíticos y supply chain. 3. Riesgos idiosincráticos del sector.",
                  "veredicto": "COMPRAR, DESESTIMAR o MANTENER EN OBSERVACIÓN",
                  "fundamento": "Dictamen ejecutivo y severo. Si se desestima, especifica con claridad si fue por insuficiencia de capital o por exceso de volatilidad frente al perfil conservador/moderado/agresivo."
                }}
                """

                with st.spinner("🤖 El motor de Inteligencia Institucional está cruzando la macroeconomía global y la econometría..."):
                    raw_response = generar_respuesta_ia_robusta(client, prompt_ia)
                    data_json = parse_json_respuesta(raw_response)

                    if not data_json:
                        # Fallback robusto con lógica separada de capital vs volatilidad
                        es_insuficiente = capital_input < precio_actual
                        veredicto_fb = "DESESTIMAR" if es_insuficiente else "MANTENER EN OBSERVACIÓN"
                        motivo_fb = f"El capital disponible de {simb} {capital_input:,.2f} no cubre la acción a {simb} {precio_actual:,.2f}." if es_insuficiente else "Se sugiere cautela por alta volatilidad sectorial."
                        
                        data_json = {
                            "diagnostico": f"Análisis basado en la cotización de {ticker_final} a {simb} {precio_actual:,.2f} y su volatilidad histórica del {volatilidad_anual:.2%}.",
                            "viabilidad": f"Verificación de capital: {'Insuficiente' if es_insuficiente else 'Suficiente'} frente al costo unitario del activo.",
                           "riesgos": "1. Riesgo de mercado sistémico y volatilidad por tasas de la FED.\n2. Presiones inflacionarias globales.\n3. Liquidez y profundidad de mercado.",
                            "veredicto": veredicto_fb,
                            "fundamento": motivo_fb
                        }

                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>1. Valoración Fundamental & Macro</div><div class='analysis-card-body'>{data_json.get('diagnostico', '')}</div></div>", unsafe_allow_html=True)
                    with col2: st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>2. Viabilidad / Riesgo</div><div class='analysis-card-body'>{data_json.get('viabilidad', '')}</div></div>", unsafe_allow_html=True)
                    with col3: st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>3. Riesgos Sistémicos e Inflación</div><div class='analysis-card-body'>{data_json.get('riesgos', '').replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)
                    with col4: st.markdown(f"<div class='analysis-card'><div class='analysis-card-title'>4. Conclusión Técnica</div><div class='analysis-card-body'>{data_json.get('fundamento', '')}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_col1, bot_col2 = st.columns([3, 1])
                    with bot_col1: st.markdown(f"<div class='decision-container'><div class='analysis-card-title' style='font-size: 1.2rem; border-bottom: none;'>🎯 Dictamen Institucional</div><div class='analysis-card-body' style='font-size: 1rem; color: #f8fafc;'>{data_json.get('fundamento', '')}</div></div>", unsafe_allow_html=True)
                    with bot_col2:
                        veredicto_clean = str(data_json.get("veredicto", "MANTENER EN OBSERVACIÓN")).upper()
                        if "COMPRAR" in veredicto_clean and "DESESTIMAR" not in veredicto_clean: badge_class, badge_icon, badge_text = "decision-comprar", "🟢", "COMPRAR"
                        elif "DESESTIMAR" in veredicto_clean: badge_class, badge_icon, badge_text = "decision-desestimar", "🔴", "DESESTIMAR"
                        else: badge_class, badge_icon, badge_text = "decision-observacion", "🟡", "EN OBSERVACIÓN"
                        st.markdown(f"<div class='decision-badge-box {badge_class}'><div style='font-size: 2.5rem; margin-bottom: 8px;'>{badge_icon}</div><div style='font-weight: 800; font-size: 1.1rem; letter-spacing: 0.05em;'>{badge_text}</div></div>", unsafe_allow_html=True)


# ==============================================================================
# PESTAÑA 2: COMPARATIVA DE DIVISAS (FOREX)
# ==============================================================================
with tab_forex:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Evaluación Cambiaria")
        col_fx1, col_fx2, col_fx3 = st.columns(3)
        with col_fx1: base_curr = st.selectbox("🔀 Moneda de Origen (Base):", list(DIVISAS.keys()), index=0, format_func=lambda x: DIVISAS[x], key="fx_base")
        with col_fx2: target_curr = st.selectbox("🎯 Moneda Destino (Objetivo):", list(DIVISAS.keys()), index=1, format_func=lambda x: DIVISAS[x], key="fx_target")
        with col_fx3: monto_fx = st.number_input(f"💰 Monto de Conversión ({base_curr}):", min_value=1.0, value=1000.0, step=100.0, key="fx_monto")
        col_fx4, col_fx5 = st.columns(2)
        with col_fx4: horizonte_fx = st.selectbox("⏱️ Horizonte Temporal:", ["Corto Plazo (1 a 3 meses)", "Mediano Plazo (6 meses a 1 año)", "Largo Plazo (1 año a más)"], key="fx_horizonte")
        with col_fx5: proposito_fx = st.selectbox("🎯 Propósito de la Evaluación:", ["Cobertura de Riesgo Cambiario (Hedging)", "Operación de Comercio Exterior", "Inversión Especulativa", "Ahorro / Reserva de Valor"], key="fx_proposito")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Cuantitativo de Divisas", use_container_width=True, key="btn_forex"):
        if not api_key_oculta or not client:
            st.error("⚠️ Falta GEMINI_API_KEY en los Secrets.")
        else:
            datos_fx_cargados = False
            try:
                df_fx = obtener_historial_forex(base_curr, target_curr)
                if df_fx.empty:
                    st.error(f"⚠️ Historial de {base_curr}/{target_curr} no encontrado.")
                else:
                    datos_fx_cargados = True
                    rate_actual = df_fx["Close"].iloc[-1]
                    df_fx["Retorno_Diario"] = df_fx["Close"].pct_change()
                    volatilidad_anual = df_fx["Retorno_Diario"].std() * np.sqrt(252)
                    var_5y_pct = ((rate_actual - df_fx["Close"].iloc[0]) / df_fx["Close"].iloc[0]) * 100

                    st.markdown(f"### 📊 Panel de Indicadores Clave - {base_curr}/{target_curr}")
                    c_fx1, c_fx2, c_fx3, c_fx4 = st.columns(4)
                    c_fx1.metric("Tipo de Cambio Actual", f"{rate_actual:,.4f}")
                    c_fx2.metric("Monto Convertido", f"{monto_fx * rate_actual:,.2f} {target_curr}")
                    c_fx3.metric("Volatilidad Anualizada", f"{volatilidad_anual:.2%}")
                    c_fx4.metric("Variación Histórica 5A", f"{var_5y_pct:+.2f}%")
                    st.markdown("---")

                    st.markdown(f"### 📈 Proyección GBM Monte Carlo ({horizonte_fx})")
                    dias_proy = 60 if "1 a 3 meses" in horizonte_fx else (180 if "6 meses a 1 año" in horizonte_fx else 365)
                    mediana_fx, p10_fx, p90_fx = simular_monte_carlo_gbm(rate_actual, df_fx["Retorno_Diario"].dropna(), dias_proy)
                    
                    fechas_hist = df_fx.index
                    fechas_futuras = pd.date_range(start=df_fx.index[-1], periods=dias_proy + 1, freq="B")

                    fig_fx = go.Figure()
                    fig_fx.add_trace(go.Scatter(x=fechas_hist, y=df_fx["Close"], mode="lines", name="Tipo de Cambio Histórico", line=dict(color="#10b981", width=2.0)))
                    fig_fx.add_trace(go.Scatter(x=fechas_futuras, y=p90_fx, mode="lines", name="Escenario Vol
