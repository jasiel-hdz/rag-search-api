from fastapi import UploadFile, HTTPException, File
from typing import Set
import os


def create_file_extension_validator(allowed_extensions: Set[str], error_message: str = None):
    """
    Factory function que crea un validador de extensiones de archivo configurable.
    Útil para crear validadores reutilizables con diferentes extensiones permitidas.
    
    Args:
        allowed_extensions: Conjunto de extensiones permitidas (ej: {".txt", ".pdf"})
        error_message: Mensaje de error personalizado. Si es None, se genera automáticamente.
        
    Returns:
        Función validadora que puede usarse como dependencia de FastAPI
        
    Example:
        >>> validator = create_file_extension_validator({".txt", ".pdf"})
        >>> @app.post("/upload")
        >>> async def upload(file: UploadFile = Depends(validator)):
        >>>     ...
    """
    def validate_file_extension(file: UploadFile = File(...)) -> UploadFile:
        """
        Valida que el archivo subido tenga una extensión permitida.
        Lanza HTTPException si la validación falla.
        
        Args:
            file: El archivo a validar (obtenido mediante File(...))
            
        Returns:
            UploadFile: El archivo validado
            
        Raises:
            HTTPException: Si el archivo no tiene nombre o extensión no permitida
        """
        if not file.filename:
            raise HTTPException(
                status_code=400, 
                detail="El archivo debe tener un nombre"
            )
        
        # Obtener la extensión del archivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Validar que la extensión esté permitida
        if file_extension not in allowed_extensions:
            if error_message:
                detail = error_message
            else:
                extensions_str = ", ".join(sorted(allowed_extensions))
                detail = (
                    f"Tipo de archivo no permitido. "
                    f"Solo se permiten archivos {extensions_str}. "
                    f"Recibido: {file_extension}"
                )
            
            raise HTTPException(status_code=400, detail=detail)
        
        return file
    
    return validate_file_extension


# Validadores predefinidos para uso común
validate_document_file = create_file_extension_validator(
    allowed_extensions={".txt", ".pdf"},
    error_message="Solo se permiten archivos .txt y .pdf"
)

validate_image_file = create_file_extension_validator(
    allowed_extensions={".jpg", ".jpeg", ".png", ".gif", ".webp"},
    error_message="Solo se permiten archivos de imagen (.jpg, .jpeg, .png, .gif, .webp)"
)

