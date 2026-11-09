import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from app.config import IMAGES_DIR, AUDIO_DIR

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
ALLOWED_AUDIO_EXTENSIONS = {".webm", ".wav", ".mp3", ".ogg", ".m4a", ".mp4", ".aac"}

async def save_uploaded_image(file: UploadFile) -> str:
    """
    Saves an uploaded image to IMAGES_DIR and returns its public URL path.
    """
    ext = Path(file.filename or "image.jpg").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = ".jpg"
        
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"img_{date_str}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = IMAGES_DIR / filename
    
    async with aiofiles.open(dest_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)
            
    return f"/uploads/images/{filename}"

async def save_uploaded_audio(file: UploadFile) -> str:
    """
    Saves an uploaded or recorded voice file to AUDIO_DIR and returns its public URL path.
    """
    ext = Path(file.filename or "voice.webm").suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        ext = ".webm"
        
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"voice_{date_str}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = AUDIO_DIR / filename
    
    async with aiofiles.open(dest_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)
            
    return f"/uploads/audio/{filename}"

def get_file_bytes_and_mime(relative_path: str):
    """
    Given a URL path like /uploads/images/abc.jpg or /uploads/audio/xyz.webm,
    returns (file_bytes, mime_type) for sending to multimodal AI.
    """
    from app.config import DATA_DIR
    clean_path = relative_path.lstrip("/")
    if clean_path.startswith("uploads/"):
        file_path = DATA_DIR / clean_path
    else:
        file_path = DATA_DIR / "uploads" / clean_path
        
    if not file_path.exists():
        return None, None
        
    ext = file_path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".webm": "audio/webm",
        ".wav": "audio/wav",
        ".mp3": "audio/mp3",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4"
    }
    mime = mime_types.get(ext, "application/octet-stream")
    with open(file_path, "rb") as f:
        data = f.read()
    return data, mime
