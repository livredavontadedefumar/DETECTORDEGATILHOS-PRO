import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONEXÃO E LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# Simulando uma verificação de ADM
ADMIN_COMMAND = "/admin_master_2026"

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail do Mapeamento ou Comando ADM:").strip().lower()
    
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    # Lógica de Administração
    is_admin = st.session_state.user_email == ADMIN_COMMAND
    
    # Conectar ao Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    if is_admin:
        st.sidebar.success("MODO ADMINISTRADOR ATIVO")
        lista_usuarios = df['Endereço de e-mail'].unique()
        usuario_selecionado = st.sidebar.selectbox("Selecionar Aluno para Análise:", lista_usuarios)
        user_data = df[df['Endereço de e-mail'] == usuario_selecionado]
        st.title(f"Análise ADM: {usuario_selecionado}")
    else:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X da Liberdade")

    # Exibição dos dados e chamada do Gemini (usando o Prompt Mestre configurado no AI Studio)
    if not user_data.empty:
        st.write(f"Registros encontrados: {len(user_data)}")
        # Aqui o código continua com a chamada da API do Gemini...
    else:
        st.error("Nenhum dado encontrado para este usuário.")