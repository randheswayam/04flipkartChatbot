# Product Requirements Document (PRD)
## Flipkart AI-Powered Customer Support Chatbot

**Version:** 1.0
**Date:** June 2026
**Stack:** Python · Streamlit · Groq LLM · ChromaDB · Semantic Router · PandasSQL

---

## 1. Overview

### 1.1 Purpose
Build a lightweight, AI-powered chatbot embedded in a Streamlit UI that serves Flipkart customers with:
- Natural, conversational responses (not rigid menu flows)
- FAQ answering via vector search (ChromaDB + Sentence Transformers)
- Product inquiry from a local dataset (CSV/JSON files via Pandas + PandasSQL)
- Smart intent routing via Semantic Router so the bot knows *what* the user wants before it answers

### 1.2 Problem Statement
Current FAQ bots dump a wall of pre-set questions the moment a user says "hi." This is jarring and unhelpful. Users need a bot that feels alive — one that asks what it can help with, understands intent, and responds precisely.

### 1.3 Goals
- Greet the user naturally; ask what they need
- Detect intent (FAQ / product search / order inquiry / small talk)
- Answer from the right data source (vector DB for FAQs, dataset files for products)
- Keep the Streamlit UI clean, minimal, and easy to navigate

---

## 2. User Flow

```
User opens app
     │
     ▼
Bot: "Hey! 👋 Welcome to Flipkart Support. How can I help you today?"
     │
     ├──► User says "hi" / "hello"
     │         └── Bot: "Great to have you here! You can ask me about products,
     │                    orders, returns, or anything else. What's on your mind?"
     │
     ├──► User says "products" / "show products" / "list items"
     │         └── Bot lists all products from dataset with name, price, category
     │
     ├──► User asks about a specific product ("Tell me about iPhone 15")
     │         └── Bot queries dataset → returns product details
     │
     ├──► User asks an FAQ ("What is your return policy?")
     │         └── Semantic Router → FAQ intent → ChromaDB vector search → Groq LLM answer
     │
     └──► User asks anything else
               └── Groq LLM answers with context from retrieved docs
```

---

## 3. Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                   │
│  (app.py — single file, chat interface)         │
└────────────────┬────────────────────────────────┘
                 │ user message
                 ▼
┌─────────────────────────────────────────────────┐
│           Semantic Router (router.py)           │
│  Routes to: faq / product / greeting / general  │
└────┬──────────────┬──────────────────┬──────────┘
     │              │                  │
     ▼              ▼                  ▼
┌─────────┐  ┌──────────────┐  ┌─────────────┐
│ChromaDB │  │ Dataset Layer│  │  Groq LLM   │
│FAQ Store│  │(pandas+sql)  │  │ (fallback / │
│(vector  │  │products.csv  │  │  enhancer)  │
│search)  │  │orders.csv    │  │             │
└─────────┘  └──────────────┘  └─────────────┘
     │              │                  │
     └──────────────┴──────────────────┘
                    │ response
                    ▼
             Streamlit Chat UI
```

---

## 4. Project Folder Structure

```
flipkart-chatbot/
│
├── app.py                    # Main Streamlit app (entry point)
├── requirements.txt          # All pip dependencies
├── .env                      # GROQ_API_KEY (never commit)
│
├── data/                     # All dataset files live here
│   ├── products.csv          # Product catalog
│   ├── orders.csv            # (optional) Order data
│   └── faqs.csv              # FAQ question-answer pairs
│
├── core/
│   ├── router.py             # Semantic Router — detects intent
│   ├── faq_engine.py         # ChromaDB ingestion + vector search
│   ├── product_engine.py     # Pandas + PandasSQL product queries
│   └── llm.py                # Groq LLM wrapper
│
└── utils/
    └── data_loader.py        # Scans /data folder, loads all CSVs/JSONs
```

**Critical rule:** `data_loader.py` must auto-scan the `/data` folder and load every `.csv` or `.json` file it finds. No hardcoded filenames. New datasets dropped into `/data/` are automatically picked up on next run.

---

## 5. Module Specifications

### 5.1 `utils/data_loader.py` — Auto Dataset Scanner

```python
# Pseudocode
def load_all_data(data_dir="data/"):
    dataframes = {}
    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            dataframes[file] = pd.read_csv(f"{data_dir}/{file}")
        elif file.endswith(".json"):
            dataframes[file] = pd.read_json(f"{data_dir}/{file}")
    return dataframes
```

- Runs at startup
- Returns a dict of `{filename: DataFrame}`
- Logs how many files were loaded

---

### 5.2 `core/router.py` — Intent Detection (Semantic Router)

| Intent | Example Utterances |
|--------|-------------------|
| `greeting` | "hi", "hello", "hey", "good morning" |
| `list_products` | "show products", "what do you sell", "product list", "products" |
| `product_inquiry` | "tell me about iPhone", "specs of Samsung TV", "price of Nike shoes" |
| `faq` | "return policy", "cancel order", "delivery time", "payment methods" |
| `order_status` | "where is my order", "track my package", "order 12345" |
| `general` | anything else |

- Uses `semantic-router[local]` with `HuggingFaceEncoder`
- Falls through to `general` if confidence < threshold (0.6)

---

### 5.3 `core/faq_engine.py` — ChromaDB Vector Store

**Ingestion (runs once on first launch):**
1. Reads `data/faqs.csv` (columns: `question`, `answer`)
2. Embeds questions using `sentence-transformers/all-MiniLM-L6-v2`
3. Stores in ChromaDB (local persistent store at `./chroma_db/`)

**Query:**
1. Embed incoming user message
2. Query ChromaDB for top-3 similar FAQs
3. Pass retrieved context + user question to Groq LLM
4. Return final answer

---

### 5.4 `core/product_engine.py` — Product Search via PandasSQL

```python
# Pseudocode for product listing
def list_all_products(df):
    return pandasql.sqldf("SELECT name, category, price FROM df LIMIT 20", locals())

# Product-specific search
def search_product(df, query):
    # Fuzzy match product name from query
    return df[df['name'].str.contains(query, case=False)]
```

Expected CSV columns: `name`, `category`, `price`, `brand`, `rating`, `description`

---

### 5.5 `core/llm.py` — Groq LLM Wrapper

- Model: `llama3-8b-8192` (fast, cheap)
- System prompt defines the bot persona: helpful Flipkart support agent
- Receives: `(user_message, context_docs)`
- Returns: clean string response
- Handles API errors gracefully with a fallback message

---

### 5.6 `app.py` — Streamlit UI

**Layout:**
```
┌──────────────────────────────────────────┐
│  🛒  Flipkart Support Bot               │
│  ─────────────────────────────────────  │
│                                          │
│  [Chat history scrollable area]          │
│                                          │
│  Bot: Hey! 👋 How can I help you today? │
│  You: show products                      │
│  Bot: Here are our top products...       │
│                                          │
│  ─────────────────────────────────────  │
│  [     Type your message here...    ] ▶  │
└──────────────────────────────────────────┘
```

**Streamlit components used:**
- `st.chat_message()` — chat bubbles
- `st.chat_input()` — input bar at bottom
- `st.session_state.messages` — conversation history
- `st.spinner()` — loading while bot thinks
- `st.sidebar` — optional: show loaded dataset names + FAQ count

**Sidebar (informational only):**
```
📦 Datasets Loaded
  ✅ products.csv (120 rows)
  ✅ faqs.csv (45 rows)

🔍 ChromaDB
  ✅ 45 FAQs indexed

💬 Model: llama3-8b-8192
```

---

## 6. Conversation Behavior Rules

| Trigger | Bot Response |
|---------|-------------|
| "hi" / "hello" | "Hey there! 👋 I'm Flipkart's support assistant. What can I help you with — products, orders, or general queries?" |
| "products" (alone) | Lists top products in a formatted table |
| Product name mentioned | Searches dataset and returns that product's details |
| FAQ question | Retrieves from ChromaDB + enhances with LLM |
| Unknown input | Passes to Groq LLM with a friendly disclaimer |
| Empty input | Ignores silently |

**Never** dump a list of FAQ questions when the user says "hi." The bot must ask first.

---

## 7. Data Requirements

### `data/products.csv` — Required Columns
| Column | Type | Description |
|--------|------|-------------|
| `name` | str | Product name |
| `category` | str | Electronics, Fashion, etc. |
| `brand` | str | Brand name |
| `price` | float | Price in ₹ |
| `rating` | float | 0–5 |
| `description` | str | Short description |

### `data/faqs.csv` — Required Columns
| Column | Type | Description |
|--------|------|-------------|
| `question` | str | FAQ question |
| `answer` | str | Answer text |

If columns differ, `data_loader.py` logs a warning and the engine skips that file gracefully.

---

## 8. Environment Setup

### `.env` file
```
GROQ_API_KEY=your_groq_api_key_here
```

### `requirements.txt`
```
streamlit
pandas
pandasql
python-dotenv
groq
semantic-router[local]
chromadb
sentence_transformers
```

### First-run sequence
1. Load `.env` → read `GROQ_API_KEY`
2. Scan `/data` folder → load all CSVs/JSONs
3. Initialize ChromaDB → ingest FAQs if not already indexed
4. Initialize Semantic Router with intent definitions
5. Launch Streamlit UI

---

## 9. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Response time | < 3 seconds for product queries; < 5s for LLM responses |
| Startup time | < 10 seconds on first run (embedding takes time) |
| Code size | `app.py` < 150 lines; each module < 100 lines |
| Readability | Beginner-friendly; every function has a docstring |
| Error handling | All API/DB calls wrapped in try/except with user-friendly messages |
| Portability | Runs locally with `streamlit run app.py` |

---

## 10. Out of Scope (v1.0)

- User authentication / login
- Real Flipkart API integration
- Payment processing
- Multi-language support
- Voice input/output
- Cloud deployment

---

## 11. Success Criteria

- [ ] Saying "hi" does NOT show a question list — bot asks what the user needs
- [ ] Saying "products" shows a clean product table from dataset
- [ ] Asking about a specific product returns its details from CSV
- [ ] FAQ questions are answered via ChromaDB + LLM
- [ ] New CSV/JSON files in `/data/` are auto-loaded without code changes
- [ ] App runs with `streamlit run app.py` and no extra setup beyond `.env`
- [ ] Code is readable enough for a junior dev to extend

---

*End of PRD — Flipkart AI Chatbot v1.0*
