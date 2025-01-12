import streamlit as st
import google.generativeai as genai
import httpx
import base64

# Configure the API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro-latest")


@st.cache_resource
def load_document(pdf_url):
    try:
      doc_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")
      return doc_data
    except Exception as e:
      st.error(f"Error loading document: {e}")
      return None

def generate_response(document_data, user_question):
    try:
        response = model.generate_content([{'mime_type':'application/pdf', 'data': document_data}, user_question])
        return response.text
    except Exception as e:
      st.error(f"Error generating response: {e}")
      return "Sorry, I couldn't process your request."

def generate_summary(document_data):
    try:
        prompt = "Proporciona un resumen de 4/5 lineas de este documento. Responde en español"
        response = model.generate_content([{'mime_type':'application/pdf', 'data': document_data}, prompt])
        return response.text
    except Exception as e:
      st.error(f"Error generating summary: {e}")
      return "Sorry, I couldn't generate a summary."

st.image('https://www.cdti.es/sites/default/files/logo_cdti_2024_con_banderas_soportes_digitales.jpg')
st.title("Conversational Assistant")

pdf_url = 'https://www.cdti.es/ayudas/ayudas-neotec-2024'

if "messages" not in st.session_state:
    st.session_state.messages = []

if pdf_url:
    document_data = load_document(pdf_url)
    if document_data:
        #with st.spinner("Generando resumen inicial..."):
        #     summary = generate_summary(document_data)
        st.subheader("Ficha Neotec 2024")
        resumen = """
NEOTEC 2024 apoya empresas de base tecnológica (EBT) con subvenciones de hasta el 70% (o 85% con doctores), con 
un máximo de 250.000€ (o 325.000€ con doctores), para proyectos basados en desarrollo tecnológico propio e I+D+i. 
Dirigido a pequeñas empresas innovadoras de hasta 3 años, con un capital mínimo de 20.000€ y un presupuesto mínimo 
de proyecto de 175.000€. Prioriza proyectos liderados por mujeres y financia gastos como personal, equipos y consultoría. 
La convocatoria fue del 10 de abril al 10 de mayo de 2024.
"""
        st.write(resumen)
        
        st.write('Puedes interactúar con el documento haciéndole preguntas.')

        for message in st.session_state.messages:
              with st.chat_message(message["role"]):
                  st.write(message["content"])

        if prompt := st.chat_input("Pregunta al documento"):
          st.session_state.messages.append({"role": "user", "content": prompt})
          with st.chat_message("user"):
                st.write(prompt)

          with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    response = generate_response(document_data, prompt)
                    st.write(response)
          st.session_state.messages.append({"role": "assistant", "content": response})

else:
  st.warning("Please enter a PDF URL")
