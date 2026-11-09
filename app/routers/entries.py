from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.database import (
    create_entry, get_entry, get_entries, update_entry, 
    delete_entry, toggle_favorite, get_entry_dates, get_stats
)
from app.utils.file_storage import save_uploaded_image, save_uploaded_audio

router = APIRouter(prefix="/api/entries", tags=["entries"])

class EntryCreate(BaseModel):
    title: str
    content: str
    entry_date: Optional[str] = None
    entry_time: Optional[str] = None
    raw_transcript: Optional[str] = ""
    image_description: Optional[str] = ""
    image_path: Optional[str] = ""
    audio_path: Optional[str] = ""
    mood: Optional[str] = "Bình yên"
    mood_emoji: Optional[str] = "🌿"
    tags: Optional[str] = ""
    time_of_day: Optional[str] = "Ngày"
    is_favorite: Optional[bool] = False
    ai_generated: Optional[bool] = False

class EntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    entry_date: Optional[str] = None
    entry_time: Optional[str] = None
    raw_transcript: Optional[str] = None
    image_description: Optional[str] = None
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    mood: Optional[str] = None
    mood_emoji: Optional[str] = None
    tags: Optional[str] = None
    time_of_day: Optional[str] = None
    is_favorite: Optional[bool] = None

@router.get("")
def list_entries(
    date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    entries = get_entries(date=date, keyword=keyword, limit=limit, offset=offset)
    return {"entries": entries, "count": len(entries)}

@router.get("/dates")
def list_dates():
    return {"dates": get_entry_dates()}

@router.get("/stats")
def app_stats():
    return get_stats()

@router.get("/{entry_id}")
def retrieve_entry(entry_id: int):
    entry = get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục nhật ký này.")
    return entry

@router.post("")
def add_entry(entry: EntryCreate):
    entry_id = create_entry(entry.model_dump())
    created = get_entry(entry_id)
    return created

@router.put("/{entry_id}")
def modify_entry(entry_id: int, entry: EntryUpdate):
    data = {k: v for k, v in entry.model_dump().items() if v is not None}
    success = update_entry(entry_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Cập nhật thất bại hoặc không tìm thấy mục.")
    return get_entry(entry_id)

@router.delete("/{entry_id}")
def remove_entry(entry_id: int):
    success = delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục để xóa.")
    return {"success": True, "message": "Đã xóa mục nhật ký thành công."}

@router.post("/{entry_id}/toggle-favorite")
def favorite_entry(entry_id: int):
    new_status = toggle_favorite(entry_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục.")
    return {"is_favorite": new_status}

@router.post("/upload/image")
async def upload_image_file(file: UploadFile = File(...)):
    url = await save_uploaded_image(file)
    return {"url": url}

@router.post("/upload/audio")
async def upload_audio_file(file: UploadFile = File(...)):
    url = await save_uploaded_audio(file)
    return {"url": url}
