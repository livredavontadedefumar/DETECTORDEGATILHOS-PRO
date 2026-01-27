import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        # Lê o link CSV direto das secrets
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        return df
    except Exception as e:
        st.error(f"Erro ao acessar dados: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Ver meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        # Ajuste o nome da coluna se necessário para bater com sua planilha
        col_email = 'Endereço de e-mail' 
        df[col_email] = df[col_email].astype(str).str.strip().str.lower()
        user_data = df[df[col_email] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Registros: {len(user_data)}")
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('IA analisando gatilhos...'):
                contexto = user_data.tail(15).to_string(index=False)
                res = model.generate_content(f"Analise estes gatilhos e dê ferramentas: {contexto}")
                st.markdown(res.text)
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
