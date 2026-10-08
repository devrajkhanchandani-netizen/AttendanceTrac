import re
import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from app.annotate import annotate_image
from app.attendance import (
    ABSENT,
    NEEDS_REVIEW,
    PRESENT,
    AttendanceReport,
    build_attendance,
)
from app.config import DETECTOR_BACKEND, MODEL_NAME, OUTPUT_DIR
from app.database import list_enrolled, load_database
from app.export import export_attendance
from app.recognition import FaceResult, recognize_faces

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
SESSION_IDLE_SECONDS = 60 * 60
SESSIONS_DIR = OUTPUT_DIR / "sessions"
SESSION_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")

STATUS_KEYS = {PRESENT: "present", ABSENT: "absent", NEEDS_REVIEW: "review"}


class ServiceError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass
class Session:
    id: str
    folder: Path
    class_name: str
    session_date: date
    photo_name: str
    width: int
    height: int
    faces: List[FaceResult]
    last_access: float
    # face number -> student name, or None meaning "not in this class"
    corrections: Dict[int, Optional[str]] = field(default_factory=dict)


class Store:
    def __init__(self):
        self.database: dict = {}
        self.enrolled: list = []
        self.sessions: Dict[str, Session] = {}
        self.lock = threading.Lock()              # protects self.sessions
        self.recognition_lock = threading.Lock()  # one recognition at a time


store = Store()


def warm_up() -> None:
    try:
        from deepface import DeepFace

        blank = np.zeros((160, 160, 3), dtype=np.uint8)
        DeepFace.represent(
            img_path=blank,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False,
        )
    except Exception as exc:
        print(f"Warm-up skipped: {exc}")


def startup() -> None:
    shutil.rmtree(SESSIONS_DIR, ignore_errors=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    store.database = load_database()
    store.enrolled = list_enrolled(store.database)
    warm_up()


def shutdown() -> None:
    shutil.rmtree(SESSIONS_DIR, ignore_errors=True)


def _purge_expired() -> None:
    now = time.time()
    with store.lock:
        expired = [s for s in store.sessions.values()
                   if now - s.last_access > SESSION_IDLE_SECONDS]
        for session in expired:
            del store.sessions[session.id]
    for session in expired:
        shutil.rmtree(session.folder, ignore_errors=True)


def get_session(session_id: str) -> Session:
    _purge_expired()
    session = None
    if SESSION_ID_PATTERN.match(session_id or ""):
        with store.lock:
            session = store.sessions.get(session_id)
    if session is None:
        raise ServiceError(404, "Session not found or expired. Please upload the photo again.")
    session.last_access = time.time()
    return session


def delete_session(session_id: str) -> None:
    session = get_session(session_id)
    with store.lock:
        store.sessions.pop(session.id, None)
    shutil.rmtree(session.folder, ignore_errors=True)


def remove_file(path) -> None:
    Path(path).unlink(missing_ok=True)


def _validate_upload(filename: str, data: bytes) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ServiceError(415, "Please upload a JPG, PNG or WEBP photo.")
    if not data:
        raise ServiceError(400, "The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ServiceError(413, "The photo is larger than 10 MB.")
    return ext


def _parse_date(text: str) -> date:
    text = (text or "").strip()
    if not text:
        return date.today()
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ServiceError(422, "Date must look like 2025-07-18.")


def _save_crop(image, face: FaceResult, path: Path) -> None:
    """Save a small crop of one face, with a margin around it."""
    height, width = image.shape[:2]
    x, y, w, h = face.box
    margin = int(0.25 * max(w, h))
    x0, y0 = max(0, x - margin), max(0, y - margin)
    x1, y1 = min(width, x + w + margin), min(height, y + h + margin)
    if x1 > x0 and y1 > y0:
        cv2.imwrite(str(path), image[y0:y1, x0:x1])


def create_session(data: bytes, filename: str,
                   class_name: str, date_text: str) -> Session:
    ext = _validate_upload(filename, data)
    session_date = _parse_date(date_text)
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ServiceError(400, "That file could not be read as an image.")
    height, width = image.shape[:2]

    session_id = uuid.uuid4().hex
    folder = SESSIONS_DIR / session_id
    (folder / "faces").mkdir(parents=True)
    original = folder / f"original{ext}"
    try:
        original.write_bytes(data)
        with store.recognition_lock:
            faces = recognize_faces(original, store.database)
        if not faces:
            raise ServiceError(
                422, "No faces were found in this photo. Try a clearer, closer photo.")
        for face in faces:
            _save_crop(image, face, folder / "faces" / f"{face.index}.jpg")
        cv2.imwrite(str(folder / "annotated.jpg"), annotate_image(original, faces))
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    finally:
        original.unlink(missing_ok=True)

    session = Session(
        id=session_id,
        folder=folder,
        class_name=(class_name or "").strip()[:100],
        session_date=session_date,
        photo_name=Path(filename or "photo").name[:100],
        width=width,
        height=height,
        faces=faces,
        last_access=time.time(),
    )
    with store.lock:
        store.sessions[session_id] = session
    return session


def set_corrections(session: Session,
                    items: List[Tuple[int, Optional[str]]]) -> None:
    valid_faces = {face.index for face in session.faces}
    cleaned: Dict[int, Optional[str]] = {}
    for face_number, student in items:
        if face_number not in valid_faces:
            raise ServiceError(422, f"There is no face number {face_number} in this photo.")
        if student is not None and student not in store.enrolled:
            raise ServiceError(422, f"'{student}' is not an enrolled student.")
        cleaned[face_number] = student
    session.corrections = cleaned


def _effective_faces(session: Session) -> List[FaceResult]:
    faces = []
    for face in session.faces:
        if face.index in session.corrections:
            student = session.corrections[face.index]
            if student is None:
                faces.append(replace(face, best_identity=None, decision="unknown"))
            else:
                faces.append(replace(face, best_identity=student,
                                     similarity=1.0, decision="match"))
        else:
            faces.append(face)
    return faces


def _build_report(session: Session) -> Tuple[AttendanceReport, set]:
    report = build_attendance(store.enrolled, _effective_faces(session))
    confirmed = {s for s in session.corrections.values() if s is not None}
    for record in report.records:
        if record.student in confirmed and record.status == PRESENT:
            record.confidence = None
    report.flagged_faces = [
        f for f in report.flagged_faces
        if not (f.face_index in session.corrections
                and session.corrections[f.face_index] is None)
    ]
    return report, confirmed


def build_payload(session: Session) -> dict:
    """Everything the web page needs, as plain JSON-friendly data."""
    report, confirmed = _build_report(session)

    counts = {PRESENT: 0, ABSENT: 0, NEEDS_REVIEW: 0}
    students = []
    for record in report.records:
        counts[record.status] += 1
        students.append({
            "name": record.student,
            "status": STATUS_KEYS[record.status],
            "score": None if record.confidence is None else round(record.confidence, 3),
            "source": "teacher" if (record.student in confirmed
                                    and record.status == PRESENT) else "auto",
        })

    faces = []
    for face in session.faces:
        x, y, w, h = face.box
        faces.append({
            "index": face.index,
            "decision": face.decision,
            "identity": face.best_identity,
            "score": round(face.similarity, 3),
            "box": {"x": x, "y": y, "w": w, "h": h},
            "box_pct": {
                "left": round(x / session.width * 100, 2),
                "top": round(y / session.height * 100, 2),
                "width": round(w / session.width * 100, 2),
                "height": round(h / session.height * 100, 2),
            },
        })

    flagged = {f.face_index: f for f in report.flagged_faces}
    original = {face.index: face for face in session.faces}
    review_numbers = sorted(
        {i for i, f in original.items() if f.decision != "match"}
        | set(flagged) | set(session.corrections)
    )
    review = []
    for number in review_numbers:
        face = original[number]
        if number in session.corrections:
            assigned = session.corrections[number]
            resolution = "not_in_class" if assigned is None else "assigned"
            reason = ("marked not in this class by the teacher" if assigned is None
                      else f"confirmed as {assigned} by the teacher")
        else:
            assigned, resolution = None, "unresolved"
            reason = flagged[number].reason if number in flagged else ""
        if number in flagged and flagged[number].reason.startswith("duplicate"):
            kind = "duplicate"
        elif face.decision == "review":
            kind = "borderline"
        elif face.decision == "unknown":
            kind = "unknown"
        else:
            kind = "match"
        review.append({
            "face": number,
            "kind": kind,
            "candidate": face.best_identity,
            "score": round(face.similarity, 3),
            "reason": reason,
            "resolution": resolution,
            "assigned_to": assigned,
            "crop_url": f"/api/attendance/{session.id}/faces/{number}",
        })

    return {
        "id": session.id,
        "class_name": session.class_name,
        "date": session.session_date.isoformat(),
        "photo": {
            "width": session.width,
            "height": session.height,
            "url": f"/api/attendance/{session.id}/photo",
        },
        "summary": {
            "present": counts[PRESENT],
            "absent": counts[ABSENT],
            "needs_review": counts[NEEDS_REVIEW],
            "total": len(report.records),
            "faces_detected": len(session.faces),
        },
        "enrolled": list(store.enrolled),
        "students": students,
        "faces": faces,
        "review": review,
    }


def build_excel(session: Session) -> Tuple[Path, str]:
    """Write the Excel file for this session. Returns (path, download name)."""
    report, _ = _build_report(session)
    safe_class = re.sub(r"[^A-Za-z0-9_-]+", "_", session.class_name).strip("_") or "class"
    filename = f"attendance_{safe_class}_{session.session_date.isoformat()}.xlsx"
    path = export_attendance(
        report,
        session.folder / filename,
        class_name=session.class_name,
        session_date=session.session_date,
        photo_name=session.photo_name,
    )
    return path, filename


def annotated_path(session: Session) -> Path:
    path = session.folder / "annotated.jpg"
    if not path.exists():
        raise ServiceError(404, "Photo not found.")
    return path


def crop_path(session: Session, face_number: int) -> Path:
    path = session.folder / "faces" / f"{int(face_number)}.jpg"
    if not path.exists():
        raise ServiceError(404, "Face not found.")
    return path
