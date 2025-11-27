import datetime
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pypdf import PdfReader

from core.documents.models import Document, Chunk
from core.vector.service import get_vector_service
from config import get_settings

settings = get_settings()
CHUNK_SIZE = 500


class DocumentService:
    
    def __init__(self, db: Session = None):
        self.db = db if db else None
        
    async def upload_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Uploads a document and processes the file.
        Saves the file, extracts text, creates database record and generates chunks.
        
        Args:
            file: The file to upload
            
        Returns:
            Dict with information about the processed document
            
        Raises:
            HTTPException: If an error occurs during the process
        """
        file_location = None
        try:
            # Ensure upload directory exists
            self._ensure_upload_directory_exists()
            
            # Save file to disk
            file_location = await self._save_file(file)
            
            # Extract text from file
            text = self._extract_text_from_file(file_location)
            
            # Create database record and chunks in a transaction
            document, chunks_count = self._create_document_with_chunks(file.filename, text)
            
            # Return processed document information
            return {
                "message": f"Document '{file.filename}' uploaded successfully",
                "document_id": document.id,
                "filename": document.filename,
                "chunks": chunks_count
            }
            
        except HTTPException:
            # Re-raise HTTPException without modification
            raise
        except (OSError, IOError) as e:
            # Clean up file if it exists and there was an I/O error
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass  # Ignore cleanup errors
            
            self._handle_exception(e, f"Error saving or reading file: {str(e)}")
        except ValueError as e:
            # Clean up file if it exists and there was a validation error
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            raise HTTPException(status_code=400, detail=str(e))
        except SQLAlchemyError as e:
            # Clean up file if it exists and there was a database error
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            self._handle_database_exception(e, "Error saving document to database")
        except Exception as e:
            # Clean up file if it exists and there was an unexpected error
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            self._handle_exception(e, f"Unexpected error processing document: {str(e)}")
    
    def _ensure_upload_directory_exists(self) -> None:
        """Ensures the upload directory exists, creates it if it doesn't."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def _save_file(self, file: UploadFile) -> str:
        """
        Saves the file to the upload directory.
        
        Args:
            file: The file to save
            
        Returns:
            Full path of the saved file
        """
        file_location = os.path.join(settings.UPLOAD_DIR, file.filename)
        
        # Reset file pointer in case it was already read
        await file.seek(0)
        content = await file.read()
        
        with open(file_location, "wb") as f:
            f.write(content)
        
        return file_location
    
    def _extract_text_from_file(self, file_location: str) -> str:
        """
        Extracts text from file according to its type.
        
        Args:
            file_location: File path
            
        Returns:
            Extracted text from file
            
        Raises:
            ValueError: If file type is not supported
            HTTPException: If PDF extraction fails
        """
        if file_location.endswith(".txt"):
            try:
                with open(file_location, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                # Try latin-1 if utf-8 fails
                with open(file_location, "r", encoding="latin-1") as f:
                    return f.read()
        elif file_location.endswith(".pdf"):
            return self._extract_text_from_pdf(file_location)
        else:
            raise ValueError(f"Unsupported file type: {os.path.splitext(file_location)[1]}")
    
    def _extract_text_from_pdf(self, file_location: str) -> str:
        """
        Extracts text from a PDF file.
        
        Args:
            file_location: Path to the PDF file
            
        Returns:
            Extracted text from all pages
            
        Raises:
            HTTPException: If PDF extraction fails
        """
        try:
            reader = PdfReader(file_location)
            text_parts = []
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text_parts.append(page_text)
                except Exception as e:
                    # Log warning but continue with other pages
                    print(f"Warning: Could not extract text from page {page_num}: {str(e)}")
                    continue
            
            if not text_parts:
                raise HTTPException(
                    status_code=400,
                    detail="PDF file appears to be empty or contains no extractable text. The PDF might be image-based or encrypted."
                )
            
            # Join all pages with double newline for readability
            full_text = "\n\n".join(text_parts)
            
            if not full_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="PDF file contains no extractable text. The PDF might be image-based or encrypted."
                )
            
            return full_text
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting text from PDF: {str(e)}"
            )
    
    def _create_document_with_chunks(self, filename: str, text: str) -> tuple[Document, int]:
        """
        Creates the document and its chunks in a transaction.
        Also generates and saves embeddings in ChromaDB.
        
        Args:
            filename: File name
            text: Text content
            
        Returns:
            Tuple with (Document, number of chunks created)
        """
        try:
            # Create document
            document = Document(
                filename=filename,
                content=text,
                created_at=datetime.datetime.now(datetime.timezone.utc)
            )
            self.db.add(document)
            self.db.flush()  # To get ID without committing
            
            # Create chunks
            chunks = []
            for i in range(0, len(text), CHUNK_SIZE):
                chunk_text = text[i:i + CHUNK_SIZE]
                chunk = Chunk(
                    document_id=document.id,
                    text=chunk_text
                )
                self.db.add(chunk)
                chunks.append(chunk)
            
            # Commit entire transaction
            self.db.commit()
            self.db.refresh(document)
            
            # Generate and save embeddings in ChromaDB (after commit)
            try:
                self._save_chunks_embeddings(chunks, document.id)
            except Exception as e:
                self._handle_exception(e, f"Error saving embeddings to ChromaDB: {str(e)}")
                self.db.rollback()
            
            return document, len(chunks)
            
        except SQLAlchemyError:
            # Rollback on error
            self.db.rollback()
            raise
    
    def _save_chunks_embeddings(self, chunks: list[Chunk], document_id: int) -> None:
        """
        Saves chunk embeddings to ChromaDB.
        
        Args:
            chunks: List of Chunk objects
            document_id: Document ID
        """
        try:
            # Prepare data for ChromaDB
            chunks_data = [
                {
                    "id": chunk.id,
                    "text": chunk.text
                }
                for chunk in chunks
            ]
            
            # Get vector service and save embeddings
            collection_name = settings.CHROMA_COLLECTION_NAME
            vector_service = get_vector_service(collection_name=collection_name)
            vector_service.add_chunks(chunks_data, document_id)
            
        except Exception as e:
            # Log error but don't fail main operation
            print(f"Error saving embeddings: {str(e)}")
            raise
    
    def _handle_database_exception(self, exception: Exception, message: str) -> None:
        """
        Handles database exceptions.
        
        Args:
            exception: The exception that occurred
            message: Descriptive error message
        """
        if self.db:
            self.db.rollback()
        
        print(f"{message}: {exception}")
        
        if isinstance(exception, HTTPException):
            raise exception
        
        raise HTTPException(status_code=500, detail=message)
    
    def _handle_exception(self, exception: Exception, message: str) -> None:
        """
        Handles general exceptions.
        
        Args:
            exception: The exception that occurred
            message: Descriptive error message
        """
        print(f"{message}: {exception}")
        
        if isinstance(exception, HTTPException):
            raise exception
        
        raise HTTPException(status_code=500, detail=message)
        
    