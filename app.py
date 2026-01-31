import streamlit as st
import pandas as pd
import numpy as np
import requests
import altair as alt  # <--- IMPORTAÇÃO NECESSÁRIA ADICIONADA
from datetime import datetime, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO GERAL
# ==============================================================================
st.set_page_config(
    page_title="AgroTech: Smart Irrigation",
    page_icon="🚜",
    layout="wide"
)

# Estilo CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Configurações do Local ---
LAT = -12.5425
LON = -55.7214
NOME_LOCAL = "Sorriso - Mato Grosso (Capital do Agro)"

# --- LINKS DO GITHUB ---
BASE_URL = "https://raw.githubusercontent.com/ChiaviniK/agrogencase/main"
URL_CONFIG = f"{BASE_URL}/config_culturas.csv"
URL_TARIFAS = f"{BASE_URL}/tarifas_energia.csv"
URL_HISTORICO_SUJO = f"{BASE_URL}/historico_leituras_sujo.csv"

# ==============================================================================
# 2. SIDEBAR (AREA DO ALUNO)
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tractor.png", width=80)
    st.title("AgroTech Case")
    st.caption("v4.1 Fixed Edition")
    st.markdown("---")
    
    st.header("📁 Material de Apoio")
    st.info("Bases de dados oficiais para o desafio:")

    @st.cache_data
    def load_data(url):
        try:
            return pd.read_csv(url)
        except: return None

    df_config = load_data(URL_CONFIG)
    if df_config is not None:
        st.download_button("📥 1. Regras de Cultura (CSV)", df_config.to_csv(index=False).encode('utf-8'), "config_culturas.csv", "text/csv")

    df_tarifas = load_data(URL_TARIFAS)
    if df_tarifas is not None:
        st.download_button("📥 2. Tarifas de Energia (CSV)", df_tarifas.to_csv(index=False).encode('utf-8'), "tarifas_energia.csv", "text/csv")

    df_sujo = load_data(URL_HISTORICO_SUJO)
    if df_sujo is not None:
        st.download_button("📥 3. Histórico Sensores (CSV)", df_sujo.to_csv(index=False).encode('utf-8'), "historico_leituras_sujo.csv", "text/csv")

# ==============================================================================
# 3. MOTORES DE DADOS (BACKEND)
# ==============================================================================

def get_realtime_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,rain&hourly=rain&timezone=America%2FSao_Paulo&forecast_days=1"
        r = requests.get(url, timeout=3)
        data = r.json()
        return {
            "temp_atual": data['current']['temperature_2m'],
            "chuva_atual": data['current']['rain'],
            "chuva_prevista_3h": sum(data['hourly']['rain'][0:3])
        }
    except:
        return {"temp_atual": 28.5, "chuva_atual": 0.0, "chuva_prevista_3h": 0.0}

@st.cache_data(ttl=86400)
def get_history_api(lat, lon, years=3):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,precipitation_sum&timezone=America%2FSao_Paulo"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        df = pd.DataFrame({
            'Data': data['daily']['time'],
            'Temp_Max': data['daily']['temperature_2m_max'],
            'Chuva_mm': data['daily']['precipitation_sum']
        })
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except: return pd.DataFrame()

def get_soil_sensor_simulated():
    return {"umidade": np.random.uniform(25, 60), "bomba_ativa": np.random.choice([True, False])}

def calcular_roi(df_tarifas):
    t_ponta, t_fora = 1.85, 0.65 
    if df_tarifas is not None:
        try:
            if 'posto' in df_tarifas.columns and 'valor' in df_tarifas.columns:
                t_ponta = df_tarifas[df_tarifas['posto'].str.contains('Ponta', case=False, na=False)]['valor'].mean()
                t_fora = df_tarifas[df_tarifas['posto'].str.contains('Fora', case=False, na=False)]['valor'].mean()
        except: pass
    custo_conv = (2 * 30) * 15 * t_ponta 
    custo_smart = (2 * 30 * 0.6) * 15 * t_fora
    return custo_conv, custo_smart

# ==============================================================================
# 4. INTERFACE PRINCIPAL
# ==============================================================================

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🌱 Smart Irrigation System")
    st.subheader(f"📍 Unidade: {NOME_LOCAL}")
with col_logo:
    st.map(pd.DataFrame({'lat': [LAT], 'lon': [LON]}), zoom=13)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "🎛️ Monitoramento", 
    "📅 Histórico (3 Anos)", 
    "💰 Gestão Financeira", 
    "🕵️ Auditoria de Dados"
])

# --- ABA 1: TEMPO REAL ---
with tab1:
    col_btn, _ = st.columns([1, 3])
    if col_btn.button('🔄 Sincronizar Sensores'):
        weather = get_realtime_weather()
        soil = get_soil_sensor_simulated()
        st.toast('Telemetria atualizada!', icon='📡')
    else:
        weather = get_realtime_weather()
        soil = get_soil_sensor_simulated()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("🌡️ Temp. Ambiente", f"{weather['temp_atual']} °C")
    with k2: st.metric("🌧️ Chuva (3h)", f"{weather['chuva_prevista_3h']} mm")
    with k3: st.metric("💧 Umidade Solo", f"{soil['umidade']:.1f} %")
    with k4: st.metric("⚙️ Bomba", "LIGADA 🟢" if soil['bomba_ativa'] else "STANDBY 🟡")

    if weather['chuva_prevista_3h'] > 2:
        msg, tipo = "⚠️ Chuva prevista. Irrigação suspensa.", "warning"
    elif soil['umidade'] < 30:
        msg, tipo = "💧 Solo seco. Irrigação ativada.", "success"
    else:
        msg, tipo = "✅ Sistema estável.", "info"
    st.chat_message("assistant").write(f"**IA Diagnosis:** {msg}")

# --- ABA 2: HISTÓRICO ---
with tab2:
    st.header("Histórico Climático Regional")
    with st.spinner("Baixando dados..."):
        df_hist = get_history_api(LAT, LON)
    
    if not df_hist.empty:
        df_hist['Ano'] = df_hist['Data'].dt.year
        anos = sorted(df_hist['Ano'].unique())
        col_filtro, _ = st.columns([1, 2])
        ano_sel = col_filtro.multiselect("Filtrar Anos:", anos, default=anos)
        df_filtered = df_hist[df_hist['Ano'].isin(ano_sel)]
        
        st.subheader("💧 Precipitação")
        st.bar_chart(df_filtered, x='Data', y='Chuva_mm', color='#4682b4')
        st.subheader("🔥 Temperaturas")
        st.line_chart(df_filtered, x='Data', y='Temp_Max', color='#ff4b4b')
        st.download_button("📥 Baixar Histórico (.csv)", df_hist.to_csv(index=False).encode('utf-8'), "historico_3anos.csv")

# --- ABA 3: FINANCEIRO (ROI) - CORRIGIDA ---
with tab3:
    st.header("Análise de Viabilidade (ROI)")
    custo_antigo, custo_novo = calcular_roi(df_tarifas)
    economia = custo_antigo - custo_novo
    perc_eco = (economia / custo_antigo) * 100
    
    c_fin1, c_fin2, c_fin3 = st.columns(3)
    c_fin1.metric("Custo Mensal (Convencional)", f"R$ {custo_antigo:,.2f}")
    c_fin2.metric("Custo Mensal (Smart)", f"R$ {custo_novo:,.2f}", delta=f"Economia: {perc_eco:.0f}%")
    c_fin3.metric("Poupança Anual", f"R$ {(economia*12):,.2f}")
    
    st.divider()
    
    col_g, col_txt = st.columns([2, 1])
    with col_g:
        df_chart = pd.DataFrame({"Sistema": ["Convencional", "Smart"], "Custo (R$)": [custo_antigo, custo_novo]})
        
        # --- CORREÇÃO DO ERRO AQUI USANDO ALTAIR ---
        chart_custo = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X('Sistema', sort=None),
            y='Custo (R$)',
            color=alt.Color('Sistema', scale=alt.Scale(domain=['Convencional', 'Smart'], range=['#ff4b4b', '#00d26a'])),
            tooltip=['Sistema', 'Custo (R$)']
        ).properties(title="Redução de Custos Operacionais")
        
        st.altair_chart(chart_custo, use_container_width=True)
        # -------------------------------------------
        
    with col_txt:
        st.info("**Ganhos:**\n1. Tarifa Branca (Fora Ponta)\n2. Economia Hídrica (Chuva)")

# --- ABA 4: AUDITORIA ---
with tab4:
    st.header("Auditoria de Qualidade")
    if df_sujo is not None:
        df_viz = df_sujo.copy()
        df_viz['timestamp'] = pd.to_datetime(df_viz['timestamp'], errors='coerce')
        if st.checkbox("🔍 Revelar Anomalias"):
            df_plot = df_viz.dropna(subset=['timestamp'])
            st.line_chart(df_plot.set_index('timestamp')['temp_ambiente'])
            st.warning("⚠️ ALERTA: Sensores >100°C detectados.")
        else:
            st.dataframe(df_viz.head(10), use_container_width=True)
