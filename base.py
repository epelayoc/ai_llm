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

st.title("Conversational Assistant")

pdf_url = 'https://www.cdti.es/sites/default/files/2024-11/manual_complementario_especifico_sneo_v.4.0.pdf'

if "messages" not in st.session_state:
    st.session_state.messages = []

if pdf_url:
    document_data = load_document(pdf_url)
    if document_data:
        with st.spinner("Generando resumen inicial..."):
             summary = generate_summary(document_data)
        st.subheader("Manual Neotec")
        st.write(summary)
        for message in st.session_state.messages:
              with st.chat_message(message["role"]):
                  st.write(message["content"])

        if prompt := st.chat_input("Ask a question about the document"):
          st.session_state.messages.append({"role": "user", "content": prompt})
          with st.chat_message("user"):
                st.write(prompt)

          with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = generate_response(document_data, prompt)
                    st.write(response)
          st.session_state.messages.append({"role": "assistant", "content": response})

else:
  st.warning("Please enter a PDF URL")
