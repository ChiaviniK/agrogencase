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
    .css-18e3th9 {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Configurações do Local (Cristo Redentor, RJ) ---
LAT = -22.9519
LON = -43.2105
NOME_LOCAL = "Rio de Janeiro - Cristo Redentor"

# --- Funções de Dados ---

def get_weather_data():
    """
    Busca dados REAIS de clima da API Open-Meteo para o Cristo Redentor.
    Documentação: https://open-meteo.com/
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,rain&hourly=rain&timezone=America%2FSao_Paulo&forecast_days=1"
        response = requests.get(url)
        data = response.json()
        
        return {
            "temp_atual": data['current']['temperature_2m'],
            "chuva_atual": data['current']['rain'],
            # Soma a chuva prevista para as próximas 3 horas
            "chuva_prevista_3h": sum(data['hourly']['rain'][0:3])
        }
    except Exception as e:
        st.error(f"Erro ao conectar na API de Clima: {e}")
        return {"temp_atual": 25.0, "chuva_atual": 0.0, "chuva_prevista_3h": 0.0}

def get_soil_sensor_simulated():
    """
    Simula os dados do sensor de solo (já que não temos um sensor físico lá).
    """
    return {
        "umidade": np.random.uniform(30, 80), # 30% a 80%
        "ph": np.random.uniform(5.5, 7.0),
        "bomba_ativa": np.random.choice([True, False])
    }

# --- Interface do Dashboard ---

# Cabeçalho com duas colunas
col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🌱 Smart Irrigation System")
    st.subheader(f"📍 Unidade: {NOME_LOCAL}")
    st.caption(f"Coordenadas: {LAT}, {LON}")
with col_logo:
    # Mostra um mapa estático simples da localização
    st.map(pd.DataFrame({'lat': [LAT], 'lon': [LON]}), zoom=13)

st.divider()

# Botão de Atualização Manual
if st.button('🔄 Atualizar Telemetria'):
    with st.spinner('Buscando dados via Satélite...'):
        weather = get_weather_data()
        soil = get_soil_sensor_simulated()
        st.toast('Dados atualizados com sucesso!', icon='✅')
else:
    # Carregamento inicial
    weather = get_weather_data()
    soil = get_soil_sensor_simulated()

# --- KPIs (Indicadores) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="🌡️ Temp. Ambiente (Real)", value=f"{weather['temp_atual']} °C")

with col2:
    color_rain = "inverse" if weather['chuva_prevista_3h'] > 0 else "normal"
    st.metric(label="🌧️ Previsão Chuva (3h)", value=f"{weather['chuva_prevista_3h']} mm", delta_color=color_rain)

with col3:
    st.metric(label="💧 Umidade Solo (Sensor)", value=f"{soil['umidade']:.1f} %")

with col4:
    status_bomba = "LIGADA" if soil['bomba_ativa'] else "DESLIGADA"
    st.metric(label="⚙️ Status Bomba", value=status_bomba)

# --- Engine de Decisão (O "Cérebro" do Aluno) ---
st.subheader("🧠 Análise da IA (Decisão de Irrigação)")

# Lógica simples para demonstrar aos alunos
umidade_ideal_min = 60.0
chuva_limite = 5.0 # Se for chover mais que 5mm, não irriga

with st.expander("Ver Detalhes da Decisão", expanded=True):
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write(f"**Regra de Negócio:**")
        st.write(f"- Umidade Mínima: `{umidade_ideal_min}%`")
        st.write(f"- Limite Chuva (Economia): `{chuva_limite}mm`")
    
    with col_b:
        decision_msg = ""
        decision_type = ""
        
        if soil['umidade'] < umidade_ideal_min:
            if weather['chuva_prevista_3h'] >= chuva_limite:
                decision_type = "success"
                decision_msg = "🚫 SOLO SECO, MAS COM PREVISÃO DE CHUVA. IRRIGAÇÃO ABORTADA (ECONOMIA DE ÁGUA)."
            else:
                decision_type = "warning"
                decision_msg = "💦 SOLO SECO E SEM CHUVA. ACIONANDO IRRIGAÇÃO..."
        else:
            decision_type = "info"
            decision_msg = "✅ NÍVEIS DE UMIDADE ADEQUADOS. NENHUMA AÇÃO NECESSÁRIA."
            
        if decision_type == "success":
            st.success(decision_msg)
        elif decision_type == "warning":
            st.warning(decision_msg)
        else:
            st.info(decision_msg)

# --- Gráfico de Monitoramento ---
st.divider()
st.subheader("📊 Histórico de Umidade (Últimas 24h)")
chart_data = pd.DataFrame(
    np.random.randn(24, 2) + [soil['umidade'], weather['temp_atual']],
    columns=['Umidade Solo', 'Temperatura']
)
st.line_chart(chart_data)

# --- Footer ---
st.markdown("---")
st.markdown("🔒 *Sistema Seguro - Conectado via Open-Meteo API*")
