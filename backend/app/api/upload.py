import shutil
import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app import models
from PIL import Image
import io

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Validate File Size (Approximation based on Content-Length header, or reading chunks)
    # Reading into memory for Pillow validation is necessary anyway.
    
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum limit of 10MB"
        )
        
    # 2. Validate Content Type (MIME)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed."
        )

    # 3. Validate with Pillow (Real Image Check)
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Verify it's an image
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. The file is corrupted or not an image."
        )

    # 4. Save File safely
    # Reset cursor after verify() might be needed if we were to save `image` object, 
    # but we are writing raw `contents` to disk to preserve original bytes.
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
        
    return {
        "filename": unique_filename,
        "content_type": file.content_type,
        "size": len(contents),
        "message": "Image uploaded successfully"
    }
