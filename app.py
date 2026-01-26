import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# Configuração da IA
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

# --- FUNÇÃO DE CONEXÃO DIRETA E LIMPA ---
def carregar_dados():
    try:
        url_original = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Limpa o link para garantir que o Google aceite o pedido
        id_planilha = url_original.split("/d/")[1].split("/")[0]
        # Forçamos o link para a aba MAPEAMENTO (gid=1239855325 conforme sua planilha)
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv&gid=1239855325"
        
        df = pd.read_csv(url_csv)
        return df
    except Exception as e:
        st.error(f"Erro na conexão com a planilha: {e}")
        return pd.DataFrame()

# --- INTERFACE E LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail do Mapeamento ou Comando ADM:").strip().lower()
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
        
        if st.session_state.user_email == "/admin_master_2026":
            st.sidebar.success("MODO ADM ATIVO")
            lista = df[col_email].unique()
            usuario_selecionado = st.sidebar.selectbox("Selecionar Aluno:", lista)
            user_data = df[df[col_email] == usuario_selecionado]
        else:
            user_data = df[df[col_email] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Registros encontrados: {len(user_data)}")
            
            # Chamada ao Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('Gerando análise...'):
                contexto = user_data.tail(30).to_string(index=False)
                prompt = f"Com base nestes registros de gatilhos: {contexto}, sugira as ferramentas adequadas."
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
        else:
            st.error("Nenhum registro encontrado para este e-mail.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
