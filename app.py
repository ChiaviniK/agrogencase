import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="AgroTech: Case Study Hub",
    page_icon="🚜",
    layout="wide"
)

# --- Estilo CSS Minimalista ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Configurações do Local (Cristo Redentor, RJ) ---
LAT = -22.9519
LON = -43.2105
NOME_LOCAL = "Rio de Janeiro - Cristo Redentor"

# --- LINKS DO GITHUB (Atualize com seu usuário se necessário) ---
# DICA: Use o link "Raw" do GitHub para funcionar o download direto
BASE_URL = "https://raw.githubusercontent.com/ChiaviniK/agrogencase/main"
URL_CONFIG = f"{BASE_URL}/config_culturas.csv"
URL_TARIFAS = f"{BASE_URL}/tarifas_energia.csv"
URL_HISTORICO_SUJO = f"{BASE_URL}/historico_leituras_sujo.csv"

# --- SIDEBAR: Área do Aluno (Downloads) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tractor.png", width=80)
    st.title("AgroTech Case")
    st.markdown("---")
    st.header("📁 Material de Apoio")
    st.info("Baixe as bases de dados para resolver o desafio:")

    # Função Helper para Download
    @st.cache_data
    def load_data(url):
        try:
            return pd.read_csv(url)
        except:
            return None

    # 1. Regras (Config)
    df_config = load_data(URL_CONFIG)
    if df_config is not None:
        st.download_button(
            "📥 1. Regras de Cultura (CSV)",
            data=df_config.to_csv(index=False).encode('utf-8'),
            file_name="config_culturas.csv",
            mime="text/csv"
        )

    # 2. Tarifas (Energia) - NOVO!
    df_tarifas = load_data(URL_TARIFAS)
    if df_tarifas is not None:
        st.download_button(
            "📥 2. Tarifas de Energia (CSV)",
            data=df_tarifas.to_csv(index=False).encode('utf-8'),
            file_name="tarifas_energia.csv",
            mime="text/csv",
            help="Use para otimizar custos (Tarifa Branca)"
        )

    # 3. Histórico (Sujo) - ATUALIZADO!
    df_sujo = load_data(URL_HISTORICO_SUJO)
    if df_sujo is not None:
        st.download_button(
            "📥 3. Histórico Sensores (CSV)",
            data=df_sujo.to_csv(index=False).encode('utf-8'),
            file_name="historico_leituras_sujo.csv",
            mime="text/csv",
            help="ATENÇÃO: Contém dados brutos que precisam de tratamento!"
        )
    else:
        st.error("Erro ao carregar CSVs. Verifique o GitHub.")
    
    st.markdown("---")
    st.caption("v2.0 - Pleno Level Challenge")

# --- Funções de Dados (Simulação) ---

def get_weather_data():
    """Busca dados REAIS de clima da API Open-Meteo"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,rain&hourly=rain&timezone=America%2FSao_Paulo&forecast_days=1"
        response = requests.get(url)
        data = response.json()
        return {
            "temp_atual": data['current']['temperature_2m'],
            "chuva_atual": data['current']['rain'],
            "chuva_prevista_3h": sum(data['hourly']['rain'][0:3])
        }
    except:
        return {"temp_atual": 25.0, "chuva_atual": 0.0, "chuva_prevista_3h": 0.0}

def get_soil_sensor_simulated():
    """Simula sensor"""
    return {
        "umidade": np.random.uniform(30, 80),
        "bomba_ativa": np.random.choice([True, False])
    }

# --- Interface Principal ---

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🌱 Smart Irrigation System")
    st.subheader(f"📍 Unidade: {NOME_LOCAL}")
with col_logo:
    st.map(pd.DataFrame({'lat': [LAT], 'lon': [LON]}), zoom=13)

st.divider()

# Botão Refresh
if st.button('🔄 Atualizar Telemetria'):
    with st.spinner('Conectando satélite...'):
        weather = get_weather_data()
        soil = get_soil_sensor_simulated()
        st.toast('Dados atualizados!', icon='✅')
else:
    weather = get_weather_data()
    soil = get_soil_sensor_simulated()

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("🌡️ Temp. Ambiente", f"{weather['temp_atual']} °C")
with col2: st.metric("🌧️ Chuva (3h)", f"{weather['chuva_prevista_3h']} mm")
with col3: st.metric("💧 Umidade Solo", f"{soil['umidade']:.1f} %")
with col4: st.metric("⚙️ Status Bomba", "LIGADA" if soil['bomba_ativa'] else "OFF")

# --- Engine de Decisão ---
st.subheader("🧠 Diagnóstico da IA")
st.info("O sistema está operando com base nas regras de negócio carregadas.")

# --- Auditoria de Qualidade de Dados (Visualização do Problema) ---
st.divider()
st.subheader("🕵️ Auditoria de Qualidade (Data Quality)")
st.markdown("Visualização dos dados brutos do arquivo `historico_leituras_sujo.csv`.")

if df_sujo is not None:
    # Convertendo data para o gráfico funcionar
    df_viz = df_sujo.copy()
    df_viz['timestamp'] = pd.to_datetime(df_viz['timestamp'])
    
    # Checkbox para dar spoiler do erro
    mostrar_erro = st.checkbox("🔍 Revelar anomalias nos dados (Spoiler)")
    
    if mostrar_erro:
        st.line_chart(df_viz.set_index('timestamp')['temp_ambiente'])
        st.warning("⚠️ ALERTA: Detectamos picos de temperatura irreais (>100°C). Sua equipe precisa filtrar isso!")
    else:
        # Mostra apenas as primeiras linhas para não assustar de cara
        st.dataframe(df_viz.head(10))
        st.caption("Amostra das primeiras 10 linhas.")
