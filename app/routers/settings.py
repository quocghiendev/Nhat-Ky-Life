from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import httpx
from app.database import get_all_settings, set_multiple_settings, set_setting, get_setting

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    ai_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    ai_tone: Optional[str] = None
    auto_fill_daily: Optional[str] = None

class TestKeyRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None

@router.get("")
def get_settings():
    all_settings = get_all_settings()
    gemini_key = all_settings.get("gemini_api_key", "").strip()
    openai_key = all_settings.get("openai_api_key", "").strip()
    
    # Obscure keys for safety in UI
    def mask_key(k: str) -> str:
        if not k:
            return ""
        if len(k) <= 8:
            return "••••••••"
        return k[:4] + "••••••••" + k[-4:]

    return {
        "ai_provider": all_settings.get("ai_provider", "gemini"),
        "gemini_model": all_settings.get("gemini_model", "gemini-3.8-flash"),
        "gemini_api_key_masked": mask_key(gemini_key),
        "has_gemini_key": bool(gemini_key),
        "openai_model": all_settings.get("openai_model", "gpt-4o-mini"),
        "openai_api_key_masked": mask_key(openai_key),
        "has_openai_key": bool(openai_key),
        "ai_tone": all_settings.get("ai_tone", "chan_that"),
        "auto_fill_daily": all_settings.get("auto_fill_daily", "1")
    }

@router.post("")
def update_settings(payload: SettingsUpdate):
    updates = {}
    if payload.ai_provider is not None:
        updates["ai_provider"] = payload.ai_provider
    if payload.gemini_model is not None:
        updates["gemini_model"] = payload.gemini_model
    if payload.gemini_api_key is not None and payload.gemini_api_key != "":
        # Only update if not blank
        updates["gemini_api_key"] = payload.gemini_api_key.strip()
    if payload.openai_model is not None:
        updates["openai_model"] = payload.openai_model
    if payload.openai_api_key is not None and payload.openai_api_key != "":
        updates["openai_api_key"] = payload.openai_api_key.strip()
    if payload.ai_tone is not None:
        updates["ai_tone"] = payload.ai_tone
    if payload.auto_fill_daily is not None:
        updates["auto_fill_daily"] = payload.auto_fill_daily

    if updates:
        set_multiple_settings(updates)
        
    return {"success": True, "message": "Đã lưu cài đặt thành công."}

@router.post("/test-key")
async def test_key(req: TestKeyRequest):
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API Key không được để trống.")
        
    if req.provider.lower() == "gemini":
        model = req.model or "gemini-3.8-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": "Xin chào! Trả lời đúng 1 từ: OK"}]}]
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    return {"valid": True, "message": "Kết nối Gemini API thành công!"}
                else:
                    return {"valid": False, "message": f"Lỗi Gemini: HTTP {resp.status_code} - {resp.text[:200]}"}
        except Exception as e:
            return {"valid": False, "message": f"Không thể kết nối: {str(e)}"}
            
    elif req.provider.lower() == "openai":
        url = "https://api.openai.com/v1/models"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers={"Authorization": f"Bearer {key}"})
                if resp.status_code == 200:
                    return {"valid": True, "message": "Kết nối OpenAI API thành công!"}
                else:
                    return {"valid": False, "message": f"Lỗi OpenAI: HTTP {resp.status_code} - {resp.text[:200]}"}
        except Exception as e:
            return {"valid": False, "message": f"Không thể kết nối: {str(e)}"}
            
    raise HTTPException(status_code=400, detail="Nhà cung cấp không được hỗ trợ.")
