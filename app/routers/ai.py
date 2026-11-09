from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.utils.file_storage import save_uploaded_image, save_uploaded_audio
from app.ai_service import process_multimodal_event, generate_daily_summary
from app.database import (
    create_entry, get_entry, get_entries, 
    get_daily_summary, save_daily_summary
)

router = APIRouter(prefix="/api/ai", tags=["ai"])

class DailySummaryRequest(BaseModel):
    date: str

@router.post("/process-event")
async def process_event(
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    notes: Optional[str] = Form(""),
    tone: Optional[str] = Form(None),
    auto_save: Optional[bool] = Form(True),
    entry_date: Optional[str] = Form(None),
    entry_time: Optional[str] = Form(None)
):
    """
    Receives camera image/photo, voice recording/audio, and optional user notes.
    Uses AI to understand audio and image, generate a structured journal entry,
    and optionally auto-save directly to today's diary.
    """
    now = datetime.now()
    cur_date = entry_date or now.strftime("%Y-%m-%d")
    cur_time = entry_time or now.strftime("%H:%M:%S")

    image_path = ""
    image_bytes = None
    image_mime = None
    if image and image.filename:
        image_bytes = await image.read()
        await image.seek(0)
        image_path = await save_uploaded_image(image)
        image_mime = image.content_type or "image/jpeg"

    audio_path = ""
    audio_bytes = None
    audio_mime = None
    if audio and audio.filename:
        audio_bytes = await audio.read()
        await audio.seek(0)
        audio_path = await save_uploaded_audio(audio)
        audio_mime = audio.content_type or "audio/webm"

    # Must provide at least one input (image, audio, or notes)
    if not image_bytes and not audio_bytes and not (notes and notes.strip()):
        raise HTTPException(
            status_code=400,
            detail="Vui lòng cung cấp ít nhất một nội dung: hình ảnh, đoạn ghi âm, hoặc ghi chú chữ."
        )

    # Process with Multimodal AI
    ai_result = await process_multimodal_event(
        image_bytes=image_bytes,
        image_mime=image_mime,
        audio_bytes=audio_bytes,
        audio_mime=audio_mime,
        user_notes=notes,
        custom_tone=tone,
        current_time=now
    )

    tags = ai_result.get("tags", [])
    if isinstance(tags, list):
        tags_str = ",".join(tags)
    else:
        tags_str = str(tags)

    saved_entry = None
    if auto_save:
        entry_payload = {
            "entry_date": cur_date,
            "entry_time": cur_time,
            "title": ai_result.get("title", "Khoảnh khắc trong ngày"),
            "content": ai_result.get("content", ""),
            "raw_transcript": ai_result.get("transcription", ""),
            "image_description": ai_result.get("image_description", ""),
            "image_path": image_path,
            "audio_path": audio_path,
            "mood": ai_result.get("mood", "Bình yên"),
            "mood_emoji": ai_result.get("mood_emoji", "🌿"),
            "tags": tags_str,
            "time_of_day": ai_result.get("time_of_day", "Ngày"),
            "is_favorite": 0,
            "ai_generated": 1
        }
        entry_id = create_entry(entry_payload)
        saved_entry = get_entry(entry_id)

    return {
        "success": True,
        "auto_saved": bool(auto_save),
        "entry": saved_entry,
        "ai_result": ai_result,
        "image_path": image_path,
        "audio_path": audio_path
    }

@router.post("/daily-summary")
async def create_daily_summary(req: DailySummaryRequest):
    entries = get_entries(date=req.date, limit=100)
    summary_data = await generate_daily_summary(req.date, entries)
    
    save_daily_summary(
        date=req.date,
        summary=summary_data.get("summary", ""),
        mood_overview=summary_data.get("mood_overview", ""),
        highlights=summary_data.get("highlights", "")
    )
    
    return {
        "date": req.date,
        "summary": summary_data.get("summary", ""),
        "mood_overview": summary_data.get("mood_overview", ""),
        "highlights": summary_data.get("highlights", ""),
        "entry_count": len(entries)
    }

@router.get("/daily-summary/{date}")
def fetch_daily_summary(date: str):
    summary = get_daily_summary(date)
    return {"date": date, "summary": summary}
