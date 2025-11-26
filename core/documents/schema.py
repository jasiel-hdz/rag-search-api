from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str

class DocumentRecord(BaseModel):
    id: int
    filename: str
    content: str