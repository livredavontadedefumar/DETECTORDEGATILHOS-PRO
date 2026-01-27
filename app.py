import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações Básicas
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. Conexão com a IA
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        # Limpeza das colunas para evitar erros de leitura
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar registros: {e}")
        return pd.DataFrame()

# 3. Gerenciamento de Acesso (Login do Aluno)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos")
    st.write("Digite seu e-mail para acessar seu mapeamento pessoal.")
    email_input = st.text_input("Seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    if not df.empty:
        # Filtra apenas os dados do aluno logado
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        st.title("Seu Raio-X da Liberdade")
        
        if not user_data.empty:
            st.info(f"Olá! Encontramos {len(user_data)} registros no seu mapeamento.")
            
            # --- ACIONAMENTO DA IA ---
            if st.button("Gerar minha análise personalizada"):
                try:
                    # Usamos o modelo Flash de forma direta para evitar o erro 404
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando seus gatilhos...'):
                        # Pegamos os últimos 30 registros para a IA analisar
                        contexto = user_data.tail(30).to_string(index=False)
                        
                        prompt = f"""
                        Você é o Detector de Gatilhos PRO. Analise os registros de mapeamento 
                        abaixo e sugira as ferramentas do método para este aluno vencer a fissura:
                        \n\n{contexto}
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Caso de propagação da chave (Fotos 23/24)
                    st.error("O Google ainda está processando o acesso da sua chave.")
                    st.info("Aguarde um minuto e tente novamente.")
        else:
            st.error("E-mail não encontrado nos nossos registros de mapeamento.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
