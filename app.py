import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração de Layout e Identidade
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")

# SEU E-MAIL MESTRE
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão com a IA (Configuração Estável)
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

# 3. Gerenciamento de Sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("Digite seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar Sistema"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    is_adm = st.session_state.user_email == EMAIL_ADM
    
    # 4. Painel de Controle (Só visível para o ADM)
    if is_adm:
        lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
        st.sidebar.header("🛡️ Painel ADM")
        aluno_alvo = st.sidebar.selectbox("Selecionar aluno para análise:", lista_emails)
        st.sidebar.info("Modo de Supervisão Ativo")
    else:
        aluno_alvo = st.session_state.user_email
        st.sidebar.write("🌿 Bem-vindo ao seu despertar!")

    # 5. Apresentação dos Dados
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        st.subheader(f"Usuário em análise: {aluno_alvo}")
        
        if not user_data.empty:
            st.info(f"Encontramos {len(user_data)} registros no mapeamento.")
            
            # BOTÃO DE AÇÃO PARA A IA
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # AJUSTE ANTÍDOTO PARA O ERRO 404:
                    # Usamos o modelo Pro que é mais estável para chaves novas
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    
                    with st.spinner('A IA está analisando o método...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        # Seu comando mestre para a IA
                        prompt = f"Analise estes gatilhos e sugira as ferramentas do método para este aluno: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Caso o Google ainda esteja ativando a chave
                    st.error("O Google ainda está processando o acesso da sua chave.")
                    st.info(f"Aguarde um minuto e tente novamente. Detalhe técnico: {e}")
        else:
            st.error("Nenhum registro encontrado para este e-mail.")

    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logged_in = False
        st.rerun()
