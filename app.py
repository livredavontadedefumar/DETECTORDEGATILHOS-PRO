import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configuração de Interface
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# CONEXÃO ALTERNATIVA
if "gemini" in st.secrets:
    # Forçamos a biblioteca a usar a API estável v1
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

# Fluxo de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Raio-X da Liberdade")
    email_input = st.text_input("Seu e-mail:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X Pessoal")
        
        if not user_data.empty:
            # Mostra que os dados foram lidos (Foto 126d)
            st.success(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            if st.button("Gerar Análise Personalizada"):
                try:
                    # ROTA DE FUGA: Usando o modelo sem forçar versões beta
                    # Se o Flash falhar, ele tentará o Pro automaticamente
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        contexto = user_data.tail(20).to_string(index=False)
                        response = model.generate_content(f"Analise estes dados: {contexto}")
                    except:
                        model = genai.GenerativeModel('gemini-pro')
                        contexto = user_data.tail(20).to_string(index=False)
                        response = model.generate_content(f"Analise estes dados: {contexto}")
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.warning("O Google ainda não liberou sua chave para este modelo.")
                    st.info("Alternativa: Use o AI Studio para gerar a análise manualmente por enquanto.")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
