import streamlit as st
import os
import embedchain
from streamlit.logger import get_logger
from translate import Translator

translator= Translator(to_lang="ml")

os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "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"
os.environ["PINECONE_API_KEY"] = "9a3d0633-db06-4ef7-a49e-3fae7210b765"

    
st.set_page_config(
    page_title=("AgroGPT"),
    page_icon="🌱",
    )

version = embedchain.__version__
st.title("💬 AgroGPT")
st.caption("🚀 developed by NeuBiom Labs!")
system_message = "You are an Agribot, here to help with information and context-specific recommendations for farming in Kerala for the following query. "
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

        for response in app.chat(system_message + prompt):
            msg_placeholder.empty()
            full_response += response
            # Translate to Malayalam
            full_response = translator.translate(full_response)
            print(full_response)

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
