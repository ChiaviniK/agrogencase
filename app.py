import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EcoFlow | Smart Irrigation", page_icon="💧", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f8ff; color: #004d40; }
    h1, h2 { color: #00695c !important; }
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 10px; padding: 15px;
        border: 1px solid #b2dfdb; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 📡 MOTOR 1: API DE PREVISÃO DO TEMPO (Open-Meteo Forecast)
# ==============================================================================
@st.cache_data(ttl=3600) # Atualiza a cada 1 hora
def get_forecast_data(lat, lon):
    """
    Busca a previsão do tempo para os próximos 7 dias.
    Essencial para o sistema decidir se irriga ou espera a chuva.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,precipitation_probability_max&timezone=America%2FSao_Paulo"
    
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            df = pd.DataFrame({
                'Data': data['daily']['time'],
                'Chuva_mm': data['daily']['precipitation_sum'],
                'Prob_Chuva_%': data['daily']['precipitation_probability_max']
            })
            return df
    except:
        pass
    return pd.DataFrame()

# ==============================================================================
# 📡 MOTOR 2: API HISTÓRICA (Para Planejamento)
# ==============================================================================
@st.cache_data
def get_historical_rain(lat, lon):
    """Busca histórico de chuvas do ano passado para comparação."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - pd.Timedelta(days=365)).strftime("%Y-%m-%d")
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    
    try:
        r = requests.get(url)
        data = r.json()
        df = pd.DataFrame({'Data': data['daily']['time'], 'Chuva_mm': data['daily']['precipitation_sum']})
        return df
    except: return pd.DataFrame()

# ==============================================================================
# 🔌 SIMULADOR DE SENSORES IOT (Umidade do Solo)
# ==============================================================================
def ler_sensor_umidade():
    """Simula a leitura de um sensor capacitivo no solo (0-100%)."""
    # Gera um valor aleatório realista (ex: solo secando)
    return np.random.randint(20, 45) # Entre 20% (Seco) e 45% (Úmido)

# ==============================================================================
# 🖥️ INTERFACE
# ==============================================================================
st.sidebar.image("https://img.icons8.com/fluency/96/sprinkler.png", width=80)
st.sidebar.title("EcoFlow")
st.sidebar.caption("Irrigação Inteligente")
st.sidebar.markdown("---")

# Configuração da Fazenda (Input do Usuário)
st.sidebar.subheader("📍 Configuração")
cidade = st.sidebar.selectbox("Local:", ["Ribeirão Preto (SP)", "Petrolina (PE)", "Sorriso (MT)"])

# Coordenadas fixas para exemplo (Poderia vir de uma API de Geocoding)
COORDS = {
    "Ribeirão Preto (SP)": (-21.17, -47.81),
    "Petrolina (PE)": (-9.38, -40.50),
    "Sorriso (MT)": (-12.54, -55.72)
}
LAT, LON = COORDS[cidade]

st.title(f"Sistema de Irrigação: {cidade}")

tab_control, tab_forecast, tab_hist = st.tabs(["🎛️ Controle (IoT)", "🌦️ Previsão (Smart)", "📊 Histórico"])

# --- TAB 1: CONTROLE EM TEMPO REAL ---
with tab_control:
    st.header("Monitoramento em Tempo Real")
    
    # 1. Leitura dos Sensores
    umidade_solo = ler_sensor_umidade()
    status_bomba = "DESLIGADA"
    cor_status = "off"
    
    # LÓGICA SMART (O Coração do Projeto)
    # Regra: Se umidade < 30% LIGAR, mas só se NÃO for chover hoje.
    
    df_previsao = get_forecast_data(LAT, LON)
    chuva_hoje = 0
    if not df_previsao.empty:
        chuva_hoje = df_previsao.iloc[0]['Chuva_mm']
    
    decisao = ""
    if umidade_solo < 30:
        if chuva_hoje > 5:
            decisao = "⚠️ Solo Seco, mas CHUVA PREVISTA. Irrigação suspensa (Economia)."
            status_bomba = "DESLIGADA (Smart Mode)"
        else:
            decisao = "💧 Solo Seco. Iniciando Irrigação..."
            status_bomba = "LIGADA 🟢"
    else:
        decisao = "✅ Umidade Ideal. Sistema em Standby."
        status_bomba = "DESLIGADA"

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Umidade do Solo", f"{umidade_solo}%", delta="-2% (última hora)")
    c2.metric("Status da Bomba", status_bomba)
    c3.metric("Previsão Chuva (Hoje)", f"{chuva_hoje} mm")
    
    st.info(f"🤖 **IA Decision:** {decisao}")
    
    # Gauge (Velocímetro) da Umidade
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = umidade_solo,
        title = {'text': "Umidade do Solo (%)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#ffcccb"},  # Seco (Vermelho claro)
                {'range': [30, 70], 'color': "#90ee90"}, # Bom (Verde claro)
                {'range': [70, 100], 'color': "#add8e6"} # Encharcado (Azul claro)
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 30
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: PREVISÃO (API) ---
with tab_forecast:
    st.header("Planejamento Hídrico (7 Dias)")
    if not df_previsao.empty:
        # Gráfico de Previsão
        fig_prev = px.bar(
            df_previsao, x='Data', y='Chuva_mm',
            title="Previsão de Precipitação (Open-Meteo API)",
            text='Prob_Chuva_%',
            labels={'Chuva_mm': 'Chuva Esperada (mm)', 'Prob_Chuva_%': 'Probabilidade'}
        )
        fig_prev.update_traces(marker_color='#4682b4', texttemplate='%{text}% Prob.')
        st.plotly_chart(fig_prev, use_container_width=True)
        
        st.dataframe(df_previsao, use_container_width=True)
    else:
        st.error("Erro na API de Previsão.")

# --- TAB 3: HISTÓRICO ---
with tab_hist:
    st.header("Histórico da Região (1 Ano)")
    with st.spinner("Carregando dados históricos..."):
        df_hist = get_historical_rain(LAT, LON)
    
    if not df_hist.empty:
        fig_hist = px.line(df_hist, x='Data', y='Chuva_mm', title="Regime de Chuvas (Últimos 12 Meses)")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.download_button("📥 Baixar Histórico (.csv)", df_hist.to_csv().encode('utf-8'), "historico_chuvas.csv")
    else:
        st.warning("Dados históricos indisponíveis.")
