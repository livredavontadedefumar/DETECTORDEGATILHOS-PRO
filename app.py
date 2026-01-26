import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA API KEY (SECRETS) ---
# Usamos o st.secrets para buscar a chave que você salvou no painel do Streamlit
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])
else:
    st.error("Erro: API Key não encontrada nas Secrets.")

# --- CONEXÃO E LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

ADMIN_COMMAND = "/admin_master_2026"

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail do Mapeamento ou Comando ADM:").strip().lower()
    
    if st.button("Acessar"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    # --- CONEXÃO COM A PLANILHA ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # AJUSTE DE CONEXÃO: Forçamos a leitura da aba MAPEAMENTO com ttl=0 para evitar erro 400
    try:
        df = conn.read(worksheet="MAPEAMENTO", ttl=0)
    except Exception as e:
        # Caso o nome da aba falhe, tentamos ler a planilha de forma geral
        df = conn.read(ttl=0)
    
    # Limpeza de dados para evitar erros de digitação e espaços vazios
    if 'Endereço de e-mail' in df.columns:
        df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
    
    is_admin = st.session_state.user_email == ADMIN_COMMAND
    
    if is_admin:
        st.sidebar.success("MODO ADMINISTRADOR ATIVO")
        if 'Endereço de e-mail' in df.columns:
            lista_usuarios = df['Endereço de e-mail'].unique()
            usuario_selecionado = st.sidebar.selectbox("Selecionar Aluno para Análise:", lista_usuarios)
            user_data = df[df['Endereço de e-mail'] == usuario_selecionado]
            st.title(f"Análise ADM: {usuario_selecionado}")
        else:
            st.error("Coluna 'Endereço de e-mail' não encontrada.")
            user_data = pd.DataFrame()
    else:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X da Liberdade")

    # Exibição dos dados e chamada do Gemini
    if not user_data.empty:
        st.write(f"Registros encontrados: {len(user_data)}")
        
        # Preparando os dados para a IA (limitando para não travar o prompt)
        contexto_aluno = user_data.tail(50).to_string(index=False)
        
        # Chamada ao Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        with st.spinner('Gerando seu Raio-X personalizado...'):
            try:
                # Instrução mestre para a IA
                prompt = f"Analise os seguintes dados de rastreamento de cigarro e gere o Raio-X sugerindo as Placas de X de acordo com os gatilhos encontrados:\n\n{contexto_aluno}"
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao gerar análise pela IA: {e}")
    else:
        st.error("Nenhum dado encontrado. Verifique se o e-mail está correto e se há registros na aba MAPEAMENTO.")
    
    if st.sidebar.button("Sair/Trocar Usuário"):
        st.session_state.logged_in = False
        st.rerun()
