import streamlit as st
import os
import embedchain
from streamlit.logger import get_logger

os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "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"
os.environ["PINECONE_API_KEY"] = "9a3d0633-db06-4ef7-a49e-3fae7210b765"

config_data = {
        "llm": {
        "provider": "huggingface",
        "config": {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "top_p": 0.5
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-mpnet-base-v2"
        }
    },
    "vectordb": {
        "provider": "pinecone",
        "config": {
            "metric": "cosine",
            "vector_dimension": 768,
            "index_name": "ragembed",
            "pod_config": {
                "environment": "gcp-starter",
                "metadata_config": {
                    "indexed": [
                        "url",
                        "hash"
                    ]
                }
            }
        }
    }
    }


@st.cache_resource
def embedchain_bot():
    return embedchain.App.from_config(config=config_data)
    
st.set_page_config(
    page_title=("AgriGPT"),
    page_icon="👋",
    )
version = embedchain.__version__
st.title(f"💬 AgriGPT {version}")
st.caption("🚀 developed by NeuBiom Labs!")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
        Hi! I'm AgriBot. """,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    app = embedchain_bot()

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

        for response in app.chat(prompt):
            msg_placeholder.empty()
            full_response += response

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
