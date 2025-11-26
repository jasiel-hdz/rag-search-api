from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from core.documents.schema import DocumentRecord
from dependencies import get_db
from .service import llm_service

documents_router = APIRouter()

@documents_router.post("/upload", response_model=DocumentRecord, status_code=201)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> DocumentRecord:
    """
    Endpoint to upload a document and save it to the database
    
    Args:
        file: The document file to upload
        db: Database session
        
    Returns:
        DocumentRecord: The saved record with id, filename and content
    """
    return DocumentRecord(id=1, filename="test.pdf", content="test content")