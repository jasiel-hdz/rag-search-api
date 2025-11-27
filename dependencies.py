from core.documents.services import DocumentService
from core.rag.services import RAGService
from fastapi import Depends, HTTPException, status
from database import sessionLocal
from config import get_settings

settings = get_settings()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_document_service(db=Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def get_rag_service() -> RAGService:
    return RAGService()