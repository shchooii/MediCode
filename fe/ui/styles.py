CSS = """
<style>
:root {
  --primary:#0D6EFD; --bg:#f7fafd; --card:#fff;
  --line:#e6eef6; --text:#0b2447; --muted:#6c757d;
}
.appview-container .main .block-container {
  padding-top: 3.2rem;
  padding-bottom: 0.6rem;
}
html, body .stApp { background: var(--bg); color: var(--text); }

.header {
  margin: 0 0 14px 0; padding: 18px 18px;
  background: linear-gradient(90deg,var(--primary),#3ea4ff); color:#fff;
  border-radius:16px; box-shadow: 0 6px 18px rgba(13,110,253,0.18);
}
.header .title { font-size: 22px; font-weight: 800; line-height: 1.3; }
.header .subtitle { font-size: 13px; opacity:.96; margin-top:6px; }

.result-card {
  border:1px solid var(--line); border-radius:10px; background:var(--card);
  padding:10px; margin:6px 0; box-shadow:0 2px 6px rgba(0,0,0,0.05);
}
.result-title { font-weight:700; font-size:14px; }
.result-meta { color:var(--muted); font-size:12px; }

.inline-search .stButton>button {
  padding: 0.45rem 0.6rem;
  border-radius: 10px;
  background: var(--primary); color:#fff; border: 0;
}
.inline-search input[type="text"] { height: 38px; }

.stNumberInput input {
  max-width: 80px;
  text-align: center;
}

.footer { color:var(--muted); font-size:12px; border-top:1px dashed var(--line);
  margin-top: 12px; padding-top: 8px; }
</style>
"""
