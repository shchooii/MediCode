from fastapi import APIRouter, HTTPException, Query
from app.schemas.code import RecommendReq, RecommendRes, SearchRes, CodeOption
from app.services.inference import recommend_codes, search_codes

router = APIRouter(prefix="/codes", tags=["codes"])

@router.post("/recommend", response_model=RecommendRes)
def codes_recommend(req: RecommendReq):
    """
    텍스트 기반 ICD 코드 추천 (Top-K)
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    options = recommend_codes(req.text, req.top_k)
    return RecommendRes(options=[CodeOption(**o) for o in options])

@router.get("/search", response_model=SearchRes)
def codes_search(
    q: str = Query(..., min_length=1, description="ICD 코드/라벨 검색어"),
    limit: int = Query(20, ge=1, le=200),
):
    """
    라벨 부분문자열 검색 (간단 휴리스틱)
    """
    options = search_codes(q, limit)
    return SearchRes(query=q, options=[CodeOption(**o) for o in options])
