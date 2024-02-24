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


def translate_string(from_lang, to_lang, string):
    try:
        input_text_elements = [ InputTextItem(text = string) ]
        response = text_translator.translate(content = input_text_elements, to = [to_lang], from_parameter = from_lang)
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
lang = "English"
final_prompt = ""

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

with st.sidebar:
    lang = st.radio(
    "Select Language",
    ["English", "Malayalam(മലയാളം)"], index=None)

if prompt := st.chat_input("Ask me anything!"):
    app = agribot()
 
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    if lang == "English":
            final_prompt = prompt
    else:
            tr_prompt = translate_string('ml','en', prompt)   
            final_prompt = tr_prompt
            
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""
        final_response = ""

        for response in app.query(final_prompt):
            msg_placeholder.empty()
            full_response += response
            print(response)
            # Translate to Malayalam
        if lang == "English":
            final_response = full_response
        else:
            tr_response = translate_string('en','ml', full_response )   
            final_response = tr_response
        
        msg_placeholder.markdown(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
