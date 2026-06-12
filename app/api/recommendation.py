from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.recommendation.search import search_products

router = APIRouter()


# ── Request / Response models ────────────────────────────────
class SearchRequest(BaseModel):
    query          : str
    top_k          : int           = 5
    min_rating     : float         = 0.0
    max_price      : Optional[float] = None
    category_filter: Optional[str]   = None


# ── GET /api/v1/search?q=wireless+earbuds ───────────────────
@router.get("/search")
def search_get(
    q        : str   = Query(..., description="Search query"),
    top_k    : int   = Query(5,   description="Number of results"),
    min_rating: float = Query(0.0, description="Minimum rating filter"),
    max_price : float = Query(None, description="Max price in ₹"),
    category  : str   = Query(None, description="Filter by category"),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = search_products(
        query=q,
        top_k=top_k,
        min_rating=min_rating,
        max_price=max_price,
        category_filter=category,
    )
    return {
        "query"       : q,
        "total_results": len(results),
        "products"    : results,
    }


# ── POST /api/v1/search  (richer filters via JSON body) ──────
@router.post("/search")
def search_post(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = search_products(
        query=req.query,
        top_k=req.top_k,
        min_rating=req.min_rating,
        max_price=req.max_price,
        category_filter=req.category_filter,
    )
    return {
        "query"       : req.query,
        "total_results": len(results),
        "products"    : results,
    }

from app.recommendation.recommender import recommend

class RecommendRequest(BaseModel):
    query     : str
    session_id: str = "default"
    top_k     : int = 5

@router.post("/recommend", summary="Full AI recommendation with intent + memory")
def get_recommendations(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = recommend(query=req.query, session_id=req.session_id, top_k=req.top_k)
    return {
        "query"        : req.query,
        "session_id"   : req.session_id,
        "intent"       : result["intent"],
        "entities"     : result["entities"],
        "total_results": len(result["products"]),
        "products"     : result["products"],
    }