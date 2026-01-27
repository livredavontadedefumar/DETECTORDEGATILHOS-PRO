import streamlit as st
import google.generativeai as genai
import pandas as pd

# Interface do Aluno
st.set_page_config(page_title="Raio-X Pessoal", page_icon="🌿")

# Conexão com a IA
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
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

# Login Simples
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Seu Raio-X da Liberdade")
    email_input = st.text_input("Seu e-mail:").strip().lower()
    if st.button("Acessar Mapeamento"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X Pessoal")
        
        if not user_data.empty:
            st.success(f"Olá! Localizamos {len(user_data)} registros.")
            
            if st.button("Gerar Análise Personalizada"):
                try:
                    # Tentativa com o Flash (mais rápido)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está interpretando seus dados...'):
                        contexto = user_data.tail(20).to_string(index=False)
                        prompt = f"Como Mentor Anti-Tabagista, analise estes gatilhos e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.warning("Aguardando liberação da nova chave pelo Google.")
                    st.info(f"Tente novamente em instantes. Erro: {e}")
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
