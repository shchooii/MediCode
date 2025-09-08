import streamlit as st
from core.config import PAGE_TITLE, PAGE_ICON
from core.state import init_state, get_selected, add_selection, remove_selection
from ui.styles import CSS
from ui.components import render_results, render_selected_codes
from utils.history import load_history, upsert_document, delete_document, load_document_to_session
from services.api import api_recommend, api_search  # 백엔드 호출

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    f'<div class="header"><div class="title">{PAGE_ICON} {PAGE_TITLE}</div>'
    '<div class="subtitle">좌: 문서 정보 고정 · 우: 검색 & 선택 진행</div></div>',
    unsafe_allow_html=True,
)

init_state()

# ───────────────────────── Sidebar — History ─────────────────────────
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
        c1, c2 = st.columns([7,3])
        if c1.button(d.get("title","(제목없음)"), key=f"sel_{d['id']}", use_container_width=True):
            load_document_to_session(d["id"])
        if c2.button("삭제", key=f"del_{d['id']}"):
            delete_document(d["id"]); st.experimental_rerun()
        st.caption(f"{d['id']} · {d.get('updated_at','')}")

# ───────────────────────── Main Layout (Left fixed info / Right search+select) ─────────────────────────
left, right = st.columns([5,5], gap="large")

# LEFT: 정보 고정 (문서 메타 + Clinical Text)
with left:
    st.markdown("#### Document Info")
    st.text_input("Document ID", key="doc_id")
    st.text_input("Title", key="doc_title", placeholder="예: 2025-09-05 외래 진료기록")
    st.markdown("---")
    st.markdown("#### Clinical Text")
    st.text_area(" ", key="text", height=360, label_visibility="collapsed")

# RIGHT: 검색 → 결과 → 선택(Selected Codes)
with right:
    # 검색 & 추천 (오른쪽에서 진행)
    st.markdown("#### Assist — 검색 & 추천")
    q_col, btn_col = st.columns([11,1])
    with q_col:
        st.session_state["unified_input"] = st.text_input(
            "Query (비우면 추천, 입력하면 검색)",
            value=st.session_state["unified_input"],
            placeholder="예: delirium vs dementia / F05 ...",
            label_visibility="collapsed",
        )
    with btn_col:
        go = st.button("🔍", use_container_width=True)

    # Top-K: 네모 칸(작게)
    k1, _ = st.columns([2,10])
    with k1:
        st.session_state["top_k"] = st.number_input(
            "Top-K", min_value=1, max_value=200,
            value=int(st.session_state["top_k"]), step=1, label_visibility="collapsed"
        )

    # 실행
    if go:
        q = st.session_state["unified_input"].strip()
        if q == "":
            st.session_state["unified_results"] = api_recommend(
                st.session_state["text"], st.session_state["top_k"]
            )
            st.session_state["last_mode"] = "recommend"
        else:
            st.session_state["unified_results"] = api_search(q, 30)
            st.session_state["last_mode"] = "search"

    # 결과
    if st.session_state.get("last_mode") == "recommend":
        render_results("추천 결과", st.session_state["unified_results"], "recommend", add_selection)
    elif st.session_state.get("last_mode") == "search":
        render_results("검색 결과", st.session_state["unified_results"], "search", add_selection)

    st.markdown("---")
    st.markdown("#### Selected Codes")
    render_selected_codes(get_selected(), remove_selection)

    # 저장
    if st.button("저장/업데이트", type="primary", use_container_width=True):
        new_id = upsert_document(
            st.session_state["doc_id"],
            st.session_state["doc_title"],
            st.session_state["text"],
            get_selected(),
        )
        st.session_state["doc_id"] = new_id
        st.success("기록에 저장했습니다.")

# Footer
st.markdown('<div class="footer">© MediCode • MVP UI</div>', unsafe_allow_html=True)
