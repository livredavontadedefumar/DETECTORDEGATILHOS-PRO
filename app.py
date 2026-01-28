import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. Configuração da página
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. CONFIGURAÇÃO DE IA COM FORÇAMENTO DE VERSÃO ESTÁVEL
if "gemini" in st.secrets:
    api_key = st.secrets["gemini"]["api_key"]
    # Forçamos o sistema a ignorar o v1beta que causa o erro 404 (foto 2837)
    os.environ["GOOGLE_API_VERSION"] = "v1" 
    genai.configure(api_key=api_key)

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

# 3. Gerenciamento de Login
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
                    # Chamada explícita ao modelo estável compatível com faturamento (foto 6a5a)
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
                        # Este comando utilizará o bônus de R$ 1.904,08 primeiro (foto 2a0c)
                        response = model.generate_content(f"Analise estes dados e sugira ferramentas práticas: \n\n{contexto}")
                        
                        if response.text:
                            st.markdown("---")
                            st.markdown(response.text)

                except Exception as e:
                    # Se o erro 404 persistir, o sistema mostrará este detalhe
                    st.error(f"Sincronizando faturamento. Tente novamente em instantes. Detalhe: {e}")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
