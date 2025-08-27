from pydantic import BaseModel, Field
from typing import List

class CodeOption(BaseModel):
    """코드 후보 (추천/검색 결과 공통)"""
    index: int
    target: str
    score: float

class RecommendReq(BaseModel):
    """추천 요청"""
    text: str
    top_k: int = Field(15, ge=1, le=200)

class RecommendRes(BaseModel):
    """추천 응답"""
    options: List[CodeOption]

class SearchRes(BaseModel):
    """검색 응답"""
    query: str
    options: List[CodeOption]
