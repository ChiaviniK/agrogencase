import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# --- (MANTENHA TODAS AS IMPORTAÇÕES E CONFIGURAÇÕES INICIAIS IGUAIS) ---
# ... (Código anterior de Config, CSS, Sidebar, Funções de API e Simulação) ...

# ==============================================================================
# 💰 FUNÇÃO NOVA: CÁLCULO FINANCEIRO
# ==============================================================================
def calcular_economia_simulada(df_tarifas):
    """
    Simula 30 dias de operação para comparar Custo Convencional vs Smart.
    """
    # Se não tiver o arquivo, usa valores padrão
    tarifa_ponta = 1.85      # R$/kWh (Horário de Pico - Caro)
    tarifa_fora_ponta = 0.65 # R$/kWh (Horário Normal - Barato)
    
    if df_tarifas is not None and not df_tarifas.empty:
        try:
            # Tenta pegar do CSV (Assumindo colunas 'modalidade' e 'valor')
            # Ajuste conforme seu CSV real. Aqui é um exemplo genérico.
            tarifa_ponta = df_tarifas[df_tarifas['posto'] == 'Ponta']['valor'].mean()
            tarifa_fora_ponta = df_tarifas[df_tarifas['posto'] == 'Fora Ponta']['valor'].mean()
        except: pass

    # Simulação de 30 dias
    consumo_bomba_kwh = 15 # Bomba de 15 kWh (Potência média)
    
    # CENÁRIO 1: SISTEMA CONVENCIONAL (Burro)
    # Liga todo dia as 18h (Ponta) por 2 horas, chovendo ou não.
    horas_convencional = 2 * 30
    custo_convencional = horas_convencional * consumo_bomba_kwh * tarifa_ponta
    
    # CENÁRIO 2: SISTEMA SMART (Seu Projeto)
    # Só liga se não chover (Economia de 40% dos dias) e liga as 22h (Fora Ponta)
    dias_irrigados = 30 * 0.6 # Irrigou só 60% dos dias
    horas_smart = 2 * dias_irrigados
    custo_smart = horas_smart * consumo_bomba_kwh * tarifa_fora_ponta
    
    return custo_convencional, custo_smart, (custo_convencional - custo_smart)

# ==============================================================================
# 🖥️ INTERFACE ATUALIZADA
# ==============================================================================

# ... (Cabeçalho e Sidebar iguais ao anterior) ...

# CRIAÇÃO DAS 4 ABAS (Adicionei a 'Gestão de Custos')
tab_realtime, tab_history, tab_finance, tab_audit = st.tabs([
    "🎛️ Tempo Real", 
    "📅 Histórico (3 Anos)", 
    "💰 Gestão de Custos & ROI",  # <--- NOVA ABA
    "🕵️ Auditoria"
])

# --- ABA 1 e 2: (MANTENHA O CÓDIGO ANTERIOR IGUAL) ---
# ... (Copie o código das abas Tempo Real e Histórico aqui) ...

# --- ABA 3: GESTÃO DE CUSTOS (A NOVIDADE) ---
with tab_finance:
    st.header("Análise de Viabilidade Econômica")
    st.markdown("Comparativo: **Irrigação Timer (Convencional)** vs **Irrigação Smart (EcoFlow)**.")
    
    # Tenta carregar as tarifas que estão no Sidebar
    df_tarifas = load_data(URL_TARIFAS)
    
    if df_tarifas is None:
        st.warning("⚠️ Arquivo `tarifas_energia.csv` não encontrado. Usando valores médios de mercado.")
    
    # Executa a simulação
    custo_old, custo_new, economia = calcular_economia_simulada(df_tarifas)
    
    # 1. KPIs Financeiros
    col_money1, col_money2, col_money3 = st.columns(3)
    
    with col_money1:
        st.metric("Custo Mensal (Sistema Antigo)", f"R$ {custo_old:,.2f}", help="Ligado todo dia no horário de pico")
    
    with col_money2:
        st.metric("Custo Mensal (Smart System)", f"R$ {custo_new:,.2f}", delta=f"Economia: {((custo_old-custo_new)/custo_old)*100:.0f}%", delta_color="normal")
        
    with col_money3:
        st.metric("Poupança Anual Projetada", f"R$ {(economia * 12):,.2f}", help="Dinheiro salvo em 12 meses")

    st.divider()
    
    # 2. Gráfico Comparativo de Barras
    col_chart, col_explain = st.columns([2, 1])
    
    with col_chart:
        dados_grafico = pd.DataFrame({
            "Cenário": ["Convencional (Timer)", "Smart Irrigation (IoT)"],
            "Custo (R$)": [custo_old, custo_new]
        })
        
        st.subheader("📉 Redução de Custos Operacionais")
        st.bar_chart(dados_grafico, x="Cenário", y="Custo (R$)", color=["#ff4b4b", "#00d26a"]) # Vermelho vs Verde

    with col_explain:
        st.info("""
        **Por que a economia é tão grande?**
        
        1. **Smart Rain:** O sistema não liga quando a API prevê chuva (Economia de Água/Energia).
        2. **Smart Time:** O sistema programa a irrigação para horários "Fora de Ponta" (Madrugada), onde a tarifa de energia é cerca de **3x mais barata**.
        """)
        
        if df_tarifas is not None:
            with st.expander("Ver Tabela de Tarifas Carregada"):
                st.dataframe(df_tarifas, use_container_width=True)

# --- ABA 4: AUDITORIA (MANTENHA IGUAL) ---
# ... (Código da Auditoria aqui) ...
