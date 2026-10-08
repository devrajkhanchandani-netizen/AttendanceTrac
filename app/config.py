from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "embeddings" / "face_database.pkl"

OUTPUT_DIR = BASE_DIR / "outputs"

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"

ACCEPT_THRESHOLD = 0.45
REVIEW_THRESHOLD = 0.35
