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
    page_title="Asistente Inteligente de Inversiones Bursátiles",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS CSS HIGH-END (MINIMALISTA, TOP FINTECH TERMINAL)
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

    /* TARJETAS DEL DICTAMEN DE ANÁLISIS (BOCETO PAINT REFINADO) */
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


# LIMPIEZA DE FORMATO MARKDOWN PASTE
def limpiar_texto_markdown(texto):
  if not texto:
    return ""
  texto = str(texto).replace("`", "")
  return texto.strip()


# MODELOS OFICIALES DE GOOGLE AI STUDIO Y GENERACIÓN ASÍNCRONA
def generar_respuesta_ia_rapida(client, prompt):
  modelos_validos = [
      "gemini-2.5-flash",
      "gemini-2.0-flash",
      "gemini-1.5-flash",
      "gemini-flash-latest",
  ]

  config = types.GenerateContentConfig(
      temperature=0.1, max_output_tokens=500, response_mime_type="application/json"
  )

  for modelo in modelos_validos:
    try:
      response = client.models.generate_content(
          model=modelo, contents=prompt, config=config
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
  cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
  cleaned = re.sub(r"\s*```$", "", cleaned)
  try:
    return json.loads(cleaned)
  except Exception:
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
      try:
        return json.loads(match.group(0))
      except Exception:
        pass
  return None


def generar_fallback_json(
    simb,
    capital_input,
    precio_actual,
    perfil_riesgo,
    horizonte,
    pe_ratio,
    volatilidad_anual,
):
  es_insuficiente = capital_input < precio_actual
  es_riesgoso = perfil_riesgo == "Conservador" and volatilidad_anual > 0.25

  if es_insuficiente or es_riesgoso:
    veredicto = "DESESTIMAR"
    fundamento = (
        f"El capital disponible ({simb} {capital_input:,.2f}) es insuficiente"
        f" para adquirir 1 acción completa ({simb} {precio_actual:,.2f}) o la"
        f" volatilidad excede la tolerancia del perfil {perfil_riesgo}."
    )
  else:
    veredicto = "MANTENER EN OBSERVACIÓN"
    fundamento = (
        f"El activo presenta métricas aceptables con un PER de {pe_ratio}, pero"
        f" requiere monitoreo según el horizonte de {horizonte}."
    )

  return {
      "diagnostico": (
          f"El activo cotiza a un precio de {simb} {precio_actual:,.2f} con un"
          f" PER de {pe_ratio} evaluado sobre la curva de los últimos 5 años."
      ),
      "viabilidad": (
          f"Capital disponible de {simb} {capital_input:,.2f} frente al precio"
          f" unitario de {simb} {precio_actual:,.2f} en un horizonte de"
          f" {horizonte}."
      ),
      "riesgos": (
          "1. Sensibilidad a tasas de interés\n2. Volatilidad sectorial y"
          " macroeconómica\n3. Variaciones en la demanda global"
      ),
      "veredicto": veredicto,
      "fundamento": fundamento,
  }


# --- DICCIONARIOS, MAPEO DE TICKERS Y TASAS DE CONVERSIÓN ---
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


# NORMALIZACIÓN DINÁMICA DE DIVISA BASE A DIVISA DESTINO
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
    tasa_base_usd = 1.0  # Por defecto USD

  return (1.0 / tasa_base_usd) * tasa_destino


# --- ENCABEZADO PRINCIPAL ---
st.title("📈 Asistente Inteligente de Inversiones Bursátiles")
st.markdown(
    "<p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>"
    "Terminal cuantitativa, fundamental y econométrica para la evaluación"
    " estratégica de activos financieros globales (Análisis a 5 Años).</p>",
    unsafe_allow_html=True,
)

# --- PANEL DE CONFIGURACIÓN ---
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
        format_func=lambda x: (
            f"{x} - {dic_acciones[x] if x != '🔍 Buscar otro Ticker manualmente' else 'Escribir Ticker'}"
        ),
    )

    if opcion_accion == "🔍 Buscar otro Ticker manualmente":
      ticker_final = st.text_input(
          "Ingrese Ticker oficial de Yahoo Finance (ej: AMD, MELI, PBR):",
          value="AAPL",
      ).upper()
      nombre_empresa = ticker_final
    else:
      ticker_final = opcion_accion
      nombre_empresa = dic_acciones[opcion_accion]

  with col3:
    moneda_sel = st.selectbox("💵 Moneda de Operación:", list(TASAS_CAMBIO_USD.keys()))

  simb = SIMBOLOS_MONEDA[moneda_sel]
  monto_min = MINIMOS_MONEDA[moneda_sel]

  col4, col5, col6 = st.columns(3)

  with col4:
    capital_input = st.number_input(
        f"💰 Capital Disponible ({simb}):",
        min_value=monto_min,
        value=monto_min * 10,
        step=monto_min,
    )

  with col5:
    horizonte = st.selectbox(
        "⏱️ Horizonte Temporal:",
        [
            "Corto Plazo (1 a 3 meses)",
            "Mediano Plazo (6 meses a 1 año)",
            "Largo Plazo (1 año a más)",
        ],
    )

  with col6:
    perfil_riesgo = st.selectbox(
        "🛡️ Perfil del Inversor:", ["Conservador", "Moderado", "Agresivo"]
    )

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

# --- BOTÓN PRINCIPAL DE EJECUCIÓN ---
if st.button(
    "🚀 Ejecutar Análisis Multidimensional y Proyección",
    use_container_width=True,
):
  if not api_key_oculta or not client:
    st.error(
        "⚠️ El servicio de Inteligencia Artificial no está configurado en el"
        " servidor (Falta la clave GEMINI_API_KEY en Secrets)."
    )
  else:
    # 1. PASO BURSÁTIL Y CUANTITATIVO (HISTÓRICO 5 AÑOS)
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
        st.error(
            "⚠️ No se encontraron registros financieros para el símbolo"
            f" '{ticker_final}'. Verifique el ticker en Yahoo Finance."
        )
      else:
        datos_cargados = True
        currency_base = info.get("currency", "USD")
        factor_conv = obtener_factor_conversion(currency_base, moneda_sel)

        precio_actual_raw = df["Close"].iloc[-1]
        precio_actual = precio_actual_raw * factor_conv
        df["Close_Moneda"] = df["Close"] * factor_conv

        # Datos fundamentales
        market_cap = (
            info.get("marketCap", 0) * factor_conv
            if info.get("marketCap")
            else 0
        )
        pe_ratio_raw = info.get("trailingPE", "N/A")
        pe_ratio = (
            f"{pe_ratio_raw:.2f}"
            if isinstance(pe_ratio_raw, (int, float))
            else str(pe_ratio_raw)
        )

        pb_ratio_raw = info.get("priceToBook", "N/A")
        pb_ratio = (
            f"{pb_ratio_raw:.2f}"
            if isinstance(pb_ratio_raw, (int, float))
            else str(pb_ratio_raw)
        )

        dividend_yield = info.get("dividendYield", 0)
        dividend_str = (
            f"{dividend_yield*100:.2f}%" if dividend_yield else "0.00%"
        )
        profit_margin = info.get("profitMargins", 0)
        margin_str = (
            f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
        )
        sector = info.get("sector", "General / No especificado")

        # Métricas Cuantitativas calculadas sobre los 5 años
        df["Retorno_Diario"] = df["Close"].pct_change()
        volatilidad_anual = df["Retorno_Diario"].std() * np.sqrt(252)
        retorno_medio_diario = df["Retorno_Diario"].mean()
        var_95 = np.percentile(df["Retorno_Diario"].dropna(), 5)

        sma_50 = df["Close_Moneda"].rolling(window=50).mean().iloc[-1]
        sma_200 = (
            df["Close_Moneda"].rolling(window=200).mean().iloc[-1]
            if len(df) >= 200
            else sma_50
        )

        # --- MOSTRAR PANEL DE KPIS DE INMEDIATO ---
        st.markdown("### 📊 Panel de Indicadores Clave & Fundamentos (5 Años)")

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric(
            f"Precio Actual ({simb})", f"{simb} {precio_actual:,.2f}"
        )
        c_m2.metric("PER (Price / Earnings)", f"{pe_ratio}")
        c_m3.metric("Volatilidad Anualizada (5A)", f"{volatilidad_anual:.2%}")
        c_m4.metric("Margen Beneficio Neto", f"{margin_str}")

        c_m5, c_m6, c_m7, c_m8 = st.columns(4)
        c_m5.metric(
            f"Cap. de Mercado ({simb})",
            f"{simb} {market_cap:,.0f}" if market_cap else "N/A",
        )
        c_m6.metric("Ratio P/B", f"{pb_ratio}")
        c_m7.metric("Rendimiento Dividendo", f"{dividend_str}")
        c_m8.metric("VaR 95% Diarios (5A)", f"{var_95:.2%}")

        st.markdown("---")

        # --- MOSTRAR GRÁFICO PLOTLY CON AUTO-ESCALADO ---
        st.markdown(
            "### 📈 Comportamiento Histórico a 5 Años & Proyección"
            f" ({horizonte})"
        )

        dias_proy = (
            60
            if "1 a 3 meses" in horizonte
            else (180 if "6 meses a 1 año" in horizonte else 365)
        )

        np.random.seed(42)
        cambios_simulados = np.random.normal(
            retorno_medio_diario, df["Retorno_Diario"].std(), dias_proy
        )
        precios_futuros = [precio_actual]
        for cambio in cambios_simulados:
          precios_futuros.append(precios_futuros[-1] * (1 + cambio))

        fechas_hist = df.index
        precios_hist = df["Close_Moneda"]
        fechas_futuras = pd.date_range(
            start=df.index[-1], periods=dias_proy + 1, freq="B"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=fechas_hist,
                y=precios_hist,
                mode="lines",
                name="Histórico Real (5 Años)",
                line=dict(color="#00e676", width=2.0),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=fechas_futuras,
                y=precios_futuros,
                mode="lines",
                name="Proyección Econométrica",
                line=dict(color="#e040fb", width=2.5, dash="dash"),
            )
        )

        fig.update_layout(
            title=dict(
                text=(
                    "Evolución de Cotización Real (5 Años) y Proyección -"
                    f" {ticker_final}"
                ),
                font=dict(size=16, color="#f9fafb"),
            ),
            xaxis=dict(
                title="Fecha / Periodo de Proyección", gridcolor="#1e293b"
            ),
            yaxis=dict(
                title=f"Precio del Activo ({simb})",
                gridcolor="#1e293b",
                zeroline=False,
                autorange=True,
            ),
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=500,
            hovermode="x unified",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(15,23,42,0.8)",
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- AVISO LEGAL ---
        st.markdown(
            """
            <div class="disclaimer-box">
                <strong>⚠️ Aviso Legal / Descargo de Responsabilidad:</strong> 
                Este modelo genera pronósticos estadísticos basándose estrictamente en datos pasados de los últimos 5 años y condiciones actuales de mercado. 
                No es 100% exacto y está expuesto a la volatilidad implícita, eventos macroeconómicos imprevistos y riesgos sistémicos. 
                Las proyecciones no constituyen una garantía de rendimiento ni una recomendación directa de compra o venta.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

    except Exception as e:
      st.error(f"Error procesando métricas financieras: {str(e)}")

    # 2. INTELIGENCIA ARTIFICIAL RESILIENTE EN MODO JSON
    if datos_cargados:
      st.markdown("## 📋 Dictamen Estratégico de Inversión")

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
          data_json = generar_fallback_json(
              simb,
              capital_input,
              precio_actual,
              perfil_riesgo,
              horizonte,
              pe_ratio,
              volatilidad_anual,
          )

        # --- RENDERIZADO HIGH-END BASADO EN EL BOCETO DE PAINT ---
        col1, col2, col3, col4 = st.columns(4)

        with col1:
          st.markdown(
              f"""
              <div class="analysis-card">
                  <div class="analysis-card-title">1. Diagnóstico Fundamental y Técnico</div>
                  <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("diagnostico", ""))}</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        with col2:
          st.markdown(
              f"""
              <div class="analysis-card">
                  <div class="analysis-card-title">2. Viabilidad del Capital y Horizonte</div>
                  <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("viabilidad", ""))}</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        with col3:
          riesgos_txt = limpiar_texto_markdown(
              data_json.get("riesgos", "")
          ).replace("\n", "<br>")
          st.markdown(
              f"""
              <div class="analysis-card">
                  <div class="analysis-card-title">3. Factores de Riesgo Macro</div>
                  <div class="analysis-card-body">{riesgos_txt}</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        with col4:
          st.markdown(
              f"""
              <div class="analysis-card">
                  <div class="analysis-card-title">4. Veredicto Estratégico</div>
                  <div class="analysis-card-body">{limpiar_texto_markdown(data_json.get("fundamento", ""))}</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        st.markdown(
            "<div style='margin-top: 20px;'></div>", unsafe_allow_html=True
        )

        bot_col1, bot_col2 = st.columns([3, 1])

        with bot_col1:
          st.markdown(
              f"""
              <div class="decision-container">
                  <div class="analysis-card-title" style="font-size: 1.12rem; margin-bottom: 10px;">🎯 Decisión y Fundamento Ejecutivo</div>
                  <div class="analysis-card-body" style="font-size: 0.96rem; line-height: 1.65; color: #f8fafc;">
                      {limpiar_texto_markdown(data_json.get("fundamento", ""))}
                  </div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        with bot_col2:
          veredicto_clean = str(
              data_json.get("veredicto", "MANTENER EN OBSERVACIÓN")
          ).upper()
          if (
              "COMPRAR" in veredicto_clean
              and "DESESTIMAR" not in veredicto_clean
          ):
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

          st.markdown(
              f"""
              <div class="decision-badge-box {badge_class}">
                  <div style="font-size: 2.2rem; margin-bottom: 6px;">{badge_icon}</div>
                  <div style="font-weight: 800; letter-spacing: 0.08em;">{badge_text}</div>
              </div>
              """,
              unsafe_allow_html=True,
          )
