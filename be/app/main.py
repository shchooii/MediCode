from fastapi import FastAPI
from be.app.routers.codes import router as codes_router

app = FastAPI(
    title="ICD Coding — inference & codes",
    version="0.1.0",
)

# Codes 라우터 연결
app.include_router(codes_router)

@app.get("/health")
def health():
    return {"status": "ok"}
