import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Identidade e Layout
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão com a IA (Ajuste para evitar erro 404)
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
    if st.button("Acessar Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel de Controle Exclusivo do ADM
    if is_adm:
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Analisar aluno:", lista_emails)
        st.sidebar.info("Modo Supervisor Ativo")
    else:
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo!")

    # 5. Análise dos Dados
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Encontramos {len(user_data)} registros para {aluno_alvo}")
            
            # --- COMANDO DA IA ---
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # MUDANÇA CRUCIAL: Usando apenas o nome estável do modelo
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('Gerando Raio-X...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Prompt que guia o comportamento da IA
                        res = model.generate_content(f"Como mentor Anti-Tabagista, analise estes registros e sugira ferramentas: \n\n{contexto}")
                        st.markdown("---")
                        st.markdown(res.text)
                except Exception as e:
                    # Caso a chave de 26/01 ainda esteja em ativação
                    st.error("O Google ainda está processando sua chave nova.")
                    st.info(f"Aguarde um minuto e tente novamente. Erro: {e}")
        else:
            st.error("Nenhum registro encontrado para este e-mail.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
