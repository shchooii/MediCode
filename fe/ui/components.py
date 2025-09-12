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
/* 카드 비주얼 */
.mc-card {
  border:1px solid var(--line); border-radius:12px; background:var(--card);
  padding:12px; margin:6px 0; box-shadow:0 2px 6px rgba(0,0,0,0.05);
  transition: box-shadow .12s ease, transform .12s ease;
}
.mc-card:hover { box-shadow:0 3px 10px rgba(0,0,0,0.08); transform: translateY(-1px); }

.mc-title { font-weight:800; font-size:14px; color:var(--text); line-height:1.2; }
.mc-meta  { font-size:12px; color:var(--muted); margin-top:4px; }

/* 버튼 사이즈/정렬 통일 */
.mc-actions { display:flex; justify-content:flex-end; align-items:center; height:100%; }
.mc-actions .stButton>button {
  height:28px; min-height:28px; padding:0 10px;
  font-size:12px; line-height:26px; border-radius:8px;
}
</style>
"""

# ───────── 카드 CSS (공식 API만 사용) ─────────
_CARD_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
  border:1px solid var(--line) !important;
  border-radius:8px !important;
  background:var(--card) !important;
  padding:4px 8px !important;   /* ← 세로 padding 최소화 */
  margin:4px 0 !important;
  box-shadow:0 1px 3px rgba(0,0,0,0.05);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  box-shadow:0 2px 6px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}

.mc-title { font-weight:700; font-size:14px; color:var(--text); line-height:1.2; }
.mc-meta  { font-size:12px; color:var(--muted); margin-top:2px; }

/* 버튼 사이즈 고정 */
.mc-actions { display:flex; align-items:center; justify-content:flex-end; height:100%; }
.mc-actions .stButton>button {
  height:28px; min-height:28px;
  padding:0 8px; font-size:12px; line-height:26px;
  border-radius:6px;
}
</style>
"""


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

                # 공식 API만: bordered 컨테이너 안에서 2열 구성
                with st.container(border=True):
                    left, right = st.columns([1, 0.20], vertical_alignment="center")
                    with left:
                        st.markdown(f"<div class='mc-title'>{title_txt}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='mc-meta'>{meta_txt}</div>", unsafe_allow_html=True)
                    with right:
                        st.markdown("<div class='mc-actions'>", unsafe_allow_html=True)
                        if st.button("➕", key=f"pick_{source}_{uid}"):
                            if not _already_selected(r):
                                add_selection(r, source)
                        st.markdown("</div>", unsafe_allow_html=True)

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

                with st.container(border=True):
                    left, right = st.columns([1, 0.20], vertical_alignment="center")
                    with left:
                        st.markdown(f"<div class='mc-title'>{title_txt}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='mc-meta'>{meta_txt}</div>", unsafe_allow_html=True)
                    with right:
                        st.markdown("<div class='mc-actions'>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{i}"):
                            remove_selection(i)
                        st.markdown("</div>", unsafe_allow_html=True)
