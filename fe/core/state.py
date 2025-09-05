import streamlit as st
from typing import Dict, Any, List

def init_state():
    st.session_state.setdefault("api_base", "http://localhost:8000")
    st.session_state.setdefault("doc_id", "")
    st.session_state.setdefault("doc_title", "")
    st.session_state.setdefault("text", "")
    st.session_state.setdefault("selected", [])
    st.session_state.setdefault("unified_input", "")
    st.session_state.setdefault("top_k", 15)
    st.session_state.setdefault("unified_results", [])
    st.session_state.setdefault("last_mode", "")

def get_selected() -> List[Dict[str, Any]]:
    return st.session_state.get("selected", [])

def add_selection(item: Dict[str, Any], source: str):
    sel = get_selected()
    if any((it["index"], it["target"]) == (item["index"], item["target"]) for it in sel):
        st.info(f"이미 선택됨: {item['target']}")
        return
    sel.append({**item, "source": source})
    st.session_state["selected"] = sel

def remove_selection(i: int):
    sel = get_selected()
    if 0 <= i < len(sel):
        sel.pop(i)
        st.session_state["selected"] = sel
        st.rerun()
