from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    CKPT_PATH: str = "/home/mixlab/tabular/shchoi/MediCode/be/app/models/versions/hx08mx85/best_model.pt"
    MODEL_PATH: str = "/home/mixlab/tabular/icd-coding/RoBERTa-base-PM-M3-Voc/RoBERTa-base-PM-M3-Voc-hf"
    TARGET2INDEX_PATH: str = "/home/mixlab/tabular/shchoi/MediCode/be/app/models/versions/hx08mx85/target2index.json"

    TOP_K: int = 15
    CHUNK_SIZE: int = 512
    STRIDE: int = 64

    class Config:
        env_file = ".env"

settings = Settings()
