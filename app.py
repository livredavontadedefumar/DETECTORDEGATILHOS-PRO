import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        # LIMPEZA CRUCIAL: Remove espaços e padroniza para minúsculo na planilha toda
        df.columns = [c.strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
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
        # Busca o e-mail digitado (também limpo)
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Olá! Encontramos {len(user_data)} registros no seu mapeamento.")
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('A IA está gerando sua análise personalizada...'):
                contexto = user_data.tail(20).to_string(index=False)
                res = model.generate_content(f"Analise estes gatilhos e sugira ferramentas: {contexto}")
                st.markdown("---")
                st.markdown(res.text)
        else:
            st.error(f"O e-mail '{st.session_state.user_email}' não foi encontrado nos registros da aba MAPEAMENTO.")
            if st.button("Tentar outro e-mail"):
                st.session_state.logged_in = False
                st.rerun()
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
