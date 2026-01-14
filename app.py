import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="AgroTech: Cristo Redentor",
    page_icon="🌱",
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

# Links RAW do GitHub (para download direto)
URL_CONFIG = "https://raw.githubusercontent.com/ChiaviniK/agrogencase/main/config_culturas.csv"
URL_HISTORICO = "https://raw.githubusercontent.com/ChiaviniK/agrogencase/main/historico_leituras.csv"

# --- Sidebar: Área de Download para Alunos ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tractor.png", width=80)
    st.title("AgroTech Case")
    st.markdown("---")
    st.header("📁 Material de Apoio")
    st.info("Baixe aqui as bases de dados para iniciar o desafio.")

    # Função para carregar dados do GitHub sem travar o app (Cache)
    @st.cache_data
    def load_data_from_github(url):
        try:
            return pd.read_csv(url)
        except:
            return None

    # Botão 1: Configuração
    df_config = load_data_from_github(URL_CONFIG)
    if df_config is not None:
        csv_config = df_config.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Regras (CSV)",
            data=csv_config,
            file_name="config_culturas.csv",
            mime="text/csv",
            help="Tabela com umidade ideal para cada cultura"
        )
    else:
        st.error("Erro ao carregar Config.")

    # Botão 2: Histórico
    df_hist = load_data_from_github(URL_HISTORICO)
    if df_hist is not None:
        csv_hist = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Histórico (CSV)",
            data=csv_hist,
            file_name="historico_leituras.csv",
            mime="text/csv",
            help="Dados de sensores dos últimos 30 dias"
        )
    else:
        st.error("Erro ao carregar Histórico.")
    
    st.markdown("---")
    st.caption("v1.2 - Case Study Build")

# --- Funções de Dados (Back-end Simulado) ---

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
    except Exception as e:
        return {"temp_atual": 25.0, "chuva_atual": 0.0, "chuva_prevista_3h": 0.0}

def get_soil_sensor_simulated():
    """Simula os dados do sensor de solo"""
    return {
        "umidade": np.random.uniform(30, 80),
        "ph": np.random.uniform(5.5, 7.0),
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

if st.button('🔄 Atualizar Telemetria em Tempo Real'):
    with st.spinner('Sincronizando sensores e satélite...'):
        weather = get_weather_data()
        soil = get_soil_sensor_simulated()
        st.toast('Dados atualizados!', icon='✅')
else:
    weather = get_weather_data()
    soil = get_soil_sensor_simulated()

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌡️ Temp. Ambiente", f"{weather['temp_atual']} °C")
with col2:
    color_rain = "inverse" if weather['chuva_prevista_3h'] > 0 else "normal"
    st.metric("🌧️ Chuva (3h)", f"{weather['chuva_prevista_3h']} mm", delta_color=color_rain)
with col3:
    st.metric("💧 Umidade Solo", f"{soil['umidade']:.1f} %")
with col4:
    status_bomba = "LIGADA" if soil['bomba_ativa'] else "DESLIGADA"
    st.metric("⚙️ Status Bomba", status_bomba)

# --- Engine de Decisão ---
st.subheader("🧠 Diagnóstico da IA")

umidade_ideal_min = 60.0
chuva_limite = 5.0 

with st.expander("Ver Detalhes da Decisão Automática", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Regras Ativas:**")
        st.code(f"Umidade Mínima: {umidade_ideal_min}%\nChuva Limite:   {chuva_limite}mm")
    
    with col_b:
        if soil['umidade'] < umidade_ideal_min:
            if weather['chuva_prevista_3h'] >= chuva_limite:
                st.success("🚫 SOLO SECO + CHUVA À VISTA. IRRIGAÇÃO ABORTADA (ECONOMIA).")
            else:
                st.warning("💦 SOLO SECO. ACIONANDO IRRIGAÇÃO...")
        else:
            st.info("✅ UMIDADE IDEAL. NENHUMA AÇÃO NECESSÁRIA.")

# --- Gráfico ---
st.divider()
st.subheader("📊 Monitoramento (Últimas 24h)")
chart_data = pd.DataFrame(
    np.random.randn(24, 2) + [soil['umidade'], weather['temp_atual']],
    columns=['Umidade Solo', 'Temperatura']
)
st.line_chart(chart_data)

st.subheader("🕵️ Auditoria de Qualidade dos Dados")
st.caption("Se este gráfico mostrar picos gigantes, seus dados estão sujos!")

# Carrega os dados (simulando o que o aluno faria)
# No código real do aluno, eles devem carregar o 'df_limpo', não o sujo.
df_audit = load_data_from_github("https://raw.githubusercontent.com/.../historico_leituras_sujo.csv")

if df_audit is not None:
    # Converter para datetime para o gráfico funcionar
    df_audit['timestamp'] = pd.to_datetime(df_audit['timestamp'])
    
    # Gráfico que vai revelar os erros (Picos de 500 graus)
    st.line_chart(df_audit.set_index('timestamp')['temp_ambiente'])
    
    st.warning("Dica: Se você vê temperaturas de 200°C+ acima, você precisa implementar um filtro de limpeza no Python!")
