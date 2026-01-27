import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONEXÃO COM A IA (FORÇANDO ESTABILIDADE) ---
if "gemini" in st.secrets:
    # Usamos apenas a configuração básica para evitar o erro 404 de versão v1beta
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
        st.error(f"Erro ao carregar os registros: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("Digite seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar Raio-X"):
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
            
            # --- SEU PROMPT MESTRE (Cérebro da IA) ---
            prompt_mestre = "Você é o DETECTOR DE GATILHOS PRO. Analise os gatilhos e sugira ferramentas do método."

            try:
                # Usamos o modelo Pro que é o mais compatível com chaves novas
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                with st.spinner('A IA está gerando sua análise...'):
                    # Enviamos os dados da Adriana para análise
                    contexto = user_data.tail(30).to_string(index=False)
                    # Forçamos a geração de conteúdo de forma simples
                    response = model.generate_content(f"{prompt_mestre}\n\nDados:\n{contexto}")
                    
                    st.markdown("---")
                    st.markdown(response.text)
            except Exception as e:
                # Caso o Google ainda esteja ativando sua chave de hoje
                st.error("O Google ainda está processando o acesso da sua chave.")
                st.info("Aguarde um instante e tente novamente em alguns minutos.")
        else:
            st.error(f"E-mail '{st.session_state.user_email}' não encontrado.")
    
    if st.sidebar.button("Sair / Trocar Usuário"):
        st.session_state.logged_in = False
        st.rerun()
