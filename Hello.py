import streamlit as st
import os
from embedchain import App
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

app = App(config=config_data)

@st.cache_resource
def embedchain_bot():
    return App.from_config('config.yaml')
    
st.set_page_config(
    page_title="AgGPT",
    page_icon="👋",
    )

st.title("💬 AgriGPT")
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


