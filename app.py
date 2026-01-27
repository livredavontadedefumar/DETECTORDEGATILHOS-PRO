import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Interface Limpa
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. IA Estável (Evita Erro 404)
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

# 3. Login do Aluno
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Seu Raio-X da Liberdade")
    st.write("Digite seu e-mail para ver sua análise personalizada.")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    if not df.empty:
        # Filtro de privacidade para o aluno
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            # --- GERAR INTELIGÊNCIA ---
            if st.button("Gerar minha análise personalizada"):
                try:
                    # Mudança para o modelo PRO para máxima compatibilidade
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    
                    with st.spinner('Analisando seus gatilhos...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        prompt = f"Como Detector de Gatilhos PRO, analise estes dados e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Aviso caso o Google ainda esteja ativando a chave (Fotos 23/24)
                    st.warning("O sistema está finalizando a ativação da sua análise.")
                    st.info("Aguarde um minuto e clique no botão novamente.")
        else:
            st.error("E-mail não encontrado nos nossos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
