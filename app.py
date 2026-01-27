import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA IA ---
if "gemini" in st.secrets:
    # Configuração direta para evitar o erro de versão v1beta
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
        st.error(f"Erro ao acessar planilha: {e}")
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
            
            # --- SEU PROMPT MESTRE ---
            prompt_mestre = "Você é o DETECTOR DE GATILHOS PRO. Analise os gatilhos e sugira as ferramentas do método."

            try:
                # TENTATIVA 1: Modelo Flash (Mais rápido)
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner('A IA está analisando seus registros...'):
                    contexto = user_data.tail(30).to_string(index=False)
                    response = model.generate_content(f"{prompt_mestre}\n\nDados: {contexto}")
                    st.markdown("---")
                    st.markdown(response.text)
            except Exception:
                try:
                    # TENTATIVA 2: Modelo Pro (Mais estável para chaves novas)
                    model_pro = genai.GenerativeModel('gemini-1.5-pro')
                    response = model_pro.generate_content(f"{prompt_mestre}\n\nDados: {user_data.tail(20).to_string()}")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error("O Google ainda está processando sua chave. Isso pode levar alguns minutos após a criação.")
                    st.info(f"Aguarde um instante e dê F5. Erro: {e}")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
