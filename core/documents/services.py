import datetime
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.documents.models import Document, Chunk
from config import get_settings

settings = get_settings()
CHUNK_SIZE = 500


class DocumentService:
    
    def __init__(self, db: Session = None):
        self.db = db if db else None
        
    async def upload_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Sube un documento y procesa el archivo.
        Guarda el archivo, extrae el texto, crea el registro en BD y genera chunks.
        
        Args:
            file: El archivo a subir
            
        Returns:
            Dict con información del documento procesado
            
        Raises:
            HTTPException: Si ocurre algún error durante el proceso
        """
        file_location = None
        try:
            # Asegurar que el directorio de upload existe
            self._ensure_upload_directory_exists()
            
            # Guardar archivo en disco
            file_location = await self._save_file(file)
            
            # Extraer el texto del archivo
            text = self._extract_text_from_file(file_location)
            
            # Crear registro en base de datos y chunks en una transacción
            document, chunks_count = self._create_document_with_chunks(file.filename, text)
            
            # Retornar información del documento procesado
            return {
                "message": f"Document '{file.filename}' uploaded successfully",
                "document_id": document.id,
                "filename": document.filename,
                "chunks": chunks_count
            }
            
        except HTTPException:
            # Re-lanzar HTTPException sin modificar
            raise
        except (OSError, IOError) as e:
            # Limpiar archivo si existe y hubo error de I/O
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass  # Ignorar errores al limpiar
            
            self._handle_exception(e, f"Error al guardar o leer el archivo: {str(e)}")
        except ValueError as e:
            # Limpiar archivo si existe y hubo error de validación
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            raise HTTPException(status_code=400, detail=str(e))
        except SQLAlchemyError as e:
            # Limpiar archivo si existe y hubo error de BD
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            self._handle_database_exception(e, "Error al guardar el documento en la base de datos")
        except Exception as e:
            # Limpiar archivo si existe y hubo error inesperado
            if file_location and os.path.exists(file_location):
                try:
                    os.remove(file_location)
                except OSError:
                    pass
            
            self._handle_exception(e, f"Error inesperado al procesar el documento: {str(e)}")
    
    def _ensure_upload_directory_exists(self) -> None:
        """Asegura que el directorio de upload existe, lo crea si no existe."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def _save_file(self, file: UploadFile) -> str:
        """
        Guarda el archivo en el directorio de upload.
        
        Args:
            file: El archivo a guardar
            
        Returns:
            Ruta completa del archivo guardado
        """
        file_location = os.path.join(settings.UPLOAD_DIR, file.filename)
        
        # Resetear el puntero del archivo por si ya fue leído
        await file.seek(0)
        content = await file.read()
        
        with open(file_location, "wb") as f:
            f.write(content)
        
        return file_location
    
    def _extract_text_from_file(self, file_location: str) -> str:
        """
        Extrae el texto del archivo según su tipo.
        
        Args:
            file_location: Ruta del archivo
            
        Returns:
            Texto extraído del archivo
            
        Raises:
            ValueError: Si el tipo de archivo no es soportado
        """
        if file_location.endswith(".txt"):
            try:
                with open(file_location, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                # Intentar con latin-1 si utf-8 falla
                with open(file_location, "r", encoding="latin-1") as f:
                    return f.read()
        elif file_location.endswith(".pdf"):
            raise ValueError("Extracción de PDF aún no implementada")
        else:
            raise ValueError(f"Tipo de archivo no soportado: {os.path.splitext(file_location)[1]}")
    
    def _create_document_with_chunks(self, filename: str, text: str) -> tuple[Document, int]:
        """
        Crea el documento y sus chunks en una transacción.
        
        Args:
            filename: Nombre del archivo
            text: Contenido del texto
            
        Returns:
            Tupla con (Document, número de chunks creados)
        """
        try:
            # Crear documento
            document = Document(
                filename=filename,
                content=text,
                created_at=datetime.datetime.now(datetime.timezone.utc)
            )
            self.db.add(document)
            self.db.flush()  # Para obtener el ID sin hacer commit
            
            # Crear chunks
            chunks = []
            for i in range(0, len(text), CHUNK_SIZE):
                chunk_text = text[i:i + CHUNK_SIZE]
                chunk = Chunk(
                    document_id=document.id,
                    text=chunk_text
                )
                self.db.add(chunk)
                chunks.append(chunk)
            
            # Commit de toda la transacción
            self.db.commit()
            self.db.refresh(document)
            
            return document, len(chunks)
            
        except SQLAlchemyError:
            # Rollback en caso de error
            self.db.rollback()
            raise
    
    def _handle_database_exception(self, exception: Exception, message: str) -> None:
        """
        Maneja excepciones de base de datos.
        
        Args:
            exception: La excepción ocurrida
            message: Mensaje descriptivo del error
        """
        if self.db:
            self.db.rollback()
        
        print(f"{message}: {exception}")
        
        if isinstance(exception, HTTPException):
            raise exception
        
        raise HTTPException(status_code=500, detail=message)
    
    def _handle_exception(self, exception: Exception, message: str) -> None:
        """
        Maneja excepciones generales.
        
        Args:
            exception: La excepción ocurrida
            message: Mensaje descriptivo del error
        """
        print(f"{message}: {exception}")
        
        if isinstance(exception, HTTPException):
            raise exception
        
        raise HTTPException(status_code=500, detail=message)
        
    