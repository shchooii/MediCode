import json, torch
from transformers import AutoTokenizer
from pathlib import Path
from typing import List, Dict, Tuple
from ..core.config import settings
from ..models.modules.plm_icd import PLMICD

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


_tokenizer, _model, _i2t = None, None, []

def _build_index2target(t2i: Dict[str, int], num_classes: int) -> List[str]:
    i2t = [''] * num_classes
    for t, i in t2i.items():
        if 0 <= i < num_classes:
            i2t[i] = t
    for i in range(num_classes):
        if not i2t[i]:
            i2t[i] = str(i)
    return i2t

def _encode_chunks(tokenizer, text: str, *, chunk_size: int, stride: int):
    enc = tokenizer(
        text, max_length=chunk_size, truncation=True,
        stride=stride, return_overflowing_tokens=True,
        padding='max_length', return_tensors='pt'
    )
    return enc['input_ids'], enc['attention_mask']

def _load_once():
    global _tokenizer, _model, _i2t
    if _model is not None:
        return
    # target2index
    t2i = json.loads(Path(settings.TARGET2INDEX_PATH).read_text(encoding="utf-8"))
    t2i = {str(k): int(v) for k, v in t2i.items()}
    num_classes = max(t2i.values()) + 1
    _i2t = _build_index2target(t2i, num_classes)

    _tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_PATH, use_fast=True)
    model = PLMICD(num_classes=num_classes, model_path=settings.MODEL_PATH).to(DEVICE)

    blob = torch.load(settings.CKPT_PATH, map_location=DEVICE)
    state = blob.get("state_dict", blob.get("model_state_dict", blob)) if isinstance(blob, dict) else blob
    try:
        model.load_state_dict(state, strict=False)
    except Exception:
        fixed = {k.replace("module.", ""): v for k, v in state.items()}
        model.load_state_dict(fixed, strict=False)
    model.eval()
    _model = model

def recommend_codes(text: str, top_k: int):
    _load_once()
    ids, attn = _encode_chunks(_tokenizer, text, chunk_size=settings.CHUNK_SIZE, stride=settings.STRIDE)
    ids, attn = ids.unsqueeze(0).to(DEVICE), attn.unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = _model(input_ids=ids, attention_mask=attn)
        probs = torch.sigmoid(logits)
        vals, idxs = torch.topk(probs, k=min(top_k, probs.size(-1)), dim=-1)
    return [
        {"index": i, "target": _i2t[i] if 0 <= i < len(_i2t) else str(i), "score": float(p)}
        for p, i in zip(vals[0].tolist(), idxs[0].tolist())
    ]

def search_codes(query: str, limit: int = 20):
    _load_once()
    q = query.strip().lower()
    hits = []
    for idx, t in enumerate(_i2t):
        s = t.lower()
        if q in s:
            pos = s.find(q)
            score = 1.0 / (1 + pos) + 0.001 / max(1, len(s))
            if s == q: score += 1.0
            hits.append((idx, t, score))
    hits.sort(key=lambda x: x[2], reverse=True)
    return [{"index": i, "target": t, "score": float(sc)} for i, t, sc in hits[:limit]]
