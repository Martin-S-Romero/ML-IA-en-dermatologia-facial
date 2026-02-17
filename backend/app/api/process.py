import os
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app import models
from app.core.face_censor import FaceCensor

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
PROCESSED_DIR = "/app/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

@router.post("/{filename}")
async def process_image(
    filename: str,
    mode: str = "blur",
    expand: int = 10,
    blur_strength: int = 55,
    pixel_size: int = 10,
    cut: bool = False,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Process an uploaded image with face censorship.
    
    Parameters:
    - filename: Name of the uploaded file (from /upload endpoint)
    - mode: Censorship mode ("blur", "black", "pixelate")
    - expand: Expansion of censored area (pixels)
    - blur_strength: Blur intensity (odd number, for blur mode)
    - pixel_size: Pixel size (for pixelate mode)
    - cut: Crop to face area
    """
    
    # Validate mode
    if mode not in ["blur", "black", "pixelate"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Must be 'blur', 'black', or 'pixelate'"
        )
    
    # Check if uploaded file exists
    input_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(input_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' not found. Please upload it first."
        )
    
    # Generate unique output filename
    file_ext = os.path.splitext(filename)[1] or ".jpg"
    output_filename = f"{uuid.uuid4()}_censored{file_ext}"
    output_path = os.path.join(PROCESSED_DIR, output_filename)
    
    # Initialize FaceCensor
    censor = FaceCensor(
        mode=mode,
        blur_strength=blur_strength,
        expand=expand,
        pixel_size=pixel_size,
        cut=cut
    )
    
    # Process image
    try:
        result = censor.process_image(input_path, output_path)
        
        if result is None:
            # Save failed record
            db_record = models.ProcessedImage(
                user_id=current_user.id,
                original_filename=filename,
                processed_filename="",
                mode=mode,
                parameters=json.dumps({
                    "expand": expand,
                    "blur_strength": blur_strength,
                    "pixel_size": pixel_size,
                    "cut": cut
                }),
                status="failed"
            )
            db.add(db_record)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process image. Resolution may be too low (min 1280x720) or no face detected."
            )
        
        # Save successful record to database
        db_record = models.ProcessedImage(
            user_id=current_user.id,
            original_filename=filename,
            processed_filename=output_filename,
            mode=mode,
            parameters=json.dumps({
                "expand": expand,
                "blur_strength": blur_strength,
                "pixel_size": pixel_size,
                "cut": cut
            }),
            status="completed"
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Return processed image
        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename=output_filename,
            headers={
                "X-Process-ID": str(db_record.id),
                "X-Mode": mode
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing image: {str(e)}"
        )
