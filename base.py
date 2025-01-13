import streamlit as st
import google.generativeai as genai
import httpx
import base64

# Configure the API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro-latest")

ti_NEOTEC = "Convocatoria Neotec 2024 - CERRADA"
url_NEOTEC = "https://www.cdti.es/sites/default/files/2024-04/convocatoria_neotec_2024.pdf"
txt_NEOTEC = """
El programa NEOTEC 2024 apoya la creación y consolidación de empresas de base tecnológica (EBT) con 
un modelo de negocio basado en el desarrollo de tecnología propia y actividades I+D+i. Ofrece subvenciones 
de hasta el 70% (o 85% con doctores) del presupuesto, con un máximo de 250.000€ (o 325.000€ con doctores) 
para pequeñas empresas innovadoras de máximo 3 años, con un capital social de 20.000€ y un presupuesto mínimo 
de proyecto de 175.000€. Se priman proyectos liderados por mujeres y se financian diversos gastos, incluyendo 
personal, equipos, y consultoría, siempre y cuando estén relacionados con el proyecto. La convocatoria estuvo abierta del 10 de abril al 10 de mayo de 2024.
"""
ti_TRANSMISIONES = "Convocatoria TransMisiones 2024 - CERRADA"
url_TRANSMISIONES = "https://www.cdti.es/sites/default/files/2024-05/convocatoria_trans_misiones_2024_firmada.pdf"
txt_TRANSMISIONES = """
La iniciativa TransMisiones 2024 es una acción que se ejecuta en colaboración entre el CDTI y la AEI, 
contemplada en el Plan Estatal de Investigación Científica, Técnica y de Innovación (PEICTI), por la que 
se coordina la financiación a agrupaciones de organismos de investigación y de difusión de conocimiento y 
agrupaciones de empresas que colaboran para el desarrollo conjunto de una actuación coordinada de I+D, que 
dé respuesta a los desafíos identificados en las prioridades temáticas o Misiones.
"""


@st.cache_resource
def load_document(pdf_url):
  if pdf_url:
    try:
      doc_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")
      return doc_data
    except Exception as e:
      st.error(f"Error loading document: {e}")
      return None
  else:
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


#st.image('https://www.cdti.es/sites/default/files/logo_cdti_2024_con_banderas_soportes_digitales.jpg')
st.image('https://www.notion.so/images/page-cover/nasa_tim_peake_spacewalk.jpg')
st.title("Asistente conversacional CDTI")
instrucciones = """
Esta aplicación te permite chatear sobre convocatorias del CDTI. Primero, selecciona la convocatoria que te interesa de un menú desplegable. 
Al hacerlo, verás información relevante sobre esa convocatoria y un enlace al documento oficial. A partir de ahí, puedes usar el chat para 
hacer preguntas específicas sobre la convocatoria y el asistente te dará respuestas basadas en el documento.
"""
st.info(instrucciones, icon="ℹ️")

option = st.selectbox(
    "¿Que convocatoria selecciónas?",
    ("NEOTEC", "TRANSMISIONES"),
)
convocatorias = {
    'NEOTEC': (ti_NEOTEC, url_NEOTEC,txt_NEOTEC),
    'TRANSMISIONES': (ti_TRANSMISIONES, url_TRANSMISIONES,txt_TRANSMISIONES) }


if "messages" not in st.session_state:
    st.session_state.messages = []

# Only proceed if an option has been selected
if option:
    titulo, pdf_url, resumen = convocatorias[option]
    document_data = load_document(pdf_url)

    if document_data:
            st.subheader(titulo)
            st.markdown(f'<a href="{pdf_url}">Enlace al documento de la convocatoria</a>', unsafe_allow_html=True)
            st.write(resumen)
            st.markdown('Plantea tus cuestiones a continuacion (ej: `¿Cuales son los potenciales beneficiarios de esta convocatoria?` )')

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
