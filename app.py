import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# CONFIGURAÇÃO DIRETA
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
        st.title("Seu Raio-X")
        
        if not user_data.empty:
            st.info(f"Olá! Localizamos {len(user_data)} registros.")
            
            if st.button("Gerar minha análise personalizada"):
                try:
                    # TENTATIVA DIRETA SEM SYSTEM INSTRUCTIONS NO CÓDIGO
                    # Isso às vezes ajuda a destravar chaves que estão "aguardando"
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('Interpretando dados...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # O Prompt Mestre entra aqui como uma pergunta direta
                        pergunta = f"""
                        Analise estes registros como um Mentor Anti-Tabagista e sugira ferramentas:
                        \n\n{contexto}
                        """
                        response = model.generate_content(pergunta)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.warning("O Google ainda está processando sua chave.")
                    st.info("Aguarde um instante e tente clicar no botão novamente.")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
