"""Command-line test: python scripts/run_attendance.py [path/to/group_photo]"""
import sys
from pathlib import Path

# Let this script import the `app` package from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.attendance import build_attendance
from app.config import BASE_DIR
from app.database import list_enrolled, load_database
from app.recognition import recognize_faces

DEFAULT_PHOTO = BASE_DIR / "Celebrities" / "group" / "HS9XbPkbQAALzb_.webp"


def main():
    photo = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PHOTO

    database = load_database()
    enrolled = list_enrolled(database)
    print(f"Enrolled students: {len(enrolled)}")
    print(f"Analyzing: {photo.name}\n")

    faces = recognize_faces(photo, database)
    print(f"Faces detected: {len(faces)}")
    for f in faces:
        print(f"  Face {f.index}: {f.best_identity} "
              f"(similarity {f.similarity:.3f}) -> {f.decision}")

    report = build_attendance(enrolled, faces)

    print("\nATTENDANCE")
    print("-" * 40)
    for r in report.records:
        conf = f"{r.confidence:.2f}" if r.confidence is not None else "-"
        print(f"{r.student:<14} {r.status:<13} {conf}")

    if report.flagged_faces:
        print("\nFACES FLAGGED FOR REVIEW")
        print("-" * 40)
        for f in report.flagged_faces:
            print(f"  Face {f.face_index}: {f.reason} (similarity {f.similarity:.2f})")


if __name__ == "__main__":
    main()
