"""Detect faces in a photo and match each one against the database.

This module only RETURNS data. It does not print or draw anything.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from app.config import (
    ACCEPT_THRESHOLD,
    DETECTOR_BACKEND,
    MODEL_NAME,
    REVIEW_THRESHOLD,
)


@dataclass
class FaceResult:
    """What we learned about one detected face."""
    index: int                      # 1-based position in this photo
    box: Tuple[int, int, int, int]  # x, y, width, height
    best_identity: Optional[str]    # closest enrolled identity (even if rejected)
    similarity: float               # cosine similarity to that identity
    decision: str                   # "match" | "review" | "unknown"


def cosine_similarity(a, b) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def best_match(embedding, database: dict):
    """Compare one embedding to every reference. Returns (identity, similarity)."""
    best_name, best_sim = None, -1.0
    for name, references in database.items():
        for reference in references:
            sim = cosine_similarity(embedding, reference["embedding"])
            if sim > best_sim:
                best_name, best_sim = name, sim
    return best_name, best_sim


def decide(similarity: float,
           accept: float = ACCEPT_THRESHOLD,
           review: float = REVIEW_THRESHOLD) -> str:
    """Turn a similarity score into 'match', 'review' or 'unknown'."""
    if similarity >= accept:
        return "match"
    if similarity >= review:
        return "review"
    return "unknown"


def recognize_faces(image_path, database: dict) -> list:
    """Detect every face in `image_path` and return a list of FaceResult."""
    # Imported here so the rest of the app loads fast and can be tested
    # without TensorFlow.
    from deepface import DeepFace

    try:
        detections = DeepFace.represent(
            img_path=str(image_path),
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
        )
    except ValueError:
        # DeepFace raises ValueError when it finds no face at all.
        return []

    results = []
    for index, face in enumerate(detections, start=1):
        area = face.get("facial_area", {})
        box = (
            int(area.get("x", 0)),
            int(area.get("y", 0)),
            int(area.get("w", 0)),
            int(area.get("h", 0)),
        )
        name, similarity = best_match(face["embedding"], database)
        results.append(
            FaceResult(
                index=index,
                box=box,
                best_identity=name,
                similarity=similarity,
                decision=decide(similarity),
            )
        )
    return results
