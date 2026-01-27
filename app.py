import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# --- CONEXÃO COM A IA ---
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
        st.error(f"Erro ao carregar os registros: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
st.title("🌿 Detector de Gatilhos PRO")

df = carregar_dados()

if not df.empty:
    # Lista de e-mails únicos para o Modo Administrador
    lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
    
    st.sidebar.header("Painel de Controle")
    # Você escolhe o aluno aqui
    usuario_selecionado = st.sidebar.selectbox("Selecionar Aluno para Análise:", lista_emails)
    
    if usuario_selecionado:
        user_data = df[df['Endereço de e-mail'] == usuario_selecionado]
        
        st.subheader(f"Raio-X: {usuario_selecionado}")
        st.info(f"Encontramos {len(user_data)} registros no mapeamento deste aluno.")
        
        prompt_mestre = "Você é o DETECTOR DE GATILHOS PRO. Analise os gatilhos e sugira ferramentas do método."

        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            if st.button(f"Gerar Análise para {usuario_selecionado}"):
                with st.spinner('A IA está processando os dados...'):
                    contexto = user_data.tail(30).to_string(index=False)
                    response = model.generate_content(f"{prompt_mestre}\n\nDados:\n{contexto}")
                    st.markdown("---")
                    st.markdown(response.text)
        except Exception as e:
            st.error("O Google ainda está processando o acesso da sua chave nova.")
            st.info("Aguarde mais alguns instantes. Esse processo é normal para chaves criadas hoje.")
else:
    st.warning("Aguardando carregamento da base de dados...")
