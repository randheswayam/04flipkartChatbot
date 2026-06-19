import streamlit as st
import time
from utils.data_loader import load_all_data

# Page configuration
st.set_page_config(
    page_title="Flipkart AI Support Bot",
    page_icon="🛒",
    layout="wide"
)

# App Title
st.title("🛒 Flipkart AI Customer Support")
st.caption("Phase 2: Dynamic Data Loading & Sidebar Metadata")

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

st.sidebar.subheader("💬 Model Details")
st.sidebar.info("🤖 llama3-8b-8192 (Phase 3)")

# Split page layout (left: chat history, right: dataset explorer preview)
col_chat, col_preview = st.columns([2, 1])

with col_chat:
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
                time.sleep(1)
            
            # Skeleton mock response echoing user message
            response = f"Hey there! I am your Flipkart support assistant. Currently, I am running on a **Phase 2 Data Loaded UI**.\n\nI detected your message: '{prompt}'.\n\nNote that my sidebar has successfully scanned and loaded our dataset files dynamically. Soon we will hook up Groq LLM to handle your queries! 🚀"
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

with col_preview:
    st.subheader("📊 Dataset Explorer")
    if datasets:
        selected_dataset = st.selectbox(
            "Select dataset to preview:",
            list(datasets.keys())
        )
        if selected_dataset:
            st.dataframe(datasets[selected_dataset].head(10))
    else:
        st.write("No datasets available to display.")
