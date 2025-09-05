import os

DEFAULT_API_BASE = os.getenv("MEDICODE_API_BASE", "http://localhost:8000")
HISTORY_PATH = os.getenv("MEDICODE_HISTORY_PATH", "./medicode_history.json")
PAGE_TITLE = "MediCode — ICD Assistant"
PAGE_ICON = "🩺"
