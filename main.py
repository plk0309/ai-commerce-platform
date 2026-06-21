from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.recommendation.search import load_search_engine
from app.api.recommendation import router as recommendation_router
from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router


# Runs on startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: load embeddings + FAISS into memory once
    print("🚀 Loading AI models...")
    load_search_engine()
    print("✅ Server ready.")
    yield
    # SHUTDOWN: nothing to clean up yet


app = FastAPI(
    title="AI Commerce Platform",
    description="Semantic search and AI-powered recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(recommendation_router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


@app.get("/")
def home():
    return {
        "status"   : "running",
        "platform" : "AI Commerce Platform",
        "version"  : "1.0.0",
        "docs"     : "/docs",
        "endpoints": [
            "GET  /api/v1/search?q=wireless+earbuds",
            "POST /api/v1/search",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)