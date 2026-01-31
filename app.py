import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# --- Configuração da Página ---
st.set_page_config(
    page_title="AgroTech: Smart Irrigation",
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

# --- Configurações do Local (Cristo Redentor, RJ - Exemplo) ---
LAT = -22.9519
LON = -43.2105
NOME_LOCAL = "Rio de Janeiro - Cristo Redentor"

# --- LINKS DO GITHUB ---
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
    
    @st.cache_data
    def load_data(url):
        try:
            return pd.read_csv(url)
        except:
            return None

    # Botões de Download (Mantidos conforme seu pedido)
    df_config = load_data(URL_CONFIG)
    if df_config is not None:
        st.download_button("📥 1. Regras de Cultura (CSV)", data=df_config.to_csv(index=False).encode('utf-8'), file_name="config_culturas.csv", mime="text/csv")

    df_tarifas = load_data(URL_TARIFAS)
    if df_tarifas is not None:
        st.download_button("📥 2. Tarifas de Energia (CSV)", data=df_tarifas.to_csv(index=False).encode('utf-8'), file_name="tarifas_energia.csv", mime="text/csv")

    df_sujo = load_data(URL_HISTORICO_SUJO)
    if df_sujo is not None:
        st.download_button("📥 3. Histórico Sensores (CSV)", data=df_sujo.to_csv(index=False).encode('utf-8'), file_name="historico_leituras_sujo.csv", mime="text/csv")
    
    st.markdown("---")
    st.caption("v3.0 - Historical Data Connected")

# ==============================================================================
# 📡 FUNÇÕES DE DADOS (API REAL + SIMULAÇÃO)
# ==============================================================================

def get_realtime_weather():
    """Busca dados REAIS de previsão imediata (Forecast API)"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,rain&hourly=rain&timezone=America%2FSao_Paulo&forecast_days=1"
        response = requests.get(url, timeout=3)
        data = response.json()
        return {
            "temp_atual": data['current']['temperature_2m'],
            "chuva_atual": data['current']['rain'],
            "chuva_prevista_3h": sum(data['hourly']['rain'][0:3])
        }
    except:
        return {"temp_atual": 25.0, "chuva_atual": 0.0, "chuva_prevista_3h": 0.0}

@st.cache_data(ttl=86400) # Cache de 24h para não pesar na API
def get_history_api(lat, lon, years=3):
    """
    Busca histórico de 3 anos na Open-Meteo Archive API.
    Retorna um DataFrame limpo com Data, Temp Max e Chuva.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
    
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,precipitation_sum&timezone=America%2FSao_Paulo"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        # Cria DataFrame
        df = pd.DataFrame({
            'Data': data['daily']['time'],
            'Temp_Max': data['daily']['temperature_2m_max'],
            'Chuva_mm': data['daily']['precipitation_sum']
        })
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except Exception as e:
        st.error(f"Erro na API Histórica: {e}")
        return pd.DataFrame()

def get_soil_sensor_simulated():
    """Simula sensor de solo"""
    return {
        "umidade": np.random.uniform(30, 80),
        "bomba_ativa": np.random.choice([True, False])
    }

# ==============================================================================
# 🖥️ INTERFACE PRINCIPAL
# ==============================================================================

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🌱 Smart Irrigation System")
    st.subheader(f"📍 Unidade: {NOME_LOCAL}")
with col_logo:
    st.map(pd.DataFrame({'lat': [LAT], 'lon': [LON]}), zoom=13)

st.divider()

# Criação de Abas para organizar o conteúdo
tab_realtime, tab_history, tab_audit = st.tabs([
    "🎛️ Monitoramento em Tempo Real", 
    "📅 Análise Histórica (3 Anos)", 
    "🕵️ Auditoria de Dados"
])

# --- ABA 1: TEMPO REAL ---
with tab_realtime:
    col_btn, _ = st.columns([1, 3])
    if col_btn.button('🔄 Atualizar Sensores'):
        weather = get_realtime_weather()
        soil = get_soil_sensor_simulated()
        st.toast('Dados sincronizados!', icon='📡')
    else:
        weather = get_realtime_weather()
        soil = get_soil_sensor_simulated()

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("🌡️ Temp. Ambiente", f"{weather['temp_atual']} °C")
    with k2: st.metric("🌧️ Chuva (3h)", f"{weather['chuva_prevista_3h']} mm")
    with k3: st.metric("💧 Umidade Solo", f"{soil['umidade']:.1f} %")
    with k4: st.metric("⚙️ Status Bomba", "LIGADA 🟢" if soil['bomba_ativa'] else "OFF 🔴")

    st.info("🧠 **IA Decision:** Sistema operando normalmente conforme regras de negócio.")

# --- ABA 2: HISTÓRICO 3 ANOS (NOVIDADE) ---
with tab_history:
    st.header("Histórico Climático da Região")
    st.markdown("Dados extraídos da API *Open-Meteo Archive* referente aos últimos 3 anos.")
    
    

    with st.spinner("Baixando dados históricos (pode levar alguns segundos)..."):
        df_hist = get_history_api(LAT, LON)
    
    if not df_hist.empty:
        # Filtro de Ano
        df_hist['Ano'] = df_hist['Data'].dt.year
        anos = sorted(df_hist['Ano'].unique())
        ano_sel = st.multiselect("Selecione os Anos para visualizar:", anos, default=anos)
        
        df_filtered = df_hist[df_hist['Ano'].isin(ano_sel)]
        
        # Gráficos
        st.subheader("💧 Regime de Chuvas (Precipitação)")
        st.bar_chart(df_filtered, x='Data', y='Chuva_mm', color='#4682b4')
        
        st.subheader("🔥 Temperaturas Máximas")
        st.line_chart(df_filtered, x='Data', y='Temp_Max', color='#ff4b4b')
        
        # Download do Histórico Limpo
        st.divider()
        csv_hist = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Base Histórica Completa (.csv)", csv_hist, "historico_3anos_limpo.csv", "text/csv")
    else:
        st.warning("Não foi possível carregar o histórico no momento.")

# --- ABA 3: AUDITORIA (Mantida do seu código original) ---
with tab_audit:
    st.header("Auditoria de Qualidade (Data Quality)")
    st.markdown("Visualização dos dados brutos do arquivo `historico_leituras_sujo.csv`.")

    if df_sujo is not None:
        df_viz = df_sujo.copy()
        # Tenta converter timestamp, se falhar, ignora erros para não quebrar o app
        df_viz['timestamp'] = pd.to_datetime(df_viz['timestamp'], errors='coerce')
        
        mostrar_erro = st.checkbox("🔍 Revelar anomalias (Spoiler)")
        
        if mostrar_erro:
            # Filtra apenas dados válidos para plotar
            df_plot = df_viz.dropna(subset=['timestamp'])
            st.line_chart(df_plot.set_index('timestamp')['temp_ambiente'])
            st.warning("⚠️ ALERTA: Picos de temperatura irreais (>100°C) detectados.")
        else:
            st.dataframe(df_viz.head(10), use_container_width=True)
            st.caption("Amostra das primeiras 10 linhas.")
