import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA API KEY ---
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])
else:
    st.error("API Key não encontrada.")

# --- CONEXÃO COM A PLANILHA (MÉTODO DIRETO) ---
def carregar_dados():
    try:
        # Puxamos o link direto das secrets
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Transformamos o link de 'edit' para 'export' para o Pandas ler direto
        url_csv = url.replace('/edit#gid=', '/export?format=csv&gid=')
        if '/edit' in url and '&gid=' not in url_csv:
             url_csv = url.replace('/edit', '/export?format=csv')
        
        # Lendo a planilha (o segredo aqui é o formato CSV que evita o erro 400/404)
        df = pd.read_csv(url_csv)
        return df
    except Exception as e:
        st.error(f"Erro na conexão com a planilha: {e}")
        return pd.DataFrame()

# --- LÓGICA DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

ADMIN_COMMAND = "/admin_master_2026"

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail ou Comando ADM:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    
    if not df.empty:
        # Padronizando a coluna de e-mail
        col_email = 'Endereço de e-mail'
        df[col_email] = df[col_email].astype(str).str.strip().str.lower()
        
        is_admin = st.session_state.user_email == ADMIN_COMMAND
        
        if is_admin:
            st.sidebar.success("MODO ADM")
            lista = df[col_email].unique()
            sel = st.sidebar.selectbox("Aluno:", lista)
            user_data = df[df[col_email] == sel]
        else:
            user_data = df[df[col_email] == st.session_state.user_email]
        
        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Registros: {len(user_data)}")
            
            # Chamada ao Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('Analisando gatilhos...'):
                contexto = user_data.tail(30).to_string(index=False)
                res = model.generate_content(f"Analise estes registros de fumo e sugira ferramentas: {contexto}")
                st.markdown(res.text)
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
