import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Interface
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. Conexão Blindada com a IA
if "gemini" in st.secrets:
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
    if st.button("Acessar Mapeamento"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X")
        
        if not user_data.empty:
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            if st.button("Gerar minha análise personalizada"):
                try:
                    # Inserindo sua Missão de Mentor da Foto 26 diretamente aqui
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                        system_instruction="Você é o DETECTOR DE GATILHOS PRO, uma inteligência especializada em Terapia Anti-Tabagista baseada no método."
                    )
                    
                    with st.spinner('Interpretando seus gatilhos agora...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        response = model.generate_content(f"Analise estes registros e sugira ferramentas: \n\n{contexto}")
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Gerencia o tempo de sincronização do Google (visto nas fotos 38 e f093e7eb)
                    st.warning("O sistema está finalizando a ativação da sua análise.")
                    st.info("Aguarde um minuto e clique no botão novamente.")
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
