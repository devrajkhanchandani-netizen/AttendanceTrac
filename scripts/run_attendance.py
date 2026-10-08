import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.annotate import annotate_image
from app.attendance import build_attendance
from app.config import BASE_DIR, OUTPUT_DIR
from app.database import list_enrolled, load_database
from app.export import export_attendance
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

    OUTPUT_DIR.mkdir(exist_ok=True)

    image_path = OUTPUT_DIR / f"annotated_{photo.stem}.jpg"
    cv2.imwrite(str(image_path), annotate_image(photo, faces))
    print(f"\nAnnotated photo saved to: {image_path}")

    excel_path = export_attendance(
        report,
        OUTPUT_DIR / f"attendance_{photo.stem}.xlsx",
        class_name="Demo class",
        photo_name=photo.name,
    )
    print(f"Excel report saved to:    {excel_path}")


if __name__ == "__main__":
    main()