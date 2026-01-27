import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Layout e Identidade
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão com a IA (Forçando Estabilidade)
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

# 3. Gerenciamento de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar Sistema"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel de Controle (Exclusivo ADM)
    if is_adm:
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Escolher aluno para análise:", lista_emails)
        st.sidebar.info("Modo de Supervisão Ativo")
    else:
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo!")

    # 5. Visualização e Análise
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        st.subheader(f"Analisando: {aluno_alvo}")
        
        if not user_data.empty:
            st.success(f"Encontramos {len(user_data)} registros no mapeamento.")
            
            # --- ACIONAMENTO DA IA ---
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # AJUSTE PARA ELIMINAR O ERRO 404:
                    # Mudamos para o modelo 1.5-flash puro, sem prefixos instáveis.
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando os dados...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        prompt = f"Como especialista Anti-Tabagista, analise estes registros de gatilhos e sugira ferramentas: \n\n{contexto}"
                        
                        # Chamada direta sem parâmetros de versão que causam o 404
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                        
                except Exception as e:
                    # Caso a ativação da chave de hoje ainda esteja em curso
                    st.error("O Google ainda está ativando sua chave nova.")
                    st.info(f"Dê F5 em 2 minutos. Erro técnico: {e}")
        else:
            st.error("Nenhum registro encontrado para este usuário.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
