import streamlit as st
from typing import List, Dict, Any, Iterable

# ───────── helpers ─────────
def _chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def _fmt_score(v):
    try: return f"{float(v):.2f}"
    except: return "-"

def _title_from_item(r):
    code, label = r.get("code"), r.get("label")
    if code and label: return f"{code} · {label}"
    if r.get("target"): return str(r["target"])
    if code: return str(code)
    return str(r.get("index",""))

def _index_from_item(r):
    return str(r.get("index", r.get("id", r.get("code",""))))

def _uniq_id(r):
    return str(r.get("code") or f'{r.get("index","")}_{r.get("target","")}')

def _already_selected(r):
    sel = st.session_state.get("selected", [])
    code = r.get("code")
    if code: return any(it.get("code")==code for it in sel)
    idx, tgt = r.get("index"), r.get("target")
    if idx is not None or tgt is not None:
        return any(it.get("index")==idx and it.get("target")==tgt for it in sel)
    t = _title_from_item(r)
    return any(_title_from_item(it)==t for it in sel)

# ───────── 카드 CSS ─────────
_CARD_CSS = """
<style>
.mc-card {
  display: flex; justify-content: space-between; align-items: center;
  border:1px solid var(--line); border-radius:10px; background:var(--card);
  padding:10px; margin:6px 0; box-shadow:0 2px 6px rgba(0,0,0,0.05);
}
.mc-card:hover { box-shadow:0 3px 10px rgba(0,0,0,0.08); transform: translateY(-1px); transition:.12s; }
.mc-card .text { display:flex; flex-direction:column; }
.mc-card .title { font-weight:700; font-size:14px; color:var(--text); }
.mc-card .meta  { font-size:12px; color:var(--muted); margin-top:2px; }
.mc-card .action { margin-left:8px; }
.mc-card .action .stButton>button {
  padding: 0.2rem 0.5rem; font-size:12px;
  border-radius: 8px;
}
</style>
"""

# ───────── renderers ─────────
def render_results(title, results, source, add_selection, cols_per_row=3):
    if not results: return
    st.markdown(_CARD_CSS, unsafe_allow_html=True)

    for row in _chunk(results, cols_per_row):
        cols = st.columns(len(row))
        for col, r in zip(cols, row):
            with col:
                uid       = _uniq_id(r)
                title_txt = _title_from_item(r)
                meta_txt  = f"index={_index_from_item(r)} · score={_fmt_score(r.get('score'))}"

                st.markdown(
                    f"""
                    <div class="mc-card">
                      <div class="text">
                        <div class="title">{title_txt}</div>
                        <div class="meta">{meta_txt}</div>
                      </div>
                      <div class="action" id="act_{uid}"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # 버튼은 별도로 렌더링 (오른쪽 action 영역)
                with st.container():
                    if st.button("➕", key=f"pick_{source}_{uid}"):
                        if not _already_selected(r):
                            add_selection(r, source)


def render_selected_codes(sel, remove_selection, cols_per_row=3):
    if not sel:
        st.info("선택된 코드가 없습니다."); return
    st.markdown(_CARD_CSS, unsafe_allow_html=True)

    for row in _chunk(list(enumerate(sel)), cols_per_row):
        cols = st.columns(len(row))
        for col, (i, it) in zip(cols, row):
            with col:
                title_txt = _title_from_item(it)
                meta_txt  = f"index={_index_from_item(it)} · score={_fmt_score(it.get('score'))} · {it.get('source','')}"

                st.markdown(
                    f"""
                    <div class="mc-card">
                      <div class="text">
                        <div class="title">{title_txt}</div>
                        <div class="meta">{meta_txt}</div>
                      </div>
                      <div class="action" id="act_sel_{i}"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.container():
                    if st.button("🗑️", key=f"del_{i}"):
                        remove_selection(i)
