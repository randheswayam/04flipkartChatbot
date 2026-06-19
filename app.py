import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.data_loader import load_all_data
from core.llm import get_chat_response
from core.product_engine import list_all_products, search_product
from core.faq_engine import initialize_faq_database, query_faq, get_faq_count

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
st.caption("Phase 5: FAQ Search & Vector Store (ChromaDB Engine)")

# Load data at startup (cached)
@st.cache_data
def get_cached_data():
    return load_all_data("data")

datasets, warnings = get_cached_data()

# Initialize FAQ Database with loaded faqs.csv
if datasets and "faqs.csv" in datasets:
    initialize_faq_database(datasets["faqs.csv"])

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

# ChromaDB status
st.sidebar.subheader("🔍 Vector DB (ChromaDB)")
faq_count = get_faq_count()
if faq_count > 0:
    st.sidebar.success(f"✅ {faq_count} FAQs indexed")
else:
    st.sidebar.warning("⚠️ No FAQs indexed")

# Display model status based on API key presence
st.sidebar.subheader("💬 Model Details")
api_key_loaded = bool(os.getenv("GROQ_API_KEY"))
if api_key_loaded:
    st.sidebar.success("🤖 llama-3.1-8b-instant (Active)")
else:
    st.sidebar.error("🤖 llama-3.1-8b-instant (API Key Missing)")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hey! 👋 Welcome to Flipkart Support. How can I help you today?\n\n"
                "Here are some helpful commands you can run:\n"
                "- `/products`: Show list of products\n"
                "- `/search [item]`: Search products by name/brand\n"
                "- `/faq [question]`: Search our support FAQs"
            )
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

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # Check for Phase 4 & 5 commands
            if prompt.strip().startswith("/products"):
                response = list_all_products(datasets.get("products.csv"))
            elif prompt.strip().startswith("/search"):
                parts = prompt.strip().split(maxsplit=1)
                search_term = parts[1] if len(parts) > 1 else ""
                response = search_product(datasets.get("products.csv"), search_term)
            elif prompt.strip().startswith("/faq"):
                parts = prompt.strip().split(maxsplit=1)
                question = parts[1] if len(parts) > 1 else ""
                if question:
                    response = query_faq(question)
                else:
                    response = "Please specify a question. (e.g. `/faq return policy`)"
            else:
                # Fall back to Groq LLM
                response = get_chat_response(st.session_state.messages)
                
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
