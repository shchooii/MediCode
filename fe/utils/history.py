import os, json, uuid
from datetime import datetime
from typing import Dict, Any
import streamlit as st
from core.config import HISTORY_PATH

def load_history() -> Dict[str, Any]:
    if not os.path.exists(HISTORY_PATH): return {"documents": []}
    try: return json.load(open(HISTORY_PATH, "r", encoding="utf-8"))
    except Exception: return {"documents": []}

def save_history(data: Dict[str, Any]) -> None:
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def upsert_document(doc_id: str, title: str, text: str, items: list) -> str:
    hist = load_history(); docs = hist.get("documents", []); now = datetime.utcnow().isoformat()+"Z"
    if not doc_id.strip(): doc_id = str(uuid.uuid4())
    for d in docs:
        if d["id"] == doc_id:
            d.update({"title": title, "text": text, "updated_at": now, "items": items})
            save_history(hist); return doc_id
    docs.append({"id": doc_id, "title": title, "text": text, "created_at": now, "updated_at": now, "items": items})
    hist["documents"] = docs; save_history(hist); return doc_id

def delete_document(doc_id: str) -> None:
    hist = load_history()
    hist["documents"] = [d for d in hist.get("documents", []) if d["id"] != doc_id]
    save_history(hist)

def load_document_to_session(doc_id: str) -> None:
    for d in load_history().get("documents", []):
        if d["id"] == doc_id:
            st.session_state.update({
                "doc_id": d["id"],
                "doc_title": d.get("title",""),
                "text": d.get("text",""),
                "selected": d.get("items", [])
            })
            st.success("문서를 불러왔습니다.")
