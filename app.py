import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Interface
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. Configuração da Inteligência Artificial
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        # Limpeza técnica das colunas
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# 3. Fluxo de Acesso
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Bem-vindo ao seu Raio-X")
    st.write("Insira seu e-mail para ver o mapeamento dos seus gatilhos.")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    
    if st.button("Ver meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()

else:
    df = carregar_dados()
    if not df.empty:
        # Filtro exclusivo para o aluno logado
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        st.title("Seu Raio-X da Liberdade")
        
        if not user_data.empty:
            st.info(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            # --- GERAÇÃO DA ANÁLISE PELA IA ---
            if st.button("Gerar minha análise personalizada"):
                try:
                    # Usando o modelo gemini-1.5-flash diretamente
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando seus gatilhos agora...'):
                        # Pegamos os registros mais recentes para a análise
                        contexto = user_data.tail(30).to_string(index=False)
                        
                        prompt = f"""
                        Você é o Detector de Gatilhos PRO, um mentor especialista no método de cessação tabágica.
                        Analise os registros de mapeamento abaixo e, com base nos gatilhos e emoções 
                        identificados, sugira ferramentas práticas do método para ajudar este aluno.
                        \n\nDados do mapeamento:\n{contexto}
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    # Mensagem amigável caso o Google ainda esteja ativando a chave
                    st.warning("O sistema está finalizando a ativação da sua análise.")
                    st.info("Aguarde um minuto e clique no botão novamente.")
        else:
            st.error("E-mail não encontrado nos registros de mapeamento.")
            if st.button("Tentar outro e-mail"):
                st.session_state.logged_in = False
                st.rerun()
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
