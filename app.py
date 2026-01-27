import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA IA ---
if "gemini" in st.secrets:
    # Configuração simples para evitar erros de versão instável
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
        st.error(f"Erro ao acessar dados: {e}")
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    email_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Ver meu Raio-X"):
        st.session_state.user_email = email_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]

        if not user_data.empty:
            st.title("Seu Raio-X da Liberdade")
            st.write(f"Olá! Encontramos {len(user_data)} registros no seu mapeamento.")
            
            # --- SEU PROMPT MESTRE (Baseado nas suas System Instructions) ---
            prompt_mestre = """
            Você é o 'DETECTOR DE GATILHOS PRO', uma inteligência especializada em Terapia Anti-Tabagista.
            Sua missão é analisar os registros de gatilhos fornecidos e sugerir as ferramentas 
            do seu método (como as Placas de X) para cada situação encontrada.
            """

            try:
                # Usando o nome estável do modelo para evitar o erro 404
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    system_instruction=prompt_mestre
                )
                
                with st.spinner('A IA está analisando seus gatilhos...'):
                    # Enviamos os últimos 30 registros da Adriana para análise
                    contexto = user_data.tail(30).to_string(index=False)
                    response = model.generate_content(f"Gere o Raio-X para estes dados: \n\n{contexto}")
                    
                    st.markdown("---")
                    st.markdown(response.text)
                        
            except Exception as e:
                # Caso a chave ainda esteja em processo de ativação no Google
                st.warning("O Google ainda está processando sua chave nova. Aguarde um instante e recarregue.")
                st.info(f"Detalhe técnico: {e}")
        else:
            st.error("E-mail não encontrado nos registros.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
