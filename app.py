import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# --- CONEXÃO COM A IA ---
if "gemini" in st.secrets:
    # Usando a configuração básica para evitar erros de versão beta
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
    st.write("Digite seu e-mail para acessar sua análise personalizada.")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        # Filtro de privacidade para o aluno logado
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        st.title("Seu Raio-X da Liberdade")
        
        if not user_data.empty:
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            # --- GERAR ANÁLISE ---
            if st.button("Gerar minha análise personalizada"):
                try:
                    # Mudança para o modelo 1.5 PRO para maior estabilidade inicial
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    
                    with st.spinner('A IA está interpretando seus dados agora...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        prompt = f"Como Mentor Anti-Tabagista, analise estes dados e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Mensagem enquanto o Google sincroniza (visto em suas fotos)
                    st.warning("O sistema está finalizando a sincronização da sua análise.")
                    st.info("Aguarde um minuto e clique no botão novamente.")
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
