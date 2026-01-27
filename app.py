import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# CONFIGURAÇÃO DA IA (FORÇANDO ESTABILIDADE)
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            # Limpeza correta para evitar o erro AttributeError 'Series'
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    e_input = st.text_input("E-mail:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        is_adm = st.session_state.user_email == EMAIL_ADM
        
        if is_adm:
            lista = sorted(df['Endereço de e-mail'].unique().tolist())
            st.sidebar.header("🛡️ Painel ADM")
            aluno = st.sidebar.selectbox("Aluno:", lista)
        else:
            aluno = st.session_state.user_email

        user_data = df[df['Endereço de e-mail'] == aluno]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.info(f"Analisando: {aluno} ({len(user_data)} registros)")
            
            if st.button(f"Gerar Inteligência"):
                try:
                    # USANDO O MODELO MAIS COMPATÍVEL COM CHAVES GRATUITAS
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    
                    with st.spinner('Analisando...'):
                        contexto = user_data.tail(25).to_string(index=False)
                        # Prompt direto para evitar erro de versão
                        response = model.generate_content(f"Aja como Mentor Anti-Tabagista. Analise: {contexto}")
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.error("O Google ainda está processando sua chave.")
                    st.info(f"Aguarde um instante e dê F5. Erro: {e}")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
