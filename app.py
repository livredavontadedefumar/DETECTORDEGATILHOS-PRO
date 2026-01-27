import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="PAINEL MESTRE - Detector de Gatilhos", page_icon="🛡️", layout="wide")

# CONFIGURAÇÃO DA IA (FORÇANDO CONEXÃO ESTÁVEL)
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            # Limpeza correta para evitar erro de Series object
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

# --- INTERFACE ADMINISTRATIVA ---
st.title("🛡️ Painel de Controle Mestre")
df = carregar_dados()

if not df.empty:
    # Lista todos os alunos para você escolher
    lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
    
    st.sidebar.header("Gestão de Alunos")
    aluno_selecionado = st.sidebar.selectbox("Escolha o aluno para Raio-X:", lista_emails)
    
    user_data = df[df['Endereço de e-mail'] == aluno_selecionado]
    
    st.subheader(f"Analisando: {aluno_selecionado}")
    st.write(f"Total de registros encontrados: {len(user_data)}")

    if st.button(f"Gerar Inteligência PRO para {aluno_selecionado}"):
        try:
            # Mudança para o modelo PRO que é mais resiliente a erros de chave nova
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            with st.spinner('A IA está processando os dados do aluno...'):
                contexto = user_data.tail(30).to_string(index=False)
                # Seu prompt mestre focado em mentoria
                prompt = f"Como Mentor Anti-Tabagista, analise estes gatilhos e sugira ferramentas do método: \n\n{contexto}"
                
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
        except Exception as e:
            st.error("O Google ainda está processando a ativação global da sua chave.")
            st.info(f"Detalhe técnico: {e}")
