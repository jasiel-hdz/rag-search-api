from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from core.documents.services import DocumentService
from core.utils import validate_document_file
from dependencies import get_document_service
from fastapi.encoders import jsonable_encoder

documents_router = APIRouter()

@documents_router.post("/upload")
async def upload_document(
    file: UploadFile = Depends(validate_document_file),
    document_service: DocumentService = Depends(get_document_service)
) -> JSONResponse:
    """
    Endpoint to upload a .txt or .pdf file.
    File extension validation is done via the validate_document_file dependency.
    """
    # Use service to process the document
    result = await document_service.upload_document(file)
    return JSONResponse(status_code=201, content=jsonable_encoder(result))