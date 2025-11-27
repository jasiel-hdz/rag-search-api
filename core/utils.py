from fastapi import UploadFile, HTTPException, File
from typing import Set
import os


def create_file_extension_validator(allowed_extensions: Set[str], error_message: str = None):
    """
    Factory function that creates a configurable file extension validator.
    Useful for creating reusable validators with different allowed extensions.
    
    Args:
        allowed_extensions: Set of allowed extensions (e.g., {".txt", ".pdf"})
        error_message: Custom error message. If None, automatically generated.
        
    Returns:
        Validator function that can be used as a FastAPI dependency
        
    Example:
        >>> validator = create_file_extension_validator({".txt", ".pdf"})
        >>> @app.post("/upload")
        >>> async def upload(file: UploadFile = Depends(validator)):
        >>>     ...
    """
    def validate_file_extension(file: UploadFile = File(...)) -> UploadFile:
        """
        Validates that the uploaded file has an allowed extension.
        Raises HTTPException if validation fails.
        
        Args:
            file: File to validate (obtained via File(...))
            
        Returns:
            UploadFile: Validated file
            
        Raises:
            HTTPException: If file has no name or extension is not allowed
        """
        if not file.filename:
            raise HTTPException(
                status_code=400, 
                detail="File must have a name"
            )
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Validate extension is allowed
        if file_extension not in allowed_extensions:
            if error_message:
                detail = error_message
            else:
                extensions_str = ", ".join(sorted(allowed_extensions))
                detail = (
                    f"File type not allowed. "
                    f"Only {extensions_str} files are allowed. "
                    f"Received: {file_extension}"
                )
            
            raise HTTPException(status_code=400, detail=detail)
        
        return file
    
    return validate_file_extension


# Predefined validators for common use
validate_document_file = create_file_extension_validator(
    allowed_extensions={".txt", ".pdf"},
    error_message="Only .txt and .pdf files are allowed"
)

validate_image_file = create_file_extension_validator(
    allowed_extensions={".jpg", ".jpeg", ".png", ".gif", ".webp"},
    error_message="Only image files (.jpg, .jpeg, .png, .gif, .webp) are allowed"
)

