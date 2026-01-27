import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# CONFIGURAÇÃO DE IA PRIORITÁRIA (CONTA LIVREDAVONTADE)
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
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Bem-vindo ao seu Raio-X")
    e_input = st.text_input("Seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar Mapeamento"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            if st.button("Gerar Inteligência Personalizada"):
                try:
                    # SUA PERSONA DEFINIDA NA FOTO A9A8
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                        system_instruction="""
                        Você é o 'DETECTOR DE GATILHOS PRO'. 
                        Sua missão é analisar os registros de consumo e gatilhos do aluno 
                        e fornecer uma análise baseada no Método Livre da Vontade de Fumar.
                        """
                    )
                    
                    with st.spinner('O mentor está analisando seus gatilhos agora...'):
                        contexto = user_data.tail(25).to_string(index=False)
                        response = model.generate_content(f"Analise estes dados e sugira ferramentas práticas: \n\n{contexto}")
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.info("Aguarde um instante para a IA processar sua análise prioritária.")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
