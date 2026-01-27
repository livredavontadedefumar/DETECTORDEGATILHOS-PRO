import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações Visuais
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão Estável com a IA
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

# 3. Controle de Acesso
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail:").strip().lower()
    if st.button("Acessar Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Interface ADM vs ALUNO
    if is_adm:
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Escolher aluno:", lista_emails)
    else:
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo!")

    # 5. Execução da Análise
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Analisando: {aluno_alvo} ({len(user_data)} registros)")
            
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # CURA PARA O ERRO 404: Chamada direta ao modelo estável
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está processando...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu Prompt Mestre (System Instruction)
                        prompt = f"Como especialista Anti-Tabagista, analise estes gatilhos e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.error("O Google ainda está ativando sua chave de hoje.")
                    st.info(f"Dê F5 em 2 minutos. Erro: {e}")
        else:
            st.error("E-mail não encontrado.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
