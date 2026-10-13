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
# CONFIGURACIÓN DE PÁGINA FINTECH PROFESIONAL
# ==============================================================================
st.set_page_config(
    page_title="Terminal Inteligente de Inversiones & Forex",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS CSS HIGH-END INSTITUCIONAL (GLASSMORPHISM)
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
        border:
