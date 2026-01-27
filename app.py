import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Interface
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. Conexão Estável com a IA
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
            # O sistema já identifica os 51 registros aqui (Foto 38)
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            if st.button("Gerar minha análise personalizada"):
                try:
                    # MUDANÇA PARA O MODELO PRO (MAIS RESILIENTE AO ERRO 404)
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    
                    with st.spinner('A IA está interpretando seus gatilhos agora...'):
                        contexto = user_data.tail(25).to_string(index=False)
                        # Prompt que utiliza a sua missão de mentor
                        pergunta = f"Como Mentor Anti-Tabagista, analise estes gatilhos e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(pergunta)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Caso o Google ainda esteja sincronizando a conta gratuita
                    st.warning("O sistema está finalizando a sincronização.")
                    st.info(f"Dê F5 e tente em 1 minuto. Erro: {e}")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
