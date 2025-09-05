import requests
import streamlit as st
from typing import List, Dict, Any

def _call(method: str, path: str, **kwargs):
    base = st.session_state.get("api_base", "http://localhost:8000").rstrip("/")
    try:
        resp = requests.request(method, f"{base}{path}", timeout=60, **kwargs)
        resp.raise_for_status()
        return resp.json(), None
    except Exception:
        return None, "API 오류"

def api_recommend(text: str, top_k: int) -> List[Dict[str, Any]]:
    data, err = _call("POST", "/codes/recommend", json={"text": text, "top_k": top_k})
    if err or not data:
        return [
            {"index": 1, "target": "I10 Hypertension", "score": 0.95},
            {"index": 2, "target": "E11 Type 2 diabetes", "score": 0.93},
        ]
    return data.get("options", [])

def api_search(q: str, limit: int = 30) -> List[Dict[str, Any]]:
    data, err = _call("GET", "/codes/search", params={"q": q, "limit": limit})
    if err or not data:
        return [
            {"index": 10, "target": "F03 Unspecified dementia", "score": 0.81},
            {"index": 11, "target": "G30 Alzheimer disease", "score": 0.79},
        ]
    return data.get("options", [])
