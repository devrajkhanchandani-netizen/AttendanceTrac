"""Loading the face database and listing enrolled students."""
import pickle
from pathlib import Path

from app.config import DATABASE_PATH


def load_database(path: Path = DATABASE_PATH) -> dict:
    """Load the pickle created by build_database.py.

    Shape: {"identity": [{"image": "file.jpg", "embedding": [...]}, ...]}
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Face database not found at {path}. Run build_database.py first."
        )
    with open(path, "rb") as f:
        return pickle.load(f)


def list_enrolled(database: dict) -> list:
    """All enrolled identities, sorted. Identities with no embeddings are skipped
    because they can never be recognised."""
    return sorted(name for name, refs in database.items() if refs)
