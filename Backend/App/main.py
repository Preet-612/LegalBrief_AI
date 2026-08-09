# import os
# import shutil
# import tempfile

# from fastapi import FastAPI, File, HTTPException, UploadFile
# from pydantic import BaseModel

# from App.Workflow.work import upload_document, ask_question

# app = FastAPI(title="LegalBrief API")

# UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "legalbrief_uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# class ChatRequest(BaseModel):
#     question: str


# @app.post("/api/upload")
# async def upload(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     return {"status": upload_document(file_path)}


# @app.post("/api/chat")
# async def chat(request: ChatRequest):
#     try:
#         return {"answer": ask_question(request.question)}
#     except RuntimeError as exc:
#         raise HTTPException(status_code=400, detail=str(exc))


import os
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from App.Workflow.work import upload_document, ask_question

app = FastAPI(title="LegalBrief API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only — restrict this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "legalbrief_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"status": upload_document(file_path)}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        return {"answer": ask_question(request.question)}
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))