import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Identidade e Layout
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão com a IA (Forçando Estabilidade)
if "gemini" in st.secrets:
    # A configuração básica evita o erro 404 de versão v1beta
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
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

# 3. Gerenciamento de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    e_input = st.text_input("E-mail:").strip().lower()
    if st.button("Acessar Raio-X"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel ADM
    if is_adm:
        lista = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno = st.sidebar.selectbox("Escolher aluno:", lista)
    else:
        aluno = st.session_state.user_email

    # 5. Visualização e Análise
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Analisando: {aluno} ({len(user_data)} registros)")
            
            if st.button(f"Gerar Inteligência para {aluno}"):
                try:
                    # Chamada direta ao modelo estável
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu comando mestre para a IA
                        prompt = f"Aja como o DETECTOR DE GATILHOS PRO. Analise estes registros e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Caso o Google ainda esteja ativando a chave de hoje
                    st.error("O Google ainda está ativando sua chave de hoje.")
                    st.info(f"Aguarde um instante e dê F5. Erro: {e}")
        else:
            st.error("Nenhum registro encontrado para este e-mail.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
