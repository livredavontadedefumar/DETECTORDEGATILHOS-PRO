import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA API KEY ---
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

# --- FUNÇÃO DE CONEXÃO DIRETA ---
def carregar_dados():
    try:
        url_original = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Extrai o ID da planilha do link
        id_planilha = url_original.split("/d/")[1].split("/")[0]
        # USA O GID DA SUA FOTO: 1834055894 para a aba MAPEAMENTO
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv&gid=1834055894"
        df = pd.read_csv(url_csv)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame()

# --- INTERFACE DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("Digite o e-mail cadastrado:").strip().lower()
    if st.button("Acessar Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        col_email = 'Endereço de e-mail'
        # Limpa os dados da planilha para comparação
        df[col_email] = df[col_email].astype(str).str.strip().str.lower()
        
        # Filtra os dados do usuário
        user_data = df[df[col_email] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Registros encontrados: {len(user_data)}")
            
            # Chamada ao Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            with st.spinner('A IA está analisando seus gatilhos...'):
                try:
                    contexto = user_data.tail(20).to_string(index=False)
                    response = model.generate_content(f"Analise estes registros e sugira as ferramentas do método: {contexto}")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro na análise da IA: {e}")
        else:
            st.error("E-mail não encontrado na aba MAPEAMENTO.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
