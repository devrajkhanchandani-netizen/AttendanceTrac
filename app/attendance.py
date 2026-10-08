from dataclasses import dataclass, field
from typing import List, Optional

PRESENT = "Present"
ABSENT = "Absent"
NEEDS_REVIEW = "Needs Review"


@dataclass
class StudentRecord:
    student: str
    status: str
    confidence: Optional[float] = None


@dataclass
class FlaggedFace:
    face_index: int
    best_identity: Optional[str]
    similarity: float
    reason: str


@dataclass
class AttendanceReport:
    records: List[StudentRecord] = field(default_factory=list)
    flagged_faces: List[FlaggedFace] = field(default_factory=list)


def build_attendance(enrolled: list, face_results: list) -> AttendanceReport:
    enrolled_set = set(enrolled)
    flagged = []

    winners = {}
    for face in face_results:
        if face.decision != "match" or face.best_identity not in enrolled_set:
            continue
        current = winners.get(face.best_identity)
        if current is None or face.similarity > current.similarity:
            if current is not None:
                flagged.append(FlaggedFace(
                    current.index, current.best_identity, current.similarity,
                    f"duplicate match for {current.best_identity}"))
            winners[face.best_identity] = face
        else:
            flagged.append(FlaggedFace(
                face.index, face.best_identity, face.similarity,
                f"duplicate match for {face.best_identity}"))

    borderline = {}
    for face in face_results:
        if face.decision == "review":
            flagged.append(FlaggedFace(
                face.index, face.best_identity, face.similarity,
                f"low confidence, possibly {face.best_identity}"))
            prev = borderline.get(face.best_identity)
            if prev is None or face.similarity > prev:
                borderline[face.best_identity] = face.similarity
        elif face.decision == "unknown":
            flagged.append(FlaggedFace(
                face.index, face.best_identity, face.similarity,
                "no confident match"))

    records = []
    for student in enrolled:
        if student in winners:
            records.append(StudentRecord(student, PRESENT, winners[student].similarity))
        elif student in borderline:
            records.append(StudentRecord(student, NEEDS_REVIEW, borderline[student]))
        else:
            records.append(StudentRecord(student, ABSENT, None))

    flagged.sort(key=lambda f: f.face_index)
    return AttendanceReport(records=records, flagged_faces=flagged)