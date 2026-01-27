import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# --- SEU E-MAIL DE ADMINISTRADOR ---
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# --- CONEXÃO IA ---
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
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- SESSÃO DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("Digite seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar Sistema"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    
    # --- LÓGICA DE VISÃO: ADM vs ALUNO ---
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    if is_adm:
        # VISÃO DO ADMINISTRADOR: Menu lateral liberado
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Analisar progresso do aluno:", lista_emails)
        st.sidebar.warning("Você está em modo de supervisão.")
    else:
        # VISÃO DO ALUNO: Travado apenas no próprio e-mail
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo ao seu despertar!")

    # --- EXECUÇÃO DA ANÁLISE ---
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        
        st.title(f"Raio-X da Liberdade")
        st.subheader(f"Usuário: {aluno_alvo}")
        
        if not user_data.empty:
            st.info(f"Registros encontrados: {len(user_data)}")
            
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    with st.spinner('A IA está processando o método...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu Prompt Mestre entra aqui
                        res = model.generate_content(f"Analise estes gatilhos e sugira ferramentas: {contexto}")
                        st.markdown("---")
                        st.markdown(res.text)
                except Exception as e:
                    st.error("O Google ainda está processando sua chave.")
                    st.info(f"Detalhe: {e}")
        else:
            st.error("Nenhum registro encontrado para este e-mail.")

    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logged_in = False
        st.rerun()
