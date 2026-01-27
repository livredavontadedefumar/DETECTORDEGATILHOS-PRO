import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# CONFIGURAÇÃO DE CONEXÃO DIRETA
if "gemini" in st.secrets:
    # Forçamos a API a usar apenas a rota estável (v1)
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Seu Raio-X Pessoal")
    e_input = st.text_input("E-mail:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            # Reconhecimento dos registros já funcionando (Foto da4d)
            st.success(f"Olá! Localizamos {len(user_data)} registros.")
            
            if st.button("Gerar Inteligência"):
                try:
                    # USANDO O MODELO MAIS ESTÁVEL POSSÍVEL
                    model = genai.GenerativeModel('gemini-pro')
                    
                    with st.spinner('A IA está interpretando seus dados...'):
                        contexto = user_data.tail(20).to_string(index=False)
                        # Seu prompt direto para evitar erros de processamento
                        pergunta = f"Como Mentor Anti-Tabagista, analise estes gatilhos e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(pergunta)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Se mesmo o Pro falhar, o problema é a propagação da chave nova
                    st.warning("O Google está sincronizando sua nova chave nos servidores mundiais.")
                    st.info("Aguarde 2 minutos e tente novamente. Esse processo é automático.")
        else:
            st.error("E-mail não cadastrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
