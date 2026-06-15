# AI-commerce-platform
AI-powered e-commerce platform featuring semantic product recommendations, intelligent shopping assistance, and sales analytics using FastAPI, Machine Learning, NLP, and Large Language Models.

# AI Commerce Platform

An AI-powered e-commerce recommendation system that combines semantic search, vector embeddings, recommendation ranking, intent detection, entity extraction, and conversational memory to provide intelligent product discovery experiences.

---

## Project Overview

Traditional e-commerce search relies heavily on keyword matching and often fails to understand the actual intent behind user queries.

This project uses:

* Sentence Transformers (MiniLM)
* Vector Embeddings
* FAISS Similarity Search
* FastAPI
* Intent Detection
* Entity Extraction
* Recommendation Reranking
* Session-Based Conversational Memory

to build a modern AI shopping assistant capable of understanding product meaning rather than only exact keywords.

---

## Features

### Semantic Product Search

Users can search using natural language:

Examples:

* wireless earbuds for gym
* laptop for machine learning
* fast charging type c cable
* waterproof bluetooth speaker

The system retrieves products based on semantic similarity instead of exact keyword matching.

---

### Vector Embeddings

Every product is converted into a dense vector representation using:

all-MiniLM-L6-v2

These embeddings capture semantic meaning and enable similarity search.

---

### FAISS Vector Search

Product embeddings are indexed using Facebook AI Similarity Search (FAISS).

Benefits:

* Extremely fast retrieval
* Scales to large product catalogs
* Efficient nearest-neighbor search

---

### Intent Detection

The recommendation engine detects query intent automatically.

Supported intents:

* Search
* Budget-based Search
* Brand-specific Search
* Product Comparison
* Follow-up Queries

Examples:

* earbuds under 2000
* only Samsung phones
* compare Dell vs HP laptops
* show cheaper options

---

### Entity Extraction

The system extracts structured constraints from user queries.

Supported entities:

* Budget
* Brand
* Category

Examples:

Query:

wireless earbuds under 1500

Extracted:

{
"budget": 1500,
"brand": null,
"category": "Electronics"
}

---

### Keyword-Aware Filtering

Additional filtering improves recommendation precision.

Examples:

* Wireless
* Bluetooth
* TWS
* Type-C
* Fast Charging
* Waterproof
* Gaming
* Mechanical
* SSD
* HDMI
* Neckband

This prevents semantically similar but incorrect products from appearing in results.

---

### Recommendation Reranking

Retrieved products are reranked using:

Final Score =
0.5 × Semantic Similarity +
0.3 × Product Rating +
0.2 × Product Popularity

This improves recommendation quality beyond pure vector similarity.

---

### Conversational Memory

Session-based memory enables follow-up recommendations.

Examples:

User:

wireless earbuds under 2000

User:

show cheaper ones

The system remembers previous context and adjusts recommendations accordingly.

---

## Architecture

User Query
↓
Intent Detection
↓
Entity Extraction
↓
MiniLM Embedding
↓
FAISS Retrieval
↓
Keyword Filtering
↓
Brand/Budget/Category Filters
↓
Reranking Engine
↓
Session Memory Update
↓
Final Recommendations

---

## Tech Stack

Backend

* Python
* FastAPI
* Uvicorn

Machine Learning

* Sentence Transformers
* all-MiniLM-L6-v2

Vector Search

* FAISS

Data Processing

* NumPy
* Pandas

API Documentation

* Swagger UI

---

## Project Structure

ai-commerce-platform/

├── app/

│ ├── api/

│ │ └── recommendation.py

│ │

│ └── recommendation/

│ ├── data_loader.py

│ ├── embeddings.py

│ ├── search.py

│ ├── ranking.py

│ └── recommender.py

│

├── artifacts/

│ ├── product_embeddings.npy

│ ├── products_df.pkl

│ └── faiss_index.bin

│

├── datasets/

├── main.py

├── requirements.txt

└── README.md

---

## Installation

Clone repository

git clone <repository-url>

cd ai-commerce-platform

Create virtual environment

python -m venv venv

Activate environment

Windows

venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

---

## Generate Embeddings

python -m app.recommendation.embeddings

This generates:

* product_embeddings.npy
* products_df.pkl

---

## Build Search Engine

python -m app.recommendation.search

This generates:

* faiss_index.bin

---

## Run Server

uvicorn main:app --reload

Server:

http://127.0.0.1:8000

Swagger Documentation:

http://127.0.0.1:8000/docs

---

## API Endpoints

### Semantic Search

GET

/api/v1/search

Example:

/api/v1/search?q=wireless+earbuds

---

POST

/api/v1/search

Request:

{
"query": "wireless earbuds",
"top_k": 5,
"min_rating": 4.0
}

---

### AI Recommendation

POST

/api/v1/recommend

Request:

{
"query": "wireless earbuds under 1500",
"session_id": "user_1",
"top_k": 5
}

Response:

{
"intent": "budget_filter",
"entities": {
"budget": 1500,
"brand": null,
"category": "Electronics"
},
"products": [...]
}

---

## Current Capabilities

Completed:

* Product Embeddings
* FAISS Indexing
* Semantic Search
* Rating Filter
* Price Filter
* Category Filter
* Intent Detection
* Entity Extraction
* Keyword Filtering
* Recommendation Reranking
* Session Memory
* FastAPI Integration
* Swagger Testing

---

## Future Enhancements

* Product Comparison Engine
* Hybrid Search (Keyword + Vector Search)
* User Personalization
* Analytics Dashboard
* LLM-Based Recommendation Explanations
* Clickstream Analytics
* Recommendation Feedback Loop
* Production Deployment
* Monitoring and Logging
* Platform Owner AI Analytics Assistant

---

## Author

Palak Verma

GitHub:
https://github.com/plk0309

## License

This project is being developed as part of an AI/ML internship project for educational and research purposes.
Built using FastAPI, Sentence Transformers, FAISS, and Recommendation System Engineering principles.
