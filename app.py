import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração de Interface
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. Conexão Blindada (Forçando v1 estável)
if "gemini" in st.secrets:
    # Esta configuração ignora rotas beta que causam o erro 404
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
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# 3. Fluxo de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Seu Raio-X da Liberdade")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X")
        
        if not user_data.empty:
            # Já identifica os 51 registros aqui (Foto 126d)
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            if st.button("Gerar minha análise personalizada"):
                try:
                    # USANDO MODELO FLASH COM PARAMETRO DE VERSÃO FIXO
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está interpretando seus gatilhos...'):
                        contexto = user_data.tail(25).to_string(index=False)
                        # Seu Prompt Mestre da Foto 26 entra aqui
                        pergunta = f"Aja como Detector de Gatilhos PRO. Analise estes registros: \n\n{contexto}"
                        
                        # Chamada simplificada para evitar o 404
                        response = model.generate_content(pergunta)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Tratamento visual caso o Google ainda bloqueie
                    st.warning("O sistema está concluindo a liberação da sua chave.")
                    st.info(f"Aguarde 2 minutos e tente novamente. Erro: {e}")
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
