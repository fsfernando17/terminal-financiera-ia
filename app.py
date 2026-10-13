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

# --- CONFIGURACIÓN DE PÁGINA FINTECH PROFESIONAL ---
st.set_page_config(
    page_title="Terminal Inteligente de Inversiones & Forex",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS CSS HIGH-END (MINIMALISTA, TOP FINTECH TERMINAL, GLASSMORPHISM)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Estilo General Dark Mode */
    .stApp {
        background-color: #070a11;
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Eliminar sombreados y cajas grises no deseadas en textos/códigos */
    code {
        background-color: transparent !important;
        color: #38bdf8 !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* Contraste en etiquetas de formulario */
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stWidgetLabel p {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.01em;
    }
    
    /* Cajas de entrada e inputs */
    div[data-baseweb="select"] > div, input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div:hover, input:focus {
        border-color: #38bdf8 !important;
    }

    /* Tabs Personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
    }

    /* Tarjetas de Métricas KPIs */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.85rem !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 1.45rem !important; font-weight: 700; }

    /* Botón Principal Estilo Neón */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1rem;
        border-radius: 12px;
        border: none;
        padding: 16px 32px;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        box-shadow: 0 6px 28px rgba(16, 185, 129, 0.55);
        transform: translateY(-1px);
    }

    /* TARJETAS DEL DICTAMEN DE ANÁLISIS (GLASSMORPHISM) */
    .analysis-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.55) 100%);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 14px;
        padding: 22px;
        height: 100%;
        min-height: 220px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .analysis-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 12px 35px -10px rgba(56, 189, 248, 0.15);
        transform: translateY(-2px);
    }
    .analysis-card-title {
        color: #38bdf8;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .analysis-card-body {
        color: #e2e8f0;
        font-size: 0.92rem;
        line-height: 1.65;
    }

    /* BLOQUE INFERIOR DE DECISIÓN Y BADGE */
    .decision-container {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .decision-badge-box {
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 150px;
        transition: all 0.3s ease;
    }

    .decision-comprar {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.35) 100%);
        border: 2px solid #10b981;
        color: #34d399;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.25);
    }

    .decision-desestimar {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.35) 100%);
        border: 2px solid #ef4444;
        color: #f87171;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.25);
    }

    .decision-observacion {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.35) 100%);
        border: 2px solid #f59e0b;
        color: #fbbf24;
        box-shadow: 0 0 30px rgba(245, 158, 11, 0.25);
    }

    /* Descargo Legal */
    .disclaimer-box {
        background-color: rgba(23, 18, 10, 0.8);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        color: #f3f4f6;
        padding: 16px 20px;
        font-size: 0.88rem;
        margin-top: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Carga transparente de la API Key
api_key_oculta = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key_oculta) if api_key_oculta else None


def limpiar_texto_markdown(texto):
    if not texto:
        return ""
    texto = str(texto).replace("`", "")
    return texto.strip()


# MODELOS OFICIALES DE GOOGLE AI STUDIO
def generar_respuesta_ia_rapida(client, prompt):
    modelos_validos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
    
    config = types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=500,
        response_mime_type="application/json"
    )

    for modelo in modelos_validos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text
        except Exception:
            continue

    return None


def parse_json_respuesta(text):
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return None


# --- DICCIONARIOS Y CONFIGURACIONES ---
DIVISAS = {
    "USD": "Dólar Estadounidense (USD)",
    "PEN": "Sol Peruano (PEN)",
    "EUR": "Euro (EUR)",
    "GBP": "Libra Esterlina (GBP)",
    "JPY": "Yen Japonés (JPY)",
    "MXN": "Peso Mexicano (MXN)",
    "CLP": "Peso Chileno (CLP)",
    "COP": "Peso Colombiano (COP)",
    "BRL": "Real Brasileño (BRL)",
    "CAD": "Dólar Canadiense (CAD)",
    "CNY": "Yuan Chino (CNY)",
    "KRW": "Won Surcoreano (KRW)",
    "AED": "Dirham de EAU (AED)"
}

TICKER_MAP = {
    "SPCCPI1.LM": "SCCO",
    "SPCCPI2.LM": "SCCO",
}

TASAS_CAMBIO_USD = {
    "USD ($)": 1.0,
    "PEN (S/.)": 3.75,
    "CLP ($)": 950.0,
    "BRL (R$)": 5.50,
    "MXN ($)": 19.50,
}

SIMBOLOS_MONEDA = {
    "USD ($)": "$",
    "PEN (S/.)": "S/.",
    "CLP ($)": "$ CLP",
    "BRL (R$)": "R$",
    "MXN ($)": "$ MXN",
}

MINIMOS_MONEDA = {
    "USD ($)": 20.0,
    "PEN (S/.)": 75.0,
    "CLP ($)": 19000.0,
    "BRL (R$)": 110.0,
    "MXN ($)": 390.0,
}

MERCADOS = {
    "NYSE / NASDAQ (Estados Unidos)": {
        "AAPL": "Apple Inc.",
        "TSLA": "Tesla Inc.",
        "MSFT": "Microsoft Corp.",
        "NVDA": "NVIDIA Corp.",
        "AMZN": "Amazon.com Inc.",
        "GOOGL": "Alphabet Inc.",
        "META": "Meta Platforms",
        "NFLX": "Netflix Inc.",
        "AMD": "Advanced Micro Devices",
        "INTC": "Intel Corp.",
        "SCCO": "Southern Copper Corp. (NYSE - USD)",
        "🔍 Buscar otro Ticker manualmente": "CUSTOM",
    },
    "Bolsa de Valores de Lima (BVL - Perú)": {
        "SPCCPI1.LM": "Southern Copper Corp. (Acc. Inversión BVL - PEN)",
        "SCCO": "Southern Copper Corp. (NYSE / BVL - USD)",
        "BAP": "Credicorp Ltd. (USD)",
        "IFS": "Intercorp Financial Services (USD)",
        "BVN": "Compañía de Minas Buenaventura (USD)",
        "CPACEN1.LM": "Cementos Pacasmayo (PEN)",
        "VOLCABC1.LM": "Volcan Compañía Minera (PEN)",
        "ALICORC1.LM": "Alicorp S.A.A. (PEN)",
        "FERREYC1.LM": "Ferreycorp S.A.A. (PEN)",
        "🔍 Buscar otro Ticker manualmente": "CUSTOM",
    },
    "B3 (Bolsa de Brasil)": {
        "PETR4.SA": "Petrobras (BRL)",
        "VALE3.SA": "Vale S.A. (BRL)",
        "ITUB4.SA": "Itaú Unibanco (BRL)",
        "BBDC4.SA": "Banco Bradesco (BRL)",
        "ABEV3.SA": "Ambev S.A. (BRL)",
        "WEGE3.SA": "WEG S.A. (BRL)",
        "🔍 Buscar otro Ticker manualmente": "CUSTOM",
    },
}


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


# FUNCIÓN ROBUSTA DE DESCARGA E HISTORIAL DE DIVISAS (FOREX 5 AÑOS)
def obtener_historial_forex(base_curr, target_curr):
    try:
        if base_curr == target_curr:
            dates = pd.date_range(end=pd.Timestamp.now(), periods=1260, freq='B')
            return pd.DataFrame({'Close': 1.0}, index=dates)
        
        # 1. Ticker directo BASE + TARGET
        ticker_direct = f"{base_curr}{target_curr}=X"
        df = yf.Ticker(ticker_direct).history(period="5y")
        if not df.empty and len(df) > 10:
            return df[['Close']]
        
        # 2. Ticker inverso TARGET + BASE
        ticker_inverse = f"{target_curr}{base_curr}=X"
        df_inv = yf.Ticker(ticker_inverse).history(period="5y")
        if not df_inv.empty and len(df_inv) > 10:
            df_inv['Close'] = 1.0 / df_inv['Close']
            return df_inv[['Close']]
        
        # 3. Cruce vía USD
        df_base = None
        if base_curr != "USD":
            df_base = yf.Ticker(f"{base_curr}USD=X").history(period="5y")
            if df_base.empty or len(df_base) <= 10:
                df_b_inv = yf.Ticker(f"USD{base_curr}=X").history(period="5y")
                if not df_b_inv.empty and len(df_b_inv) > 10:
                    df_base = df_b_inv.copy()
                    df_base['Close'] = 1.0 / df_b_inv['Close']
        
        df_target = None
        if target_curr != "USD":
            df_target = yf.Ticker(f"{target_curr}USD=X").history(period="5y")
            if df_target.empty or len(df_target) <= 10:
                df_t_inv = yf.Ticker(f"USD{target_curr}=X").history(period="5y")
                if not df_t_inv.empty and len(df_t_inv) > 10:
                    df_target = df_t_inv.copy()
                    df_target['Close'] = 1.0 / df_t_inv['Close']
        
        if base_curr == "USD" and df_target is not None and not df_target.empty:
            df_res = pd.DataFrame(index=df_target.index)
            df_res['Close'] = 1.0 / df_target['Close']
            return df_res
        elif target_curr == "USD" and df_base is not None and not df_base.empty:
            df_res = pd.DataFrame(index=df_base.index)
            df_res['Close'] = df_base['Close']
            return df_res
        elif df_base is not None and df_target is not None and not df_base.empty and not df_target.empty:
            df_comb = pd.concat([df_base['Close'], df_target['Close']], axis=1, keys=['b', 't']).dropna()
            df_res = pd.DataFrame(index=df_comb.index)
            df_res['Close'] = df_comb['b'] / df_comb['t']
            return df_res
            
    except Exception:
        pass
    return pd.DataFrame()


def generar_fallback_json_forex(base_curr, target_curr, rate_actual, horizonte, proposito, volatilidad_anual):
    return {
        "diagnostico": f"El par {base_curr}/{target_curr} cotiza a un tipo de cambio de {rate_actual:,.4f}. La trayectoria de 5 años refleja una volatilidad anualizada del {volatilidad_anual:.2%}.",
        "viabilidad": f"Para un horizonte de {horizonte} con propósito de {proposito}, se requiere evaluar la diferencial de tasas de interés entre ambos bancos centrales.",
        "riesgos": "1. Decisiones de política monetaria y tasas de referencia\n2. Volatilidad en precios de commodities e inflación\n3. Eventos geopolíticos e incertidumbre electoral",
        "veredicto": "MANTENER EN OBSERVACIÓN",
        "fundamento": f"Se recomienda vigilar los soportes y resistencias clave del par {base_curr}/{target_curr} antes de ejecutar coberturas o conversiones de capital masivas."
    }


def generar_fallback_json_acciones(simb, capital_input, precio_actual, perfil_riesgo, horizonte, pe_ratio, volatilidad_anual):
    es_insuficiente = capital_input < precio_actual
    es_riesgoso = (perfil_riesgo == "Conservador" and volatilidad_anual > 0.25)
    
    if es_insuficiente or es_riesgoso:
        veredicto = "DESESTIMAR"
        fundamento = f"El capital disponible ({simb} {capital_input:,.2f}) es insuficiente para adquirir 1 acción completa ({simb} {precio_actual:,.2f}) o la volatilidad excede la tolerancia del perfil {perfil_riesgo}."
    else:
        veredicto = "MANTENER EN OBSERVACIÓN"
        fundamento = f"El activo presenta métricas aceptables con un PER de {pe_ratio}, pero requiere monitoreo según el horizonte de {horizonte}."

    return {
        "diagnostico": f"El activo cotiza a un precio de {simb} {precio_actual:,.2f} con un PER de {pe_ratio} evaluado sobre la curva de los últimos 5 años.",
        "viabilidad": f"Capital disponible de {simb} {capital_input:,.2f} frente al precio unitario de {simb} {precio_actual:,.2f} en un horizonte de {horizonte}.",
        "riesgos": "1. Sensibilidad a tasas de interés\n2. Volatilidad sectorial y macroeconómica\n3. Variaciones en la demanda global",
        "veredicto": veredicto,
        "fundamento": fundamento
    }


# --- ENCABEZADO PRINCIPAL ---
st.title("📈 Terminal Inteligente de Inversiones & Forex")
st.markdown(
    "<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 20px;'>"
    "Plataforma cuantitativa, econométrica y analítica para la evaluación estratégica de acciones globales y mercado de divisas (Análisis a 5 Años).</p>",
    unsafe_allow_html=True,
)

# --- ESTRUCTURA DE PESTAÑAS (TABS) ---
tab_acciones, tab_forex = st.tabs(["📊 Análisis Accionario", "🔀 Comparativa de Divisas (Forex)"])

# ==============================================================================
# PESTAÑA 1: ANÁLISIS ACCIONARIO
# ==============================================================================
with tab_acciones:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Inversión Accionaria")

        col1, col2, col3 = st.columns(3)

        with col1:
            mercado_sel = st.selectbox("🌍 Mercado de Origen:", list(MERCADOS.keys()), key="stock_mercado")

        dic_acciones = MERCADOS[mercado_sel]

        with col2:
            opcion_accion = st.selectbox(
                "📊 Selección de Acción / Ticker:",
                list(dic_acciones.keys()),
                format_func=lambda x: (
                    f"{x} - {dic_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir Ticker'}"
                ),
                key="stock_accion"
            )

            if opcion_accion == "🔍 Buscar otro Ticker manualmente":
                ticker_final = st.text_input(
                    "Ingrese Ticker oficial de Yahoo Finance (ej: AMD, MELI, PBR):",
                    value="AAPL",
                    key="stock_ticker_manual"
                ).upper()
                nombre_empresa = ticker_final
            else:
                ticker_final = opcion_accion
                nombre_empresa = dic_acciones[opcion_accion]

        with col3:
            moneda_sel = st.selectbox("💵 Moneda de Operación:", list(TASAS_CAMBIO_USD.keys()), key="stock_moneda")

        simb = SIMBOLOS_MONEDA[moneda_sel]
        monto_min = MINIMOS_MONEDA[moneda_sel]

        col4, col5, col6 = st.columns(3)

        with col4:
            capital_input = st.number_input(
                f"💰 Capital Disponible ({simb}):",
                min_value=monto_min,
                value=monto_min * 10,
                step=monto_min,
                key="stock_capital"
            )

        with col5:
            horizonte = st.selectbox(
                "⏱️ Horizonte Temporal:",
                [
                    "Corto Plazo (1 a 3 meses)",
                    "Mediano Plazo (6 meses a 1 año)",
                    "Largo Plazo (1 año a más)",
                ],
                key="stock_horizonte"
            )

        with col6:
            perfil_riesgo = st.selectbox(
                "🛡️ Perfil del Inversor:", ["Conservador", "Moderado", "Agresivo"], key="stock_perfil"
            )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Multidimensional Accionario", use_container_width=True, key="btn_stock"):
        if not api_key_oculta or not client:
            st.error("⚠️ El servicio de Inteligencia Artificial no está configurado en el servidor (Falta GEMINI_API_KEY).")
        else:
            datos_cargados = False
            try:
                search_ticker = TICKER_MAP.get(ticker_final, ticker_final)
                stock = yf.Ticker(search_ticker)
                df = stock.history(period="5y")
                
                if df.empty and search_ticker.endswith(".LM"):
                    alt_ticker = search_ticker.replace(".LM", "")
                    stock = yf.Ticker(alt_ticker)
                    df = stock.history(period="5y")

                info = stock.info

                if df.empty:
                    st.error(f"⚠️ No se encontraron registros financieros para el símbolo '{ticker_final}'. Verifique el ticker en Yahoo Finance.")
                else:
                    datos_cargados = True
                    currency_base = info.get("currency", "USD")
                    factor_conv = obtener_factor_conversion(currency_base, moneda_sel)

                    precio_actual_raw = df["Close"].iloc[-1]
                    precio_actual = precio_actual_raw * factor_conv
                    df["Close_Moneda"] = df["Close"] * factor_conv

                    market_cap = info.get("marketCap", 0) * factor_conv if info.get("marketCap") else 0
                    pe_ratio_raw = info.get("trailingPE", "N/A")
                    pe_ratio = f"{pe_ratio_raw:.2f}" if isinstance(pe_ratio_raw, (int, float)) else str(pe_ratio_raw)

                    pb_ratio_raw = info.get("priceToBook", "N/A")
                    pb_ratio = f"{pb_ratio_raw:.2f}" if isinstance(pb_ratio_raw, (int, float)) else str(pb_ratio_raw)

                    dividend_yield = info.get("dividendYield", 0)
                    dividend_str = f"{dividend_yield*100:.2f}%" if dividend_yield else "0.00%"
                    profit_margin = info.get("profitMargins", 0)
                    margin_str = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                    sector = info.get("sector", "General / No especificado")

                    df["Retorno_Diario"] = df["Close"].pct_change()
                    volatilidad_anual = df["Retorno_Diario"].std() * np.sqrt(252)
                    retorno_medio_diario = df["Retorno_Diario"].mean()
                    var_95 = np.percentile(df["Retorno_Diario"].dropna(), 5)

                    sma_50 = df["Close_Moneda"].rolling(window=50).mean().iloc[-1]
                    sma_200 = df["Close_Moneda"].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else sma_50

                    # KPIs
                    st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos (5 Años)")
                    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                    c_m1.metric(f"Precio Actual ({simb})", f"{simb} {precio_actual:,.2f}")
                    c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
                    c_m3.metric("Volatilidad Anualizada (5A)", f"{volatilidad_anual:.2%}")
                    c_m4.metric("Margen Beneficio Neto", f"{margin_str}")

                    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
                    c_m5.metric(f"Cap. de Mercado ({simb})", f"{simb} {market_cap:,.0f}" if market_cap else "N/A")
                    c_m6.metric("Ratio P/B", f"{pb_ratio}")
                    c_m7.metric("Rendimiento Dividendo", f"{dividend_str}")
                    c_m8.metric("VaR 95% Diarios (5A)", f"{var_95:.2%}")

                    st.markdown("---")

                    # Gráfico Plotly
                    st.markdown(f"### 📈 Comportamiento Histórico a 5 Años & Proyección ({horizonte})")
                    dias_proy = 60 if "1 a 3 meses" in horizonte else (180 if "6 meses a 1 año" in horizonte else 365)

                    np.random.seed(42)
                    cambios_simulados = np.random.normal(retorno_medio_diario, df["Retorno_Diario"].std(), dias_proy)
                    precios_futuros = [precio_actual]
                    for cambio in cambios_simulados:
                        precios_futuros.append(precios_futuros[-1] * (1 + cambio))

                    fechas_hist = df.index
                    precios_hist = df["Close_Moneda"]
                    fechas_futuras = pd.date_range(start=df.index[-1], periods=dias_proy + 1, freq="B")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=fechas_hist, y=precios_hist, mode="lines", name="Histórico Real (5 Años)", line=dict(color="#00e676", width=2.0)))
                    fig.add_trace(go.Scatter(x=fechas_futuras, y=precios_futuros, mode="lines", name="Proyección Econométrica", line=dict(color="#e040fb", width=2.5, dash="dash")))

                    fig.update_layout(
                        title=dict(text=f"Evolución de Cotización Real (5 Años) y Proyección - {ticker_final}", font=dict(size=16, color="#f9fafb")),
                        xaxis=dict(title="Fecha / Periodo de Proyección", gridcolor="#1e293b"),
                        yaxis=dict(title=f"Precio del Activo ({simb})", gridcolor="#1e293b", zeroline=False, autorange=True),
                        template="plotly_dark",
                        paper_bgcolor="#0f172a",
                        plot_bgcolor="#0f172a",
                        height=500,
                        hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.8)")
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("""
                        <div class="disclaimer-box">
                            <strong>⚠️ Aviso Legal / Descargo de Responsabilidad:</strong> 
                            Este modelo genera pronósticos estadísticos basándose estrictamente en datos pasados de los últimos 5 años y condiciones actuales de mercado. 
                            No es 100% exacto y está expuesto a volatilidad implícita y eventos macroeconómicos.
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

            except Exception as e:
                st.error(f"Error procesando métricas financieras: {str(e)}")

            if datos_cargados:
                st.markdown("## 📋 Dictamen Estratégico de Inversión Accionaria")

                paquete_analisis = f"""
                Activo: {ticker_final} ({nombre_empresa}) | Sector: {sector}
                Precio Actual: {simb} {precio_actual:,.2f} | Capital: {simb} {capital_input:,.2f}
                Moneda: {moneda_sel} | Horizonte: {horizonte} | Perfil: {perfil_riesgo}
                PER: {pe_ratio} | P/B: {pb_ratio} | Volatilidad 5A: {volatilidad_anual:.2%} | VaR 95%: {var_95:.2%}
                SMA 50: {simb} {sma_50:,.2f} | SMA 200: {simb} {sma_200:,.2f}
                """

                prompt_ia = f"""
                Genera respuesta ÚNICAMENTE en JSON sintético:
                {paquete_analisis}

                JSON OBLIGATORIO:
                {{
                  "diagnostico": "Análisis síntesis de PER, P/B y SMA 50/200 a 5 años.",
                  "viabilidad": "Evalúa capital {simb} {capital_input:,.2f} vs precio {simb} {precio_actual:,.2f} y perfil {perfil_riesgo}.",
                  "riesgos": "1. Macro\\n2. Sectorial\\n3. Operativo",
                  "veredicto": "DESESTIMAR",
                  "fundamento": "Explicación directa y ejecutiva."
                }}
                REGLAS: Sin cursivas ni asteriscos. 'veredicto' sólo COMPRAR, DESESTIMAR o MANTENER EN OBSERVACIÓN.
                """

                with st.spinner("🤖 Generando dictamen estratégico..."):
                    raw_response = generar_respuesta_ia_rapida(client, prompt_ia)
                    data_json = parse_json_respuesta(raw_response)

                    if not data_json:
                        data_json = generar_fallback_json_acciones(simb, capital_input, precio_actual, perfil_riesgo, horizonte, pe_ratio, volatilidad_anual)

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">1. Diagnóstico Fundamental y Técnico</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("diagnostico", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">2. Viabilidad del Capital y Horizonte</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("viabilidad", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        riesgos_txt = limpiar_texto_markdown(data_json.get("riesgos", "")).replace('\n', '<br>')
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">3. Factores de Riesgo Macro</div>
                            <div class="analysis-card-body">{riesgos_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col4:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">4. Veredicto Estratégico</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("fundamento", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_col1, bot_col2 = st.columns([3, 1])

                    with bot_col1:
                        st.markdown(f"""
                        <div class="decision-container">
                            <div class="analysis-card-title" style="font-size: 1.12rem; margin-bottom: 10px;">🎯 Decisión y Fundamento Ejecutivo</div>
                            <div class="analysis-card-body" style="font-size: 0.96rem; line-height: 1.65; color: #f8fafc;">
                                {limpiar_texto_markdown(data_json.get("fundamento", ""))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with bot_col2:
                        veredicto_clean = str(data_json.get("veredicto", "MANTENER EN OBSERVACIÓN")).upper()
                        if "COMPRAR" in veredicto_clean and "DESESTIMAR" not in veredicto_clean:
                            badge_class = "decision-comprar"
                            badge_icon = "🟢"
                            badge_text = "COMPRAR"
                        elif "DESESTIMAR" in veredicto_clean:
                            badge_class = "decision-desestimar"
                            badge_icon = "🔴"
                            badge_text = "DESESTIMAR"
                        else:
                            badge_class = "decision-observacion"
                            badge_icon = "🟡"
                            badge_text = "MANTENER EN OBSERVACIÓN"

                        st.markdown(f"""
                        <div class="decision-badge-box {badge_class}">
                            <div style="font-size: 2.2rem; margin-bottom: 6px;">{badge_icon}</div>
                            <div style="font-weight: 800; letter-spacing: 0.08em;">{badge_text}</div>
                        </div>
                        """, unsafe_allow_html=True)


# ==============================================================================
# PESTAÑA 2: COMPARATIVA DE DIVISAS (FOREX)
# ==============================================================================
with tab_forex:
    with st.container(border=True):
        st.subheader("⚙️ Parámetros Operativos de Evaluación Cambiaria")

        col_fx1, col_fx2, col_fx3 = st.columns(3)

        with col_fx1:
            base_curr = st.selectbox("🔀 Moneda de Origen (Base):", list(DIVISAS.keys()), index=0, format_func=lambda x: DIVISAS[x], key="fx_base")

        with col_fx2:
            target_curr = st.selectbox("🎯 Moneda Destino (Objetivo):", list(DIVISAS.keys()), index=1, format_func=lambda x: DIVISAS[x], key="fx_target")

        with col_fx3:
            monto_fx = st.number_input(f"💰 Monto de Conversión ({base_curr}):", min_value=1.0, value=1000.0, step=100.0, key="fx_monto")

        col_fx4, col_fx5 = st.columns(2)

        with col_fx4:
            horizonte_fx = st.selectbox(
                "⏱️ Horizonte Temporal:",
                [
                    "Corto Plazo (1 a 3 meses)",
                    "Mediano Plazo (6 meses a 1 año)",
                    "Largo Plazo (1 año a más)"
                ],
                key="fx_horizonte"
            )

        with col_fx5:
            proposito_fx = st.selectbox(
                "🎯 Propósito de la Evaluación:",
                [
                    "Cobertura de Riesgo Cambiario (Hedging)",
                    "Operación de Comercio Exterior / Importación",
                    "Inversión / Especulación Forex",
                    "Ahorro / Reserva de Valor"
                ],
                key="fx_proposito"
            )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Ejecutar Análisis Multidimensional de Divisas", use_container_width=True, key="btn_forex"):
        if not api_key_oculta or not client:
            st.error("⚠️ El servicio de Inteligencia Artificial no está configurado en el servidor (Falta GEMINI_API_KEY).")
        else:
            datos_fx_cargados = False
            try:
                df_fx = obtener_historial_forex(base_curr, target_curr)

                if df_fx.empty:
                    st.error(f"⚠️ No se pudo obtener el historial de tipo de cambio para la paridad {base_curr}/{target_curr}. Intente con otra combinación.")
                else:
                    datos_fx_cargados = True
                    rate_actual = df_fx['Close'].iloc[-1]
                    df_fx['Retorno_Diario'] = df_fx['Close'].pct_change()

                    volatilidad_anual = df_fx['Retorno_Diario'].std() * np.sqrt(252)
                    retorno_medio_diario = df_fx['Retorno_Diario'].mean()
                    var_95 = np.percentile(df_fx['Retorno_Diario'].dropna(), 5)

                    min_52w = df_fx['Close'].tail(252).min() if len(df_fx) >= 252 else df_fx['Close'].min()
                    max_52w = df_fx['Close'].tail(252).max() if len(df_fx) >= 252 else df_fx['Close'].max()

                    sma_50 = df_fx['Close'].rolling(window=50).mean().iloc[-1]
                    sma_200 = df_fx['Close'].rolling(window=200).mean().iloc[-1] if len(df_fx) >= 200 else sma_50

                    rate_inicial_5y = df_fx['Close'].iloc[0]
                    var_5y_pct = ((rate_actual - rate_inicial_5y) / rate_inicial_5y) * 100

                    # KPIs Cambiarios
                    st.markdown(f"### 📊 Panel de Indicadores Clave - Paridad {base_curr} / {target_curr}")

                    c_fx1, c_fx2, c_fx3, c_fx4 = st.columns(4)
                    c_fx1.metric(f"Tipo de Cambio Actual ({target_curr})", f"{rate_actual:,.4f}")
                    c_fx2.metric("Monto Convertido Estimado", f"{monto_fx * rate_actual:,.2f} {target_curr}")
                    c_fx3.metric("Volatilidad Anualized (5A)", f"{volatilidad_anual:.2%}")
                    c_fx4.metric("Variación a 5 Años", f"{var_5y_pct:+.2f}%")

                    c_fx5, c_fx6, c_fx7, c_fx8 = st.columns(4)
                    c_fx5.metric("Promedio Móvil SMA 50d", f"{sma_50:,.4f}")
                    c_fx6.metric("Promedio Móvil SMA 200d", f"{sma_200:,.4f}")
                    c_fx7.metric("Rango 52 Semanas (Mín - Máx)", f"{min_52w:,.2f} - {max_52w:,.2f}")
                    c_fx8.metric("VaR 95% Diarios (Riesgo FX)", f"{var_95:.2%}")

                    st.markdown("---")

                    # Gráfico Plotly FX
                    st.markdown(f"### 📈 Comportamiento Histórico a 5 Años & Proyección Econométrica ({horizonte_fx})")

                    dias_proy = 60 if "1 a 3 meses" in horizonte_fx else (180 if "6 meses a 1 año" in horizonte_fx else 365)

                    np.random.seed(42)
                    cambios_simulados = np.random.normal(retorno_medio_diario, df_fx['Retorno_Diario'].std(), dias_proy)
                    precios_futuros = [rate_actual]
                    for cambio in cambios_simulados:
                        precios_futuros.append(precios_futuros[-1] * (1 + cambio))

                    fechas_hist = df_fx.index
                    precios_hist = df_fx['Close']
                    fechas_futuras = pd.date_range(start=df_fx.index[-1], periods=dias_proy + 1, freq="B")

                    fig_fx = go.Figure()
                    fig_fx.add_trace(go.Scatter(x=fechas_hist, y=precios_hist, mode="lines", name=f"Tipo de Cambio Real ({base_curr}/{target_curr})", line=dict(color="#00e676", width=2.0)))
                    fig_fx.add_trace(go.Scatter(x=fechas_futuras, y=precios_futuros, mode="lines", name="Proyección Econométrica FX", line=dict(color="#e040fb", width=2.5, dash="dash")))

                    fig_fx.update_layout(
                        title=dict(text=f"Evolución de Paridad Cambiaria (5 Años) y Proyección - {base_curr}/{target_curr}", font=dict(size=16, color="#f9fafb")),
                        xaxis=dict(title="Fecha / Periodo de Proyección", gridcolor="#1e293b"),
                        yaxis=dict(title=f"Tipo de Cambio ({base_curr}/{target_curr})", gridcolor="#1e293b", zeroline=False, autorange=True),
                        template="plotly_dark",
                        paper_bgcolor="#0f172a",
                        plot_bgcolor="#0f172a",
                        height=500,
                        hovermode="x unified",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(15,23,42,0.8)")
                    )

                    st.plotly_chart(fig_fx, use_container_width=True)

                    st.markdown("""
                        <div class="disclaimer-box">
                            <strong>⚠️ Aviso Legal / Descargo de Responsabilidad FX:</strong> 
                            Las cotizaciones cambiarias están sujetas a alta volatilidad por decisiones de política monetaria (Fed, BCE, BCRP, etc.), intervenciones cambiarias y eventos macroeconómicos. 
                            Este modelo econométrico no constituye asesoramiento financiero ni garantía de rendimiento.
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

            except Exception as e:
                st.error(f"Error procesando análisis cambiario: {str(e)}")

            if datos_fx_cargados:
                st.markdown(f"## 📋 Dictamen Estratégico de Evaluación Cambiaria ({base_curr} / {target_curr})")

                paquete_analisis_fx = f"""
                Par de Divisas: {base_curr} / {target_curr} ({DIVISAS[base_curr]} frente a {DIVISAS[target_curr]})
                Tipo de Cambio Actual: 1 {base_curr} = {rate_actual:,.4f} {target_curr}
                Monto Evaluado: {monto_fx:,.2f} {base_curr} (= {monto_fx * rate_actual:,.2f} {target_curr})
                Horizonte Temporal: {horizonte_fx} | Propósito: {proposito_fx}
                Volatilidad Anualizada (5A): {volatilidad_anual:.2%} | Variación 5A: {var_5y_pct:+.2f}%
                VaR 95% Diario: {var_95:.2%} | SMA 50d: {sma_50:,.4f} | SMA 200d: {sma_200:,.4f}
                Rango 52 Semanas: Mínimo {min_52w:,.4f} - Máximo {max_52w:,.4f}
                """

                prompt_fx = f"""
                Actúa como un Economista Senior especializado en Mercado Forex y Macroeconomía Global.
                Evalúa el par {base_curr}/{target_curr} y genera respuesta ÚNICAMENTE en JSON sintético:

                INFORMACIÓN A EVALUAR:
                {paquete_analisis_fx}

                JSON OBLIGATORIO:
                {{
                  "diagnostico": "Análisis macroeconómico síntesis, diferencial de tasas e indicadores técnicos (SMA 50/200) a 5 años.",
                  "viabilidad": "Evaluación de conveniencia de conversión / cobertura para {monto_fx:,.2f} {base_curr} en el horizonte {horizonte_fx}.",
                  "riesgos": "1. Política Monetaria / Tasas\\n2. Inflación y Commodities\\n3. Geopolítica / FX",
                  "veredicto": "FORTALECIMIENTO DE BASE",
                  "fundamento": "Explicación directa, sintética y ejecutiva."
                }}
                REGLAS: Sin cursivas ni asteriscos. 'veredicto' sólo FORTALECIMIENTO DE BASE, DEBILITAMIENTO DE BASE o MANTENER EN OBSERVACIÓN.
                """

                with st.spinner("🤖 Generando dictamen cambial estratégico..."):
                    raw_response_fx = generar_respuesta_ia_rapida(client, prompt_fx)
                    data_json_fx = parse_json_respuesta(raw_response_fx)

                    if not data_json_fx:
                        data_json_fx = generar_fallback_json_forex(base_curr, target_curr, rate_actual, horizonte_fx, proposito_fx, volatilidad_anual)

                    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

                    with col_f1:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">1. Diagnóstico Macroeconómico y Técnico</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json_fx.get("diagnostico", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_f2:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">2. Viabilidad y Sensibilidad Cambiaria</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json_fx.get("viabilidad", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_f3:
                        riesgos_fx_txt = limpiar_texto_markdown(data_json_fx.get("riesgos", "")).replace('\n', '<br>')
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">3. Factores de Riesgo Geopolítico / FX</div>
                            <div class="analysis-card-body">{riesgos_fx_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_f4:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <div class="analysis-card-title">4. Estrategia y Posicionamiento</div>
                            <div class="analysis-card-body">{limpiar_texto_markdown(data_json_fx.get("fundamento", ""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

                    bot_fx1, bot_fx2 = st.columns([3, 1])

                    with bot_fx1:
                        st.markdown(f"""
                        <div class="decision-container">
                            <div class="analysis-card-title" style="font-size: 1.12rem; margin-bottom: 10px;">🎯 Decisión y Fundamento Ejecutivo FX</div>
                            <div class="analysis-card-body" style="font-size: 0.96rem; line-height: 1.65; color: #f8fafc;">
                                {limpiar_texto_markdown(data_json_fx.get("fundamento", ""))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with bot_fx2:
                        veredicto_fx_clean = str(data_json_fx.get("veredicto", "MANTENER EN OBSERVACIÓN")).upper()
                        if "FORTALECIMIENTO" in veredicto_fx_clean or "COMPRA" in veredicto_fx_clean:
                            badge_fx_class = "decision-comprar"
                            badge_fx_icon = "🟢"
                            badge_fx_text = f"FORTALECIMIENTO ({base_curr})"
                        elif "DEBILITAMIENTO" in veredicto_fx_clean or "VENTA" in veredicto_fx_clean:
                            badge_fx_class = "decision-desestimar"
                            badge_fx_icon = "🔴"
                            badge_fx_text = f"DEBILITAMIENTO ({base_curr})"
                        else:
                            badge_fx_class = "decision-observacion"
                            badge_fx_icon = "🟡"
                            badge_fx_text = "ESTABLE / OBSERVACIÓN"

                        st.markdown(f"""
                        <div class="decision-badge-box {badge_fx_class}">
                            <div style="font-size: 2.2rem; margin-bottom: 6px;">{badge_fx_icon}</div>
                            <div style="font-weight: 800; letter-spacing: 0.08em; font-size: 1rem;">{badge_fx_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
