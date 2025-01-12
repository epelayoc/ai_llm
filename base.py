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
st.title("Asistente conversacional")

pdf_url = 'https://www.cdti.es/sites/default/files/2024-04/convocatoria_neotec_2024.pdf'

if "messages" not in st.session_state:
    st.session_state.messages = []

if pdf_url:
    document_data = load_document(pdf_url)
    if document_data:
        #with st.spinner("Generando resumen inicial..."):
        #     summary = generate_summary(document_data)
        st.subheader("Convocatoria Neotec 2024 - CERRADA")
        resumen = """
El programa NEOTEC 2024 apoya la creación y consolidación de empresas de base tecnológica (EBT) con 
un modelo de negocio basado en el desarrollo de tecnología propia y actividades I+D+i. Ofrece subvenciones 
de hasta el 70% (o 85% con doctores) del presupuesto, con un máximo de 250.000€ (o 325.000€ con doctores) 
para pequeñas empresas innovadoras de máximo 3 años, con un capital social de 20.000€ y un presupuesto mínimo 
de proyecto de 175.000€. Se priman proyectos liderados por mujeres y se financian diversos gastos, incluyendo 
personal, equipos, y consultoría, siempre y cuando estén relacionados con el proyecto. La convocatoria estuvo abierta del 10 de abril al 10 de mayo de 2024.

"""
        st.write(resumen)
        #st.html("<a href='https://www.cdti.es/sites/default/files/2024-04/convocatoria_neotec_2024.pdf'>link al documento de la pasada convocatoria de 2024</a>")
        st.markdown(<a href='https://www.cdti.es/sites/default/files/2024-04/convocatoria_neotec_2024.pdf'>link al documento de la pasada convocatoria de 2024</a>, unsafe_allow_html=True)
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
