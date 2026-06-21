# AI Commerce Platform 🛍️📊

An AI-powered e-commerce platform featuring a **Customer AI Shopping Assistant** and a **Platform Owner AI Analytics Assistant** — both powered by semantic search, intent detection, and Groq LLaMA for natural language responses.

Built as part of an AI/ML internship at **Katharos Techie**.

---

## Live Demo

> API running locally at `http://127.0.0.1:8000`
> Interactive docs: `http://127.0.0.1:8000/docs`

---

## What This Project Does

### 🛒 Customer AI Shopping Assistant
Understands natural language product queries and returns intelligent recommendations.

| User says | System does |
|-----------|-------------|
| `"wireless earbuds under ₹2000"` | Detects budget intent, extracts ₹2000 filter, searches semantically, filters wired products, reranks by quality |
| `"show cheaper ones"` | Inherits previous context via session memory, reduces budget to 60% |
| `"only boAt products"` | Applies brand filter on top of existing context |
| `"gaming keyboard mechanical with RGB"` | Extracts 3 simultaneous keyword constraints |

### 📊 Platform Owner AI Analytics Assistant
Answers business questions in natural language using real transaction data.

| Admin asks | System does |
|------------|-------------|
| `"show business KPIs"` | Returns total revenue, orders, customers, AOV |
| `"why did sales drop"` | Runs anomaly detection with z-scores |
| `"compare October vs November 2011"` | Month-over-month revenue comparison |
| `"which country buys the most"` | Revenue breakdown by country with share % |
| `"revenue trend over time"` | 3-month rolling comparison, growth direction |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI + Uvicorn | REST API, async request handling |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | Convert products and queries to 384-dim vectors |
| Vector Search | FAISS (IndexFlatIP) | Cosine similarity search across 1,465 products |
| LLM | Groq LLaMA 3.1-8b-instant | Natural language response generation |
| Data Processing | Pandas + NumPy | Analytics engine, data cleaning |
| Validation | Pydantic | Request/response schema validation |
| Config | python-dotenv | API key management |

---

## Project Architecture

```
User Query
    │
    ▼
POST /api/v1/chat
    │
    ├── Shopping query? ──────────────────────────────────┐
    │                                                      ▼
    │                                          Intent Detection
    │                                                 │
    │                                          Entity Extraction
    │                                          (budget, brand, category)
    │                                                 │
    │                                          Session Memory Check
    │                                          (follow-up handling)
    │                                                 │
    │                                          FAISS Semantic Search
    │                                                 │
    │                                          Keyword Filter
    │                                          (wireless vs wired, etc.)
    │                                                 │
    │                                          Quality Reranking
    │                                          (similarity + rating + popularity)
    │                                                 │
    └── Analytics query? ─────────────────────────────┐
                                                       ▼
                                          Analytics Intent Detection
                                                       │
                                          Pandas Analytics Engine
                                          (revenue, trends, anomalies)
                                                       │
                                                       │
                                                       │
                                                       ▼
                                          Groq LLaMA 3.1
                                          (Natural language reply)
                                                       │
                                                       ▼
                                              JSON Response
                                          {reply, products/data, intent}
```

---

## Project Structure

```
ai-commerce-platform/
│
├── app/
│   ├── recommendation/
│   │   ├── __init__.py
│   │   ├── data_loader.py       # Loads + cleans products.csv
│   │   ├── embeddings.py        # Generates + caches embeddings
│   │   ├── search.py            # FAISS index + semantic search
│   │   ├── ranking.py           # Quality reranking (similarity + rating + popularity)
│   │   └── recommender.py       # Intent detection, entity extraction, session memory
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── data_loader.py       # Loads + cleans online_retail.csv
│   │   ├── engine.py            # KPI, revenue, trends, anomaly detection
│   │   └── intent.py            # Analytics intent + entity extraction
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── groq_client.py       # Groq API wrapper
│   │   ├── shopping_prompt.py   # Shopping assistant prompt builder
│   │   └── analytics_prompt.py  # Analytics assistant prompt builder
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── recommendation.py    # GET+POST /search, POST /recommend
│   │   ├── analytics.py         # POST /analytics
│   │   └── chat.py              # POST /chat (unified endpoint)
│   │
│   ├── database/
│   └── utils/
│
├── datasets/
│   ├── products.csv             # 1,465 Amazon electronics products
│   └── online_retail.csv        # 541,909 UK retail transactions (2010-2011)
│
├── artifacts/                   # Auto-generated, gitignored
│   ├── product_embeddings.npy   # Shape: (1465, 384)
│   ├── products_df.pkl          # Cleaned product DataFrame
│   └── faiss_index.bin          # FAISS vector index
│
├── main.py                      # FastAPI app entry point
├── requirements.txt
├── .env                         # GROQ_API_KEY (never committed)
├── .gitignore
└── README.md
```

---

## Datasets

| Dataset | Rows | Source | Used For |
|---------|------|--------|---------|
| `products.csv` | 1,465 | Amazon Electronics (Kaggle) | Semantic search, recommendations |
| `online_retail.csv` | 541,909 | UCI ML Repository | Revenue analytics, trend analysis |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone the repository
```bash
git clone https://github.com/plk0309/ai-commerce-platform.git
cd ai-commerce-platform
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Add datasets
Place these files in the `datasets/` folder:
- `products.csv` — Amazon electronics dataset
- `online_retail.csv` — Online retail transaction dataset

### 6. Start the server
```bash
uvicorn main:app --reload-dir app --reload-dir datasets
```

First startup takes ~60 seconds to generate embeddings. Every startup after that is instant (loads from cache).

### 7. Open Swagger UI
```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### `POST /api/v1/chat` — Unified Chatbot (Main Endpoint)
Auto-routes between shopping and analytics assistants.

```json
// Shopping query
{
  "message": "recommend wireless earbuds under 2000",
  "session_id": "user_123",
  "role": "customer"
}

// Analytics query
{
  "message": "show business KPIs",
  "session_id": "admin_1",
  "role": "admin"
}
```

**Response includes:** `reply` (natural language), `intent`, `products` or `data`

---

### `POST /api/v1/recommend` — Full Recommendation Pipeline
```json
{
  "query": "gaming keyboard mechanical under 3000",
  "session_id": "user_123",
  "top_k": 5
}
```

---

### `GET /api/v1/search` — Semantic Search
```
/api/v1/search?q=wireless+earbuds&max_price=2000&min_rating=4.0
```

---

### `POST /api/v1/analytics` — Analytics Assistant
```json
{
  "query": "why did sales drop",
  "session_id": "admin_1"
}
```

---

## Sample Prompts to Test

### Shopping Assistant (`role: customer`)
```
"recommend a laptop for machine learning under 80000"
"wireless earbuds under 2000"
"show cheaper ones"              ← follow-up (uses session memory)
"only boAt earbuds"             ← brand filter follow-up
"gaming keyboard mechanical"
"type-c fast charging cable"
"waterproof bluetooth speaker under 3000"
"compare boAt vs JBL earbuds"
```

### Analytics Assistant (`role: admin`)
```
"show business KPIs"
"top 10 products by revenue"
"compare 2011-10 vs 2011-11"
"why did sales drop"
"which country buys the most"
"revenue trend over time"
"best day for sales"
"top customers by spending"
```

---

## How the Recommendation Engine Works

```
Query: "wireless earbuds under 2000"
         │
         ▼
Intent Detection ──────────► budget_filter
         │
         ▼
Entity Extraction ─────────► budget=2000, category=Electronics
         │
         ▼
Sentence Transformer ──────► 384-dim query vector
         │
         ▼
FAISS Search ──────────────► Top 20 similar products
         │
         ▼
Keyword Filter ────────────► Keep only 'wireless/bluetooth/tws' products
         │
         ▼
Budget Filter ─────────────► Keep only products ≤ ₹2,000
         │
         ▼
Quality Reranking ─────────► score = 0.5×similarity + 0.3×rating + 0.2×popularity
         │
         ▼
Top 5 results ─────────────► Passed to Groq LLaMA
         │
         ▼
Natural Language Reply ────► "Based on your ₹2,000 budget, I recommend..."
```

---

## Evaluation Criteria Coverage

| Assignment Requirement | Status |
|------------------------|--------|
| LLM Integration | ✅ Groq LLaMA 3.1-8b |
| Semantic Product Search | ✅ FAISS + Sentence Transformers |
| Recommendation System | ✅ Intent + Entity + Ranking |
| Conversational Memory | ✅ Session-based follow-ups |
| Analytics Assistant | ✅ 9 intent types, 8 engine functions |
| Anomaly Detection | ✅ Z-score based |
| Explainable Recommendations | ✅ LLM generates reasons |
| FastAPI Backend | ✅ 5 endpoints |
| Structured Architecture | ✅ Modular, production-style |
| Documentation | ✅ This README + Technical Guide PDF |

---

## Future Roadmap

- [ ] **Streamlit Frontend** — chat UI for demo
- [ ] **Product Comparison Engine** — side-by-side product comparison
- [ ] **Hybrid Search** — BM25 keyword + FAISS semantic search combined
- [ ] **User Profiling** — store preferences across sessions in PostgreSQL
- [ ] **Docker Deployment** — containerize for easy deployment
- [ ] **Cloud Deployment** — Railway or Render
- [ ] **Evaluation Metrics** — Precision@K, NDCG for recommendation quality
- [ ] **Review Summarization** — AI summary of customer reviews per product
- [ ] **Trending Products** — `/api/v1/trending` endpoint

---

## Author

**Palak** — AI/ML Development Intern at Katharos Techie

- GitHub: [@plk0309](https://github.com/plk0309)
- Project: [ai-commerce-platform](https://github.com/plk0309/ai-commerce-platform)

---

*Built with FastAPI · Sentence Transformers · FAISS · Groq LLaMA · Pandas*