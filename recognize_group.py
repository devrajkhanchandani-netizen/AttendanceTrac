from pathlib import Path
import pickle
import cv2
import numpy as np
from deepface import DeepFace


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).parent

GROUP_DIR = BASE_DIR / "Celebrities" / "group"
DATABASE_PATH = BASE_DIR / "embeddings" / "face_database.pkl"

GROUP_IMAGE = GROUP_DIR / "HS9XbPkbQAALzb_.webp"
OUTPUT_IMAGE = GROUP_DIR / "recognized_result.jpg"


# ==========================================
# SETTINGS
# ==========================================

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"

# Prototype threshold.
# We'll tune this after seeing the actual results.
SIMILARITY_THRESHOLD = 0.45


# ==========================================
# COSINE SIMILARITY
# ==========================================

def cosine_similarity(a, b):

    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


# ==========================================
# LOAD DATABASE
# ==========================================

print("Loading face database...")

with open(DATABASE_PATH, "rb") as f:
    database = pickle.load(f)

print(f"Loaded {len(database)} identities.")

print(f"Analyzing: {GROUP_IMAGE.name}")
print()


# ==========================================
# DETECT FACES
# ==========================================

print("Detecting faces in group photo...")

faces = DeepFace.represent(
    img_path=str(GROUP_IMAGE),
    model_name=MODEL_NAME,
    detector_backend=DETECTOR_BACKEND,
    enforce_detection=True
)

print(f"Faces detected: {len(faces)}")
print()


# ==========================================
# LOAD IMAGE
# ==========================================

image = cv2.imread(str(GROUP_IMAGE))

recognized_people = set()


# ==========================================
# RECOGNIZE EACH FACE
# ==========================================

for index, face in enumerate(faces, start=1):

    query_embedding = face["embedding"]

    facial_area = face.get("facial_area", {})

    best_name = "Unknown"
    best_similarity = -1.0


    # Compare this face against
    # every reference image in the database

    for actor_name, references in database.items():

        for reference in references:

            similarity = cosine_similarity(
                query_embedding,
                reference["embedding"]
            )

            if similarity > best_similarity:

                best_similarity = similarity
                best_name = actor_name


    # ======================================
    # APPLY THRESHOLD
    # ======================================

    if best_similarity < SIMILARITY_THRESHOLD:

        final_name = "Unknown"

    else:

        final_name = best_name
        recognized_people.add(final_name)


    print(
        f"Face {index}: {final_name} "
        f"(similarity: {best_similarity:.3f})"
    )


    # ======================================
    # GET FACE LOCATION
    # ======================================

    x = int(facial_area.get("x", 0))
    y = int(facial_area.get("y", 0))

    w = int(facial_area.get("w", 0))
    h = int(facial_area.get("h", 0))


    # ======================================
    # DRAW FACE BOX
    # ======================================

    cv2.rectangle(
        image,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        2
    )


    # ======================================
    # DRAW NAME
    # ======================================

    label = f"{final_name} {best_similarity:.2f}"

    cv2.putText(
        image,
        label,
        (x, max(y - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


# ==========================================
# SAVE RESULT
# ==========================================

cv2.imwrite(
    str(OUTPUT_IMAGE),
    image
)


# ==========================================
# FINAL RESULTS
# ==========================================

print()
print("===================================")
print("RECOGNITION COMPLETE")
print("===================================")

print(f"Faces detected: {len(faces)}")
print(f"Recognized: {len(recognized_people)}")

print()
print("People recognized:")

for person in sorted(recognized_people):

    print(f"  ✓ {person}")


print()
print("Annotated image saved to:")

print(OUTPUT_IMAGE)