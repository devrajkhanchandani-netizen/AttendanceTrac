from pathlib import Path
import pickle
from deepface import DeepFace

BASE_DIR = Path(__file__).parent
INDV_DIR = BASE_DIR / "Celebrities" / "indv"
OUTPUT_DIR = BASE_DIR / "embeddings"

OUTPUT_DIR.mkdir(exist_ok=True)

database = {}

supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}

for actor_folder in INDV_DIR.iterdir():

    if not actor_folder.is_dir():
        continue

    actor_name = actor_folder.name

    print(f"\nProcessing: {actor_name}")

    database[actor_name] = []

    for image_path in actor_folder.iterdir():

        if image_path.suffix.lower() not in supported_extensions:
            continue

        print(f"  → {image_path.name}")

        try:
            result = DeepFace.represent(
                img_path=str(image_path),
                model_name="ArcFace",
                detector_backend="retinaface"
            )

            embedding = result[0]["embedding"]

            database[actor_name].append({
                "image": image_path.name,
                "embedding": embedding
            })

            print("     ✓ Face processed")

        except Exception as e:
            print(f"     ✗ Failed: {e}")

database_path = OUTPUT_DIR / "face_database.pkl"

with open(database_path, "wb") as f:
    pickle.dump(database, f)

print("\n===================================")
print("DATABASE CREATED")
print("===================================")
print(f"Saved to: {database_path}")

for actor, images in database.items():
    print(f"{actor}: {len(images)} embeddings")