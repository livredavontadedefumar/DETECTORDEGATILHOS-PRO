import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_original = st.secrets["connections"]["gsheets"]["spreadsheet"]
        id_planilha = url_original.split("/d/")[1].split("/")[0]
        # Usando o GID da foto: 1834055894
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv&gid=1834055894"
        df = pd.read_csv(url_csv)
        return df
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail do Mapeamento:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        col_email = 'Endereço de e-mail'
        df[col_email] = df[col_email].astype(str).str.strip().str.lower()
        
        user_data = df[df[col_email] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            contexto = user_data.tail(20).to_string(index=False)
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('Gerando análise...'):
                response = model.generate_content(f"Analise estes registros de gatilhos e sugira ferramentas: {contexto}")
                st.markdown(response.text)
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
