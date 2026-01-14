import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="AgroTech Monitor",
    page_icon="🌱",
    layout="wide"
)

# --- Estilo CSS Minimalista (Opcional, para dar um 'tchan') ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Título e Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🌱 AgroTech: Controle de Irrigação")
    st.markdown("Monitoramento em tempo real do Setor A (Soja)")
with col2:
    st.image("https://img.icons8.com/color/96/tractor.png", width=80) # Icone ilustrativo

st.divider()

# --- Simulação de Dados (Aqui entraria a requisição à API/Banco do grupo) ---
# Função para simular o que vem do Back-end
def get_sensor_data():
    # Simula dados aleatórios para o visual
    return {
        "umidade": np.random.uniform(40, 90),
        "temperatura": np.random.uniform(20, 35),
        "chuva_prevista": np.random.choice([0, 0, 0, 5, 12, 0]), # Chance maior de não chover
        "status_bomba": np.random.choice([True, False])
    }

# Botão de atualizar (Simula o Real-time)
if st.button('🔄 Atualizar Dados dos Sensores'):
    data = get_sensor_data()
else:
    data = get_sensor_data() # Carrega na primeira vez

# --- Painel de Indicadores (KPIs) ---
col_u, col_t, col_c, col_s = st.columns(4)

with col_u:
    st.metric(label="💧 Umidade do Solo", value=f"{data['umidade']:.1f}%", delta="-2% nas últimas 2h")

with col_t:
    st.metric(label="🌡️ Temperatura", value=f"{data['temperatura']:.1f}°C")

with col_c:
    # Lógica visual simples
    chuva = data['chuva_prevista']
    cor_chuva = "off" if chuva == 0 else "normal"
    st.metric(label="🌧️ Chuva (3h)", value=f"{chuva} mm", delta_color=cor_chuva)

with col_s:
    # Status da Bomba
    status = "LIGADA" if data['status_bomba'] else "DESLIGADA"
    cor_status = "normal" if data['status_bomba'] else "off" # Verde se ligada, cinza se desli.
    st.metric(label="⚙️ Bomba de Irrigação", value=status)

# --- Lógica de Decisão Visual ---
# Aqui o aluno vê se o sistema tomou a decisão certa
st.subheader("Diagnóstico do Sistema")

if data['umidade'] < 60 and data['chuva_prevista'] < 5:
    st.error("⚠️ ALERTA: Umidade Baixa. Irrigação deve ser ativada!")
    if not data['status_bomba']:
        st.caption("🔴 Falha: A bomba deveria estar ligada e não está.")
elif data['umidade'] < 60 and data['chuva_prevista'] >= 5:
    st.success("✅ ECONOMIA: Solo seco, mas chuva prevista. Irrigação suspensa.")
else:
    st.info("✅ Sistema em Stand-by. Condições ideais.")

# --- Gráfico de Histórico (Simulado) ---
st.divider()
st.subheader("Histórico das últimas 24h")

# Criando dados fictícios para o gráfico
chart_data = pd.DataFrame({
    'Horário': pd.date_range(start=datetime.now(), periods=24, freq='H'),
    'Umidade (%)': np.random.uniform(50, 80, 24),
    'Temperatura (°C)': np.random.uniform(22, 30, 24)
})

st.line_chart(chart_data.set_index('Horário'))

# --- Rodapé ---
st.markdown("---")
st.markdown("Developed for AgroTech Case Study | 2024")