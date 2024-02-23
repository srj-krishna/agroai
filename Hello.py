import streamlit as st
import os
import embedchain
from streamlit.logger import get_logger
import azure.ai.translation.text
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

text_translator = TextTranslationClient(credential = TranslatorCredential("8a775052516145059fc3839081b55967", "southeastasia"));
os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "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"
os.environ["PINECONE_API_KEY"] = "9a3d0633-db06-4ef7-a49e-3fae7210b765"

with st.sidebar:
    lang = st.radio(
    "Select Language",
    ["English", "Malayalam(മലയാളം)"],
    index=None,)
    message_placeholder.markdown(f"Changing language to {lang}")

def translate_string(lang_code, string):
    try:
        input_text_elements = [ InputTextItem(text = string) ]
        response = text_translator.translate(content = input_text_elements, to = [lang_code], from_parameter = 'en')
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                return translated_text.text

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
        return string  # return original string if translation fails
    
st.set_page_config(
    page_title=("AgroGPT"),
    page_icon="🌱",
    )

version = embedchain.__version__
st.title("💬 AgroGPT")
st.caption("🚀 developed by NeuBiom Labs!")
system_message = "You are an Agribot, here to help with information and context-specific recommendations for farming in Kerala for the following query. If you don't know something just politely say that you don't have the information."

@st.cache_resource
def agribot():
    return embedchain.App.from_config("config.yaml")
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
        Hi! I'm AgriBot, your personal agricultural assistant. I'm here to help you with information and context-specific recommendations for farming in Kerala. I can guide you through every step of the farming process. How can I help you today? """,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    app = agribot()

    if prompt.startswith("/add"):
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
        prompt = prompt.replace("/add", "").strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Adding to knowledge base...")
            app.add(prompt)
            message_placeholder.markdown(f"Added {prompt} to knowledge base!")
            st.session_state.messages.append({"role": "assistant", "content": f"Added {prompt} to knowledge base!"})
            st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""

        for response in app.query(system_message + prompt):
            msg_placeholder.empty()
            full_response += response
            # Translate to Malayalam
            
        tr_response = translate_string('ml', full_response )    
        msg_placeholder.markdown(tr_response)
        st.session_state.messages.append({"role": "assistant", "content": tr_response})
