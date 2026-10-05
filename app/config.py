"""Central settings for AttendanceTrac. Change values here, not inside other files."""
from pathlib import Path

# Project root = the folder that contains the `app/` folder.
BASE_DIR = Path(__file__).resolve().parent.parent

# Where build_database.py saved the embeddings.
DATABASE_PATH = BASE_DIR / "embeddings" / "face_database.pkl"

# Pretrained models (same as your existing scripts).
MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"

# PLACEHOLDER thresholds. Both must be calibrated later with real data.
#   similarity >= ACCEPT_THRESHOLD                      -> "match"
#   REVIEW_THRESHOLD <= similarity < ACCEPT_THRESHOLD   -> "review"
#   similarity < REVIEW_THRESHOLD                       -> "unknown"
ACCEPT_THRESHOLD = 0.45
REVIEW_THRESHOLD = 0.35
