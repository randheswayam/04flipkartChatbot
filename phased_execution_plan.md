# Phased Execution Plan: Flipkart AI Customer Support Chatbot

This document outlines a step-by-step, incremental implementation plan to build the Flipkart AI-Powered Customer Support Chatbot. Each phase is designed to be completed in a single session, leaving the application in a fully runnable, testable, and demonstrable state.

---

## Phase 1: Skeleton Chat UI & Project Setup
* **Goal**: Establish the repository structure, verify dependencies, configure environment variables, and launch a basic interactive chat interface.
* **Deliverables**:
  - `requirements.txt` verified and environment packages installed.
  - `.env` template created for `GROQ_API_KEY`.
  - Directory structure initialized: `data/`, `core/`, `utils/`.
  - `app.py` created as the entry point with a basic Streamlit chat UI.
* **App State**: The user can launch the app and type messages. The bot will respond by echoing the message back or with a mock greeting.
* **How to Verify**:
  1. Run `streamlit run app.py` in the workspace.
  2. Open the browser to the local URL (usually `http://localhost:8501`).
  3. Type "hello" and verify that it appears in the chat bubble and the bot responds with a template greeting.

---

## Phase 2: Dynamic Data Loader Utility & Sidebar Metadata
* **Goal**: Build the automatic scanner to discover and load data files in the `data/` directory.
* **Deliverables**:
  - Mock datasets added to the `data/` folder: `products.csv` and `faqs.csv` matching the schema in the PRD.
  - `utils/data_loader.py` implemented to dynamically scan `/data` and load CSV/JSON files.
  - `app.py` updated to load dataframes on startup and display files along with row counts in the Streamlit Sidebar.
* **App State**: The chat interface remains interactive with mock responses. The sidebar dynamically shows which datasets have been loaded.
* **How to Verify**:
  1. Run `streamlit run app.py`.
  2. Verify the sidebar displays:
     - `products.csv` loaded (with the correct number of rows).
     - `faqs.csv` loaded (with the correct number of rows).
  3. Drop a temporary dummy CSV (e.g., `test.csv`) into the `data/` directory and refresh the app; verify it shows up in the sidebar.

---

## Phase 3: Groq LLM Integration (Flipkart Persona Chat)
* **Goal**: Integrate the Groq LLM API and establish the helpful customer support agent persona.
* **Deliverables**:
  - `core/llm.py` wrapper implemented using the `groq` SDK and the `llama3-8b-8192` model.
  - System prompt written to define the bot persona (polite, helpful Flipkart assistant).
  - `app.py` updated to pass the user's message history to the LLM and display real responses.
* **App State**: The bot acts as a general customer support assistant, responding conversationally to greetings and general questions.
* **How to Verify**:
  1. Add a valid `GROQ_API_KEY` to the `.env` file.
  2. Run `streamlit run app.py`.
  3. Ask general questions like "Who are you?" or "Can you help me buy a phone?" and verify the bot answers dynamically in character.

---

## Phase 4: Product Database Queries (PandasSQL Engine)
* **Goal**: Build the search engine to query the product catalog using SQL syntax via PandasSQL.
* **Deliverables**:
  - `core/product_engine.py` implemented with two functions:
    - Listing all products (limited to 20).
    - Searching for specific products (fuzzy matching on name/category).
  - Temporary command prefixes (`/products` and `/search [item]`) registered in `app.py` to allow direct testing.
* **App State**: The bot can retrieve structured product details directly from `products.csv` using special keywords or slash commands.
* **How to Verify**:
  1. Run `streamlit run app.py`.
  2. Type `/products` in the chat input and verify that a table containing products, categories, and prices is displayed.
  3. Type `/search iPhone` and verify that the system searches `products.csv` and returns specifications/prices for the matching items.

---

## Phase 5: FAQ Search & Vector Store (ChromaDB Engine)
* **Goal**: Implement semantic similarity search for FAQs using a local vector store.
* **Deliverables**:
  - `core/faq_engine.py` implemented using `chromadb` and `sentence-transformers/all-MiniLM-L6-v2`.
  - Automatic ingestion logic: loads `faqs.csv` and creates embeddings in a persistent directory (`./chroma_db/`) on the first launch.
  - Retrieval logic: finds the top 3 similar FAQs and passes them as context to the Groq LLM to answer the user.
  - Temporary command prefix `/faq [question]` registered in `app.py`.
* **App State**: The bot can retrieve and conversationalize FAQ questions from `faqs.csv` using semantic search.
* **How to Verify**:
  1. Run `streamlit run app.py` (verify the `./chroma_db/` folder is generated in the root).
  2. Type `/faq return policy` and verify that the response retrieves the correct policy from the CSV and presents it in a helpful, conversational manner.

---

## Phase 6: Semantic Router (Intent Routing Integration)
* **Goal**: Connect the routing layer to automatically detect user intent and map messages to the correct engine without slash commands.
* **Deliverables**:
  - `core/router.py` implemented using `semantic-router[local]` with the `HuggingFaceEncoder`.
  - Router configured with training phrases for: `greeting`, `list_products`, `product_inquiry`, `faq`, and `general` (fallback).
  - Main loop in `app.py` modified to run user input through the router first, then dispatch to the correct engine. Temporary slash commands are removed.
* **App State**: The full chatbot system is integrated. The bot automatically understands what the user wants and responds using the appropriate source.
* **How to Verify**:
  1. Run `streamlit run app.py`.
  2. Type "Hi there!" -> Bot greets you and asks how to help.
  3. Type "Show me all items" or "products" -> Bot lists the product catalog.
  4. Type "Tell me about iPhone 15" -> Bot performs a fuzzy product search and displays details.
  5. Type "How long does shipping take?" -> Bot retrieves shipping FAQ via vector search and explains.
  6. Type "Tell me a joke" -> Bot falls back to general Groq LLM conversation.

---

## Phase 7: Edge Cases, Error Handling & UI Polish
* **Goal**: Harden the application against common errors and polish the user interface.
* **Deliverables**:
  - Robust exception handling in `llm.py` and `faq_engine.py` with friendly fallback messages.
  - Schema checking in `data_loader.py` to log a sidebar warning if columns are missing or malformed.
  - Cleaned UI styling in `app.py` (enhanced markdown formatting, loading indicators, helpful initial prompts).
* **App State**: The application is robust, error-tolerant, and ready for deployment or demo.
* **How to Verify**:
  1. Temporarily rename `GROQ_API_KEY` in `.env` to verify that the app displays a graceful warning instead of crashing.
  2. Corrupt or delete a column in `products.csv` and verify that the UI shows an informative warning.
  3. Interact with the chat and check that spinners (`st.spinner`) and layout margins look polished and responsive.
