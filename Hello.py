import streamlit as st
import os
from embedchain import App
from streamlit.logger import get_logger

os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "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"
os.environ["PINECONE_API_KEY"] = "9a3d0633-db06-4ef7-a49e-3fae7210b765"

st.set_page_config(
    page_title="AgGPT",
    page_icon="👋",
    )

st.title("💬 AgriGPT")
st.caption("🚀 developed by NeuBiom Labs!")
