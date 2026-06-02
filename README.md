# ai-commerce-platform
AI-powered e-commerce platform featuring semantic product recommendations, intelligent shopping assistance, and sales analytics using FastAPI, Machine Learning, NLP, and Large Language Models.
# AI Commerce Platform

An AI-powered e-commerce platform that enhances product discovery through semantic search, intelligent recommendations, and conversational shopping assistance.

## Project Overview

This project aims to build an intelligent commerce platform that helps users discover relevant products using Natural Language Processing (NLP), Machine Learning, and Large Language Models (LLMs).

Instead of relying only on keyword-based search, the platform leverages semantic embeddings to understand user intent and recommend products based on meaning and context.

## Features

### Current Features

* FastAPI backend setup
* Product dataset preprocessing pipeline
* GitHub-integrated project structure
* Semantic text preparation for recommendation systems

### Upcoming Features

* Semantic product search
* AI-powered recommendation engine
* Conversational shopping assistant
* Personalized product recommendations
* Sales analytics dashboard
* Trend detection and business insights
* Vector similarity search using embeddings
* RAG-based product information retrieval

## Dataset

The project currently uses an e-commerce product dataset containing:

* Product ID
* Product Name
* Category
* Product Description
* Discounted Price
* Actual Price
* Discount Percentage
* Rating
* Rating Count
* User Reviews
* Product Links
* Product Images

Dataset Size:

* 1,465 Products
* 16 Attributes

## Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn

### Machine Learning & NLP

* Sentence Transformers
* Transformers
* Scikit-learn
* NumPy
* Pandas

### AI Components

* Semantic Embeddings
* Cosine Similarity Search
* Recommendation Systems
* Retrieval-Augmented Generation (Planned)

### Version Control

* Git
* GitHub

## Project Structure

```text
ai-commerce-platform/
│
├── app/
│   └── recommendation/
│       ├── data_loader.py
│       ├── embeddings.py
│       └── search.py
│
├── datasets/
│   └── products.csv
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### Clone Repository

```bash
git clone https://github.com/plk0309/ai-commerce-platform.git
cd ai-commerce-platform
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start FastAPI server:

```bash
uvicorn main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Recommendation Engine Workflow

```text
Product Dataset
       ↓
Data Cleaning
       ↓
Text Combination
       ↓
Sentence Embeddings
       ↓
Vector Representation
       ↓
Cosine Similarity Search
       ↓
Top Product Recommendations
```

## Current Progress

### Week 1

* Environment setup completed
* FastAPI backend configured
* GitHub repository setup completed
* Product dataset integrated
* Data loading pipeline implemented
* Semantic text preprocessing completed

### In Progress

* Product embedding generation
* Semantic recommendation engine
* Similarity search implementation

## Future Enhancements

* User personalization
* Chat-based shopping assistant
* Product review summarization
* Sales forecasting
* Inventory analytics
* LLM-powered product insights
* Real-time recommendation APIs

## Author

Palak Verma

GitHub:
https://github.com/plk0309

## License

This project is being developed as part of an AI/ML internship project for educational and research purposes.
