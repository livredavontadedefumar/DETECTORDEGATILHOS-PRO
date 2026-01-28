import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Raio-X da Liberdade", page_icon="🌿")

# 2. CONFIGURAÇÃO DE IA PRIORITÁRIA (CONTA LIVREDAVONTADE)
# Vinculado ao projeto DETECTOR DE GATILHOS (foto 43a8)
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Endereço de e-mail' in df.columns:
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame()

# 3. Gerenciamento de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Bem-vindo ao seu Raio-X")
    e_input = st.text_input("Seu e-mail cadastrado:").strip().lower()
    if st.button("Acessar Mapeamento"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        user_data = df[df['Endereço de e-mail'] == st.session_state.user_email]
        st.title("Seu Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Olá! Localizamos {len(user_data)} registros no seu mapeamento.")
            
            # 4. BOTÃO DE GERAÇÃO COM AJUSTE PARA ERRO 404 (FOTO 915e)
            if st.button("Gerar Inteligência Personalizada"):
                try:
                    # 'models/gemini-1.5-flash' é o caminho oficial para contas pagas
                    model = genai.GenerativeModel(
                        model_name='models/gemini-1.5-flash',
                        system_instruction="""
                        Você é o 'DETECTOR DE GATILHOS PRO'. 
                        Sua missão é analisar os registros de consumo e gatilhos do aluno 
                        e fornecer uma análise baseada no Método Livre da Vontade de Fumar.
                        """
                    )
                    
                    with st.spinner('O mentor está analisando seus gatilhos agora...'):
                        contexto = user_data.tail(25).to_string(index=False)
                        # Chamada direta utilizando o faturamento ativo (foto 6a5a)
                        response = model.generate_content(f"Analise estes dados e sugira ferramentas práticas: \n\n{contexto}")
                        
                        if response.text:
                            st.markdown("---")
                            st.markdown(response.text)
                        else:
                            st.warning("A IA processou, mas o retorno veio vazio. Tente novamente.")

                except Exception as e:
                    # Exibe o erro real caso o Google ainda esteja processando o faturamento
                    st.error(f"Nota: A IA está sendo ativada. Detalhe: {e}")
                    st.info("Se o erro persistir, aguarde 5 minutos para a sincronização do faturamento.")
        else:
            st.error("E-mail não encontrado.")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
