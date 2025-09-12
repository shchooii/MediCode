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
            "doc_id_val":"", "doc_title":"", "text":"", "selected":[],
            "unified_input":"", "unified_results":[], "last_mode":""
        })
    st.markdown("---")
    for d in docs:
        c1, c2 = st.columns([7,3])
        # 문서 제목 버튼 (이름만)
        if c1.button(d.get("title","(제목없음)"), key=f"sel_{d['id']}", use_container_width=True):
            # 알림 없이 조용히 세션 로드
            load_document_to_session(d["id"], notify=False)
            st.rerun()
        # 삭제 버튼만
        if c2.button("삭제", key=f"del_{d['id']}", use_container_width=True):
            delete_document(d["id"])
            st.rerun()

# ───────────────────────── Main Layout (Left: Doc & Text & Selected / Right: Search+Results) ─────────────────────────
left, right = st.columns([6,4], gap="large")

with left:
    st.markdown("#### Document Info")
    st.text_input("Title", key="doc_title", placeholder="예: 2025-09-05 외래 진료기록")

    st.markdown("#### Clinical Text")
    st.text_area(" ", key="text", height=220, label_visibility="collapsed")

    st.markdown("#### Selected Codes")
    render_selected_codes(get_selected(), remove_selection)

    # ⬇⬇⬇ 저장/업데이트 버튼을 왼쪽으로 이동
    if st.button("저장/업데이트", key="save_btn", use_container_width=True):
        new_id = upsert_document(
            st.session_state.get("doc_id_val",""),
            st.session_state["doc_title"],
            st.session_state["text"],
            get_selected(),
        )
        st.session_state["doc_id_val"] = new_id
        st.success("기록에 저장했습니다.")
        st.rerun()

with right:
    st.markdown("#### Assist — 검색 & 추천")
    q_col, btn_col = st.columns([11,1])
    with q_col:
        st.session_state["unified_input"] = st.text_input(
            "Query (비우면 추천, 입력하면 검색)",
            value=st.session_state.get("unified_input",""),
            placeholder="예: delirium vs dementia / F05 ...",
            label_visibility="collapsed",
        )
    with btn_col:
        go = st.button("🔍", use_container_width=True)

    k1, _ = st.columns([2,10])
    with k1:
        st.session_state["top_k"] = st.number_input(
            "Top-K", min_value=1, max_value=200,
            value=int(st.session_state.get("top_k", 30)), step=1, label_visibility="collapsed"
        )

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

    if st.session_state.get("last_mode") == "recommend":
        render_results("추천 결과", st.session_state["unified_results"], "recommend", add_selection)
    elif st.session_state.get("last_mode") == "search":
        render_results("검색 결과", st.session_state["unified_results"], "search", add_selection)


# Footer
st.markdown('<div class="footer">© MediCode • MVP UI</div>', unsafe_allow_html=True)
