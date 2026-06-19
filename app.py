import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.data_loader import load_all_data
from core.llm import get_chat_response

# Load environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Flipkart AI Support Bot",
    page_icon="🛒",
    layout="centered"
)

# App Title
st.title("🛒 Flipkart AI Customer Support")
st.caption("Phase 3: Groq LLM Persona Chat")

# Load data at startup (cached)
@st.cache_data
def get_cached_data():
    return load_all_data("data")

datasets, warnings = get_cached_data()

# Render Sidebar Information
st.sidebar.title("System Status")
st.sidebar.markdown("---")

st.sidebar.subheader("📦 Datasets Loaded")
if datasets:
    for filename, df in datasets.items():
        st.sidebar.success(f"✅ **{filename}** ({len(df)} rows)")
else:
    st.sidebar.info("No datasets loaded from /data")

# Display warnings if there are missing/malformed schemas
if warnings:
    st.sidebar.subheader("⚠️ Warnings / Errors")
    for filename, warn_msg in warnings.items():
        st.sidebar.warning(f"**{filename}**:\n{warn_msg}")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Vector DB (ChromaDB)")
st.sidebar.info("⏳ Initialization Pending (Phase 5)")

# Display model status based on API key presence
st.sidebar.subheader("💬 Model Details")
api_key_loaded = bool(os.getenv("GROQ_API_KEY"))
if api_key_loaded:
    st.sidebar.success("🤖 llama3-8b-8192 (Active)")
else:
    st.sidebar.error("🤖 llama3-8b-8192 (API Key Missing)")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! 👋 Welcome to Flipkart Support. How can I help you today?"
        }
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input field
if prompt := st.chat_input("Type your message here..."):
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response with a simulated thinking spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Call Groq LLM wrapper with chat history
            response = get_chat_response(st.session_state.messages)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
