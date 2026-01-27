import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configurações de Identidade e Layout
st.set_page_config(page_title="Detector de Gatilhos PRO", page_icon="🌿", layout="wide")
EMAIL_ADM = "livredavontadedefumar@gmail.com" 

# 2. Conexão com a IA (Chave: ...8hsk)
if "gemini" in st.secrets:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])

def carregar_dados():
    try:
        url_csv = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df = pd.read_csv(url_csv)
        # CORREÇÃO DO ERRO 'AttributeError': Limpando nomes de colunas um a um
        df.columns = [str(c).strip() for c in df.columns]
        
        if 'Endereço de e-mail' in df.columns:
            # CORREÇÃO DO ERRO DA FOTO: Limpando os e-mails corretamente
            df['Endereço de e-mail'] = df['Endereço de e-mail'].astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erro ao processar dados da planilha: {e}")
        return pd.DataFrame()

# 3. Gerenciamento de Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    st.title("🌿 Detector de Gatilhos PRO")
    e_input = st.text_input("E-mail cadastrado:").strip().lower()
    if st.button("Acessar Sistema"):
        st.session_state.user_email = e_input
        st.session_state.logged_in = True
        st.rerun()
else:
    df = carregar_dados()
    if not df.empty:
        # Verifica se quem logou é o Mestre ou Aluno
        is_adm = st.session_state.user_email == EMAIL_ADM
        
        # 4. Painel de Controle (Só para o Mestre)
        if is_adm:
            lista_emails = sorted(df['Endereço de e-mail'].unique().tolist())
            st.sidebar.header("🛡️ Painel ADM")
            aluno_alvo = st.sidebar.selectbox("Analisar aluno:", lista_emails)
        else:
            aluno_alvo = st.session_state.user_email
            st.sidebar.write("🌿 Bem-vindo!")

        # 5. Visualização e Inteligência Artificial
        user_data = df[df['Endereço de e-mail'] == aluno_alvo]
        st.title("Raio-X da Liberdade")
        
        if not user_data.empty:
            st.success(f"Encontramos {len(user_data)} registros para {aluno_alvo}")
            
            if st.button(f"Gerar Inteligência para {aluno_alvo}"):
                try:
                    # Usando o modelo estável para evitar Erro 404
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    with st.spinner('A IA está analisando os gatilhos...'):
                        contexto = user_data.tail(30).to_string(index=False)
                        prompt = f"Como Mentor Anti-Tabagista, analise estes dados e sugira ferramentas: \n\n{contexto}"
                        
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown(response.text)
                except Exception as e:
                    st.error("O Google está sincronizando sua chave.")
                    st.info(f"Dê F5 em 1 minuto. Detalhe técnico: {e}")
        else:
            st.error("Nenhum dado encontrado para este usuário.")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
