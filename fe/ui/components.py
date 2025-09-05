import streamlit as st
from typing import List, Dict, Any

def render_results(title: str, results: List[Dict[str, Any]], source: str, add_selection):
    if not results:
        return
    st.markdown(f"##### {title}")
    for r in results:
        c1, c2 = st.columns([8,2])
        with c1:
            st.markdown(
                f"<div class='result-card'><div class='result-title'>{r['target']}</div>"
                f"<div class='result-meta'>index={r['index']} · score={r['score']:.2f}</div></div>",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("선택", key=f"pick_{source}_{r['index']}"):
                add_selection(r, source)

def render_selected_codes(sel: List[Dict[str, Any]], remove_selection):
    if not sel:
        st.info("선택된 코드가 없습니다.")
    else:
        for i, it in enumerate(sel):
            c1, c2 = st.columns([8,2])
            with c1:
                st.markdown(
                    f"<div class='result-card'><div class='result-title'>{it['target']}</div>"
                    f"<div class='result-meta'>index={it['index']} · score={it['score']:.2f} · {it.get('source','')}</div></div>",
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("삭제", key=f"del_{i}"):
                    remove_selection(i)
