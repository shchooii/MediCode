import os, json, uuid
from datetime import datetime
from typing import Dict, Any
import streamlit as st
from core.config import HISTORY_PATH, DOCS_DIR   # ← DOCS_DIR 추가

def load_history() -> Dict[str, Any]:
    if not os.path.exists(HISTORY_PATH): return {"documents": []}
    try: return json.load(open(HISTORY_PATH, "r", encoding="utf-8"))
    except Exception: return {"documents": []}

def save_history(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _write_doc_files(doc: Dict[str, Any]) -> None:
    """개별 문서를 DOCS_DIR/{id}.json 및 텍스트/코드 요약 파일로 저장"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    doc_path = os.path.join(DOCS_DIR, f"{doc['id']}.json")
    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    # 옵션: 임상 텍스트와 선택 코드를 별도 파일로도 떨굼
    txt_path = os.path.join(DOCS_DIR, f"{doc['id']}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(doc.get("text",""))

    tsv_path = os.path.join(DOCS_DIR, f"{doc['id']}_codes.tsv")
    items = doc.get("items", [])
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("index\tcode\ttarget\tscore\tsource\n")
        for it in items:
            f.write(
                f"{it.get('index','')}\t{it.get('code','')}\t{it.get('target','')}\t"
                f"{it.get('score','')}\t{it.get('source','')}\n"
            )

def upsert_document(doc_id: str, title: str, text: str, items: list) -> str:
    hist = load_history()
    docs = hist.get("documents", [])
    now = datetime.utcnow().isoformat()+"Z"
    if not doc_id.strip():
        doc_id = str(uuid.uuid4())

    # 갱신 or 추가
    existing = None
    for d in docs:
        if d["id"] == doc_id:
            existing = d
            break

    if existing:
        existing.update({"title": title, "text": text, "updated_at": now, "items": items})
        doc = existing
    else:
        doc = {"id": doc_id, "title": title, "text": text,
               "created_at": now, "updated_at": now, "items": items}
        docs.append(doc)
        hist["documents"] = docs

    # 저장
    save_history(hist)
    _write_doc_files(doc)   # ← 폴더에 개별 파일까지 저장
    return doc_id

def delete_document(doc_id: str) -> None:
    hist = load_history()
    hist["documents"] = [d for d in hist.get("documents", []) if d["id"] != doc_id]
    save_history(hist)
    # 개별 파일도 삭제(있으면)
    try:
        for ext in (".json", ".txt", "_codes.tsv"):
            path = os.path.join(DOCS_DIR, f"{doc_id}{ext}")
            if os.path.exists(path): os.remove(path)
    except Exception:
        pass

def load_document_to_session(doc_id: str, notify: bool = False) -> None:
    for d in load_history().get("documents", []):
        if d["id"] == doc_id:
            st.session_state.update({
                "doc_id_val": d["id"],
                "doc_title": d.get("title",""),
                "text": d.get("text",""),
                "selected": d.get("items", [])
            })
            if notify:
                st.toast("문서를 불러왔습니다.", icon="✅")
            return
