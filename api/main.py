from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from api import service

XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
NO_STORE = {"Cache-Control": "no-store"}  # browsers must not cache face images


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading the face database and warming up the models. This can take a while...")
    service.startup()
    print("Ready.")
    yield
    service.shutdown()


app = FastAPI(title="AttendanceTrac API", lifespan=lifespan)


@app.exception_handler(service.ServiceError)
async def service_error_handler(request, exc: service.ServiceError):
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


class Correction(BaseModel):
    face: int
    student: Optional[str] = None


class ConfirmRequest(BaseModel):
    corrections: List[Correction]


@app.get("/api/health")
def health():
    return {"status": "ok", "enrolled": len(service.store.enrolled)}


@app.post("/api/attendance")
def create_attendance(
    photo: UploadFile = File(...),
    class_name: str = Form(""),
    session_date: str = Form(""),
):
    data = photo.file.read(service.MAX_UPLOAD_BYTES + 1)
    session = service.create_session(data, photo.filename or "", class_name, session_date)
    return service.build_payload(session)


@app.get("/api/attendance/{session_id}")
def get_attendance(session_id: str):
    return service.build_payload(service.get_session(session_id))


@app.post("/api/attendance/{session_id}/confirm")
def confirm_faces(session_id: str, body: ConfirmRequest):
    session = service.get_session(session_id)
    service.set_corrections(session, [(c.face, c.student) for c in body.corrections])
    return service.build_payload(session)


@app.get("/api/attendance/{session_id}/photo")
def get_photo(session_id: str):
    session = service.get_session(session_id)
    return FileResponse(service.annotated_path(session),
                        media_type="image/jpeg", headers=NO_STORE)


@app.get("/api/attendance/{session_id}/faces/{face_number}")
def get_face(session_id: str, face_number: int):
    session = service.get_session(session_id)
    return FileResponse(service.crop_path(session, face_number),
                        media_type="image/jpeg", headers=NO_STORE)


@app.get("/api/attendance/{session_id}/excel")
def get_excel(session_id: str):
    session = service.get_session(session_id)
    path, filename = service.build_excel(session)
    # The Excel file is deleted right after it has been sent.
    return FileResponse(path, media_type=XLSX_TYPE, filename=filename,
                        headers=NO_STORE,
                        background=BackgroundTask(service.remove_file, path))


@app.delete("/api/attendance/{session_id}")
def end_session(session_id: str):
    service.delete_session(session_id)
    return {"deleted": True}
