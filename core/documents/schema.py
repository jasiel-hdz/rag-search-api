from fastapi import UploadFile
from pydantic import BaseModel

class DocumentRequest(BaseModel):
    file: UploadFile

class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str

class DocumentRecord(BaseModel):
    id: int
    filename: str
    content: str