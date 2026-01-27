import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Layout
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão Blindada (FORÇANDO VERSÃO ESTÁVEL V1)
if "gemini" in st.secrets:
    # Esta configuração garante que não usaremos o v1beta que causa o erro 404
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        df.columns = [c.strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).strip().lower()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# 3. Gerenciamento de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    e_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar Sistema"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel ADM (Como na sua Foto 22)
    if is_adm:
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Escolher aluno para análise:", lista_emails)
        st.sidebar.info("Modo Supervisor Ativo")
    else:
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo!")

    # 5. Visualização do Raio-X
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Analisando: {aluno_alvo} ({len(user_data)} registros)")
            
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # CURA DO ERRO 404: Chamada direta ao modelo estável
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando os registros...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu Prompt Mestre da Foto 4
                        prompt = f"Como DETECTOR DE GATILHOS PRO, analise estes dados e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Caso o Google ainda esteja ativando a chave (Fotos 20, 21 e 22)
                    st.error("O Google ainda está ativando sua chave criada hoje.")
                    st.info(f"Dê F5 no app em 2 minutos. Erro técnico: {e}")
        else:
            st.error("Nenhum registro encontrado para este e-mail.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
