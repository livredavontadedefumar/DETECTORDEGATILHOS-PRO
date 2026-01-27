import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações Iniciais
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão Blindada (Forçando v1 estável)
if "gemini" in st.secrets:
    # Esta configuração ignora o v1beta e usa a rota oficial
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

# 3. Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    e = st.text_input("E-mail:").strip().lower()
    if st.button("Acessar"):
        st.session_state.user_email = e
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel ADM (Foto 14/15)
    if is_adm:
        lista = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno = st.sidebar.selectbox("Escolher aluno:", lista)
    else:
        aluno = st.session_state.user_email

    # 5. O Raio-X (Foto 16)
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno]
        st.title("Raio-X da Liberdade")
        if not user_data.empty:
            st.success(f"Analisando: {aluno} ({len(user_data)} registros)")
            
            if st.button(f"Gerar Inteligência"):
                try:
                    # USANDO O NOME CURTO PARA EVITAR 404
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está processando...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu Prompt Mestre da Foto 4
                        prompt = f"Aja como o DETECTOR DE GATILHOS PRO. Analise: {contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"O Google ainda está ativando sua chave. Erro: {e}")
