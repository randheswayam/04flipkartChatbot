import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="Flipkart AI Support Bot",
    page_icon="🛒",
    layout="centered"
)

# App title and description
st.title("🛒 Flipkart AI Customer Support")
st.caption("Phase 1: Chat UI Skeleton")

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
        response = f"Hey there! I am your Flipkart support assistant. Currently, I am running on a **Phase 1 Skeleton UI**. I received your message: '{prompt}'.\n\nOnce the next implementation phases are completed, I will be able to route intents, query products from our database, and answer your FAQs! 🚀"
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
