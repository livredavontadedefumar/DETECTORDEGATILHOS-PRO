import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA IA (FORÇANDO VERSÃO ESTÁVEL) ---
if "gemini" in st.secrets:
    # Forçamos o uso da biblioteca para não usar v1beta que está dando erro 404
    os.environ["GOOGLE_API_KEY"] = st.secrets["gemini"]["api_key"]
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
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
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Olá! Encontramos {len(user_data)} registros no seu mapeamento.")
            
            # MUDANÇA NO MOTOR: Usando o nome do modelo sem o prefixo 'models/' 
            # para testar a compatibilidade direta com a chave de API
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('A IA está analisando seus gatilhos...'):
                try:
                    contexto = user_data.tail(30).to_string(index=False)
                    prompt = f"Analise estes registros de gatilhos de fumo e sugira as ferramentas do método: {contexto}"
                    
                    # Chamada direta sem parâmetros de versão que causam o 404
                    response = model.generate_content(prompt)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    # Se falhar o flash, tentamos o pro 1.0 que é o mais compatível de todos
                    try:
                        model_old = genai.GenerativeModel('gemini-1.0-pro')
                        response = model_old.generate_content(prompt)
                        st.markdown(response.text)
                    except:
                        st.error(f"Houve um problema na comunicação com o Google. Verifique sua API Key nas Secrets. Erro: {e}")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
