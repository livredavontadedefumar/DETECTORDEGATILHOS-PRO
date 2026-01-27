import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

if "gemini" in st.secrets:
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
            
            # AJUSTE DEFINITIVO: Usando o nome completo do modelo para evitar o Erro 404
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            with st.spinner('A IA está gerando sua análise personalizada...'):
                try:
                    # Enviamos apenas as colunas relevantes para economizar processamento
                    contexto = user_data.tail(30).to_string(index=False)
                    
                    prompt = f"""
                    Você é um especialista em cessação tabágica. 
                    Analise os seguintes registros de gatilhos de fumo e sugira as ferramentas 
                    adequadas para cada situação:
                    
                    {contexto}
                    """
                    
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as ai_error:
                    # Caso o modelo flash ainda dê erro, tentamos o pro como backup automático
                    try:
                        model_backup = genai.GenerativeModel('models/gemini-1.5-pro')
                        response = model_backup.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                    except:
                        st.error(f"Erro na geração: {ai_error}")
        else:
            st.error(f"O e-mail '{st.session_state.user_email}' não foi encontrado.")
            if st.button("Tentar outro e-mail"):
                st.session_state.logged_in = False
                st.rerun()
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
