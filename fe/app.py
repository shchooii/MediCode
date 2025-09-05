import streamlit as st
from core.config import PAGE_TITLE, PAGE_ICON
from core.state import init_state, get_selected, add_selection, remove_selection
from ui.styles import CSS
from ui.components import render_results, render_selected_codes
from utils.history import load_history, upsert_document, delete_document, load_document_to_session
from services.api import api_recommend, api_search  # 서비스 호출

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    f'<div class="header"><div class="title">{PAGE_ICON} {PAGE_TITLE}</div>'
    '<div class="subtitle">좌: Clinical Text · 우: 선택 코드 · 하단: 검색바</div></div>',
    unsafe_allow_html=True,
)

init_state()

# Sidebar - History
with st.sidebar:
    st.markdown("### 🗂️ History")
    docs = load_history().get("documents", [])
    if st.button("＋ 새 문서", use_container_width=True):
        st.session_state.update({
            "doc_id":"", "doc_title":"", "text":"", "selected":[],
            "unified_input":"", "unified_results":[], "last_mode":""
        })
    st.markdown("---")
    for d in docs:
        if st.button(d.get("title","(제목없음)"), key=f"sel_{d['id']}", use_container_width=True):
            load_document_to_session(d["id"])
        if st.button("삭제", key=f"del_{d['id']}"):
            delete_document(d["id"]); st.experimental_rerun()
        st.caption(f"{d['id']} · {d.get('updated_at','')}")

# Meta
m1, m2 = st.columns([3,7])
with m1:
    st.text_input("Document ID", key="doc_id")
    st.text_input("Title", key="doc_title", placeholder="예: 2025-09-05 외래 진료기록")
st.markdown("---")

# Main Layout
left, right = st.columns([5,5], gap="large")
with left:
    st.markdown("#### Clinical Text")
    st.text_area(" ", key="text", height=240, label_visibility="collapsed")
with right:
    st.markdown("#### Selected Codes")
    render_selected_codes(get_selected(), remove_selection)

# Unified Search
st.markdown("---")
st.markdown("### Assist — 검색 & 추천")

q_col, btn_col = st.columns([11,1])
with q_col:
    st.session_state["unified_input"] = st.text_input(
        "Query", value=st.session_state["unified_input"],
        placeholder="예: delirium vs dementia / F05 ...", label_visibility="collapsed"
    )
with btn_col:
    go = st.button("🔍", use_container_width=True)

c1, _ = st.columns([2, 10])  # 왼쪽은 입력 칸, 오른쪽은 빈 공간
with c1:
    st.session_state["top_k"] = st.number_input(
        "Top-K", min_value=1, max_value=200,
        value=int(st.session_state["top_k"]), step=1, label_visibility="collapsed"
    )
    
if go:
    q = st.session_state["unified_input"].strip()
    if q == "":
        st.session_state["unified_results"] = api_recommend(st.session_state["text"], st.session_state["top_k"])
        st.session_state["last_mode"] = "recommend"
    else:
        st.session_state["unified_results"] = api_search(q, 30)
        st.session_state["last_mode"] = "search"

if st.session_state["last_mode"] == "recommend":
    render_results("추천 결과", st.session_state["unified_results"], "recommend", add_selection)
elif st.session_state["last_mode"] == "search":
    render_results("검색 결과", st.session_state["unified_results"], "search", add_selection)

st.markdown('<div class="footer">© MediCode • MVP single-page UI</div>', unsafe_allow_html=True)
