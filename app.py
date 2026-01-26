import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA API KEY (SECRETS) ---
genai.configure(api_key=st.secrets["gemini"]["api_key"])

# --- CONEXÃO E LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

ADMIN_COMMAND = "/admin_master_2026"

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail do Mapeamento ou Comando ADM:").strip().lower()
    
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    # Conectar ao Sheets especificando a aba MAPEAMENTO
    conn = st.connection("gsheets", type=GSheetsConnection)
    # AJUSTE AQUI: Lendo especificamente a aba de registros
    df = conn.read(worksheet="MAPEAMENTO")
    
    # Limpeza de dados para evitar erros de digitação
    df['Endereço de e-mail'] = df['Endereço de e-mail'].str.strip().str.lower()
    
    is_admin = st.session_state.user_email == ADMIN_COMMAND
    
    if is_admin:
        st.sidebar.success("MODO ADMINISTRADOR ATIVO")
        lista_usuarios = df['Endereço de e-mail'].unique()
        usuario_selecionado = st.sidebar.selectbox("Selecionar Aluno para Análise:", lista_usuarios)
        user_data = df[df['Endereço de e-mail'] == usuario_selecionado]
        st.title(f"Análise ADM: {usuario_selecionado}")
    else:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X da Liberdade")

    if not user_data.empty:
        st.write(f"Registros encontrados: {len(user_data)}")
        
        # Preparando os dados para a IA
        contexto_aluno = user_data.to_string(index=False)
        
        # Chamada ao Gemini
        model = genai.GenerativeModel('gemini-1.5-pro') # Ou o modelo que você configurou
        
        with st.spinner('Gerando seu Raio-X personalizado...'):
            try:
                response = model.generate_content(f"Analise os seguintes dados de rastreamento e gere o Raio-X conforme o seu treinamento mestre:\n\n{contexto_aluno}")
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao gerar análise: {e}")
    else:
        st.error("Nenhum dado encontrado para este usuário na aba MAPEAMENTO.")
    
    if st.sidebar.button("Sair/Trocar Usuário"):
        st.session_state.logged_in = False
        st.rerun()
