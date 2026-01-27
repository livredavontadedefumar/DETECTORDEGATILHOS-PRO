import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿")

# --- CONFIGURAÇÃO DA IA ---
if "gemini" in st.secrets:
    # AJUSTE DE SEGURANÇA: Configuração direta para evitar erros de versão v1beta
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
        st.error(f"Erro ao acessar planilha: {e}")
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
            
            # --- SEU PROMPT MESTRE (Integrado da sua foto de System Instructions) ---
            prompt_mestre = """
            Você é o 'DETECTOR DE GATILHOS PRO', uma inteligência especializada em Terapia Anti-Tabagista.
            Sua missão é analisar registros de gatilhos e sugerir as ferramentas do método.
            """

            try:
                # FORÇANDO O MODELO: Usando o nome direto que você configurou no AI Studio
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    system_instruction=prompt_mestre
                )
                
                with st.spinner('A IA está analisando seus 46 registros...'):
                    # Transformando os dados da Adriana em texto para a IA
                    contexto = user_data.tail(30).to_string(index=False)
                    
                    # Chamada simplificada para evitar erro de versão
                    response = model.generate_content(f"Gere a análise para estes dados: \n\n{contexto}")
                    
                    st.markdown("---")
                    st.markdown(response.text)
                        
            except Exception as e:
                # Se o Flash falhar, tentamos o Pro como backup imediato
                try:
                    model_pro = genai.GenerativeModel('gemini-1.5-pro')
                    response = model_pro.generate_content(f"{prompt_mestre}\n\nAnalise: {user_data.tail(20).to_string()}")
                    st.markdown("---")
                    st.markdown(response.text)
                except:
                    st.error(f"Houve um problema de comunicação com o Google. Verifique se a API Key é a nova. Erro: {e}")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
