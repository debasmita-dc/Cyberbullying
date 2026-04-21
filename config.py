import os

class Config:
    SECRET_KEY = "cybersafe-secret"

    BASE_DIR = os.path.dirname(__file__)

    # Database
    DB_PATH = os.path.join(BASE_DIR, "complaints.db")

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # ✅ Trained ML model folder
    MODEL_DIR = os.path.join(BASE_DIR, "..", "models", "toxicity-bert")

    OPENAI_MODEL = "gpt-5.2"
