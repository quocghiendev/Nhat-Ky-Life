import base64
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx
from app.database import get_setting

logger = logging.getLogger(__name__)

TONE_PROMPTS = {
    "chan_that": "Văn phong chân thật, tự nhiên như lời tâm sự hằng ngày, mộc mạc và gần gũi.",
    "sau_sac": "Văn phong sâu sắc, giàu tính chiêm nghiệm, lắng đọng và tìm kiếm ý nghĩa trong từng chi tiết nhỏ.",
    "tho_mong": "Văn phong thơ mộng, lãng mạn, chú trọng miêu tả cảm xúc, ánh sáng, không gian và rung động tâm hồn.",
    "vui_ve": "Văn phong vui vẻ, dí dỏm, năng lượng tích cực, tươi sáng và tràn đầy sức sống.",
    "toi_gian": "Văn phong tối giản, súc tích, gãy gọn, ghi lại sự thật và cảm nhận cô đọng nhất."
}

def get_time_of_day_label(dt: datetime) -> str:
    hour = dt.hour
    if 5 <= hour < 11:
        return "Sáng"
    elif 11 <= hour < 14:
        return "Trưa"
    elif 14 <= hour < 18:
        return "Chiều"
    elif 18 <= hour < 22:
        return "Tối"
    else:
        return "Đêm"

async def process_multimodal_event(
    image_bytes: Optional[bytes] = None,
    image_mime: Optional[str] = None,
    audio_bytes: Optional[bytes] = None,
    audio_mime: Optional[str] = None,
    user_notes: Optional[str] = None,
    custom_tone: Optional[str] = None,
    current_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Core function that takes image, voice audio, and/or user notes,
    and returns a structured diary entry in Vietnamese.
    """
    if current_time is None:
        current_time = datetime.now()
        
    tone_key = custom_tone or get_setting("ai_tone", "chan_that")
    tone_instruction = TONE_PROMPTS.get(tone_key, TONE_PROMPTS["chan_that"])
    time_of_day = get_time_of_day_label(current_time)
    
    provider = get_setting("ai_provider", "gemini").lower()
    gemini_key = get_setting("gemini_api_key", "").strip()
    openai_key = get_setting("openai_api_key", "").strip()
    
    # Check if Gemini can be used
    if (provider == "gemini" and gemini_key) or (not openai_key and gemini_key):
        try:
            return await _call_gemini_multimodal(
                gemini_key=gemini_key,
                image_bytes=image_bytes,
                image_mime=image_mime,
                audio_bytes=audio_bytes,
                audio_mime=audio_mime,
                user_notes=user_notes,
                tone_instruction=tone_instruction,
                current_time=current_time,
                time_of_day=time_of_day
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            # If failed, fall back to mock or report error
            return _generate_smart_fallback(
                image_bytes=image_bytes,
                audio_bytes=audio_bytes,
                user_notes=user_notes,
                current_time=current_time,
                time_of_day=time_of_day,
                warning=f"Không thể kết nối Gemini API: {str(e)}"
            )

    # Check if OpenAI can be used
    if provider == "openai" and openai_key:
        try:
            return await _call_openai_multimodal(
                openai_key=openai_key,
                image_bytes=image_bytes,
                image_mime=image_mime,
                audio_bytes=audio_bytes,
                audio_mime=audio_mime,
                user_notes=user_notes,
                tone_instruction=tone_instruction,
                current_time=current_time,
                time_of_day=time_of_day
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return _generate_smart_fallback(
                image_bytes=image_bytes,
                audio_bytes=audio_bytes,
                user_notes=user_notes,
                current_time=current_time,
                time_of_day=time_of_day,
                warning=f"Không thể kết nối OpenAI API: {str(e)}"
            )

    # If no key is set yet, return an intelligent mock entry with helpful tip
    return _generate_smart_fallback(
        image_bytes=image_bytes,
        audio_bytes=audio_bytes,
        user_notes=user_notes,
        current_time=current_time,
        time_of_day=time_of_day,
        warning="Chưa cấu hình API Key trong Cài đặt (Đang dùng chế độ thử nghiệm nội bộ)."
    )

async def _call_gemini_multimodal(
    gemini_key: str,
    image_bytes: Optional[bytes],
    image_mime: Optional[str],
    audio_bytes: Optional[bytes],
    audio_mime: Optional[str],
    user_notes: Optional[str],
    tone_instruction: str,
    current_time: datetime,
    time_of_day: str
) -> Dict[str, Any]:
    model = get_setting("gemini_model", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    
    parts: List[Dict[str, Any]] = []
    
    prompt_text = f"""
Bạn là một trợ lý viết nhật ký cá nhân bằng tiếng Việt tinh tế và thấu hiểu.
Thời gian ghi nhận: {current_time.strftime('%H:%M, ngày %d/%m/%Y')} (Khoảng thời gian: Buổi {time_of_day}).
Yêu cầu văn phong: {tone_instruction}

Nhiệm vụ của bạn:
1. Nếu có tệp âm thanh đính kèm (giọng nói người dùng): Hãy nghe kỹ giọng nói, ghi lại nội dung lời nói (transcription) và cảm nhận cảm xúc trong giọng kể.
2. Nếu có tệp hình ảnh đính kèm (ảnh chụp camera/ảnh tải lên): Hãy quan sát khung cảnh, đối tượng, màu sắc, chi tiết nổi bật trong ảnh.
3. Nếu có ghi chú bằng chữ của người dùng: Hãy kết hợp thông điệp đó.
4. Tổng hợp tất cả các chi tiết từ âm thanh, hình ảnh và ghi chú thành 1 bài viết nhật ký hoàn chỉnh, chân thực, hấp dẫn theo dòng thời gian của ngày hôm nay.

BẮT BUỘC trả về đúng định dạng JSON chuẩn (không bọc trong markdown hoặc text thừa) với các trường sau:
{{
  "title": "Tiêu đề nhật ký ngắn gọn, ý nghĩa, gợi cảm xúc (khoảng 5-10 từ)",
  "transcription": "Gỡ băng nội dung giọng nói trong âm thanh (nếu không có âm thanh thì để chuỗi rỗng)",
  "image_description": "Mô tả ngắn gọn khung cảnh trong ảnh (nếu không có ảnh thì để chuỗi rỗng)",
  "content": "Nội dung nhật ký hoàn chỉnh bằng tiếng Việt (1 đến 3 đoạn văn tự nhiên, sâu sắc, kết hợp chi tiết từ ảnh và lời kể)",
  "mood": "Tâm trạng nổi bật nhất (ví dụ: Vui vẻ, Hạnh phúc, Bình yên, Chiêm nghiệm, Náo nhiệt, Bồi hồi...)",
  "mood_emoji": "1 emoji phù hợp nhất với tâm trạng (ví dụ: 😊, ☕, 🌿, 🌅, ✨, 🎉...)",
  "time_of_day": "{time_of_day}",
  "tags": ["tag1", "tag2", "tag3"]
}}
"""
    if user_notes:
        prompt_text += f"\nGhi chú bổ sung từ người dùng: {user_notes}\n"

    parts.append({"text": prompt_text})
    
    if image_bytes and image_mime:
        parts.append({
            "inline_data": {
                "mime_type": image_mime,
                "data": base64.b64encode(image_bytes).decode("utf-8")
            }
        })
        
    if audio_bytes and audio_mime:
        parts.append({
            "inline_data": {
                "mime_type": audio_mime,
                "data": base64.b64encode(audio_bytes).decode("utf-8")
            }
        })

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini không trả về kết quả.")
        
    text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    parsed = json.loads(text_content)
    parsed["ai_generated"] = 1
    return parsed

async def _call_openai_multimodal(
    openai_key: str,
    image_bytes: Optional[bytes],
    image_mime: Optional[str],
    audio_bytes: Optional[bytes],
    audio_mime: Optional[str],
    user_notes: Optional[str],
    tone_instruction: str,
    current_time: datetime,
    time_of_day: str
) -> Dict[str, Any]:
    transcript = ""
    # If audio is present, transcribe using OpenAI Whisper API
    if audio_bytes:
        ext = "webm"
        if audio_mime and "wav" in audio_mime:
            ext = "wav"
        elif audio_mime and "mp3" in audio_mime:
            ext = "mp3"
        elif audio_mime and "ogg" in audio_mime:
            ext = "ogg"
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                "file": (f"audio.{ext}", audio_bytes, audio_mime or "audio/webm"),
                "model": (None, "whisper-1"),
                "language": (None, "vi")
            }
            headers = {"Authorization": f"Bearer {openai_key}"}
            w_resp = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)
            if w_resp.status_code == 200:
                transcript = w_resp.json().get("text", "")

    # Now call GPT-4o for multimodal synthesis
    messages_content: List[Dict[str, Any]] = []
    
    prompt_text = f"""
Bạn là một trợ lý viết nhật ký cá nhân bằng tiếng Việt tinh tế.
Thời gian: {current_time.strftime('%H:%M, %d/%m/%Y')} (Buổi {time_of_day}).
Yêu cầu văn phong: {tone_instruction}

Dữ liệu đầu vào:
- Lời nói người dùng ghi âm lại: {transcript if transcript else "(Không có âm thanh)"}
- Ghi chú người dùng: {user_notes if user_notes else "(Không có)"}

Hãy phân tích hình ảnh đính kèm (nếu có) và kết hợp với lời nói + ghi chú để tạo 1 bài viết nhật ký hoàn chỉnh.
Trả về JSON chuẩn với các trường:
{{
  "title": "Tiêu đề nhật ký (5-10 từ)",
  "transcription": "{transcript}",
  "image_description": "Mô tả bức ảnh (nếu có)",
  "content": "Nội dung bài viết nhật ký giàu cảm xúc, kết hợp ảnh và lời kể",
  "mood": "Tâm trạng",
  "mood_emoji": "emoji",
  "time_of_day": "{time_of_day}",
  "tags": ["tag1", "tag2"]
}}
"""
    messages_content.append({"type": "text", "text": prompt_text})
    
    if image_bytes and image_mime:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        messages_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_mime};base64,{b64_img}"
            }
        })

    model = get_setting("openai_model", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": messages_content}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        data = resp.json()
        text_content = data["choices"][0]["message"]["content"]
        parsed = json.loads(text_content)
        if transcript and not parsed.get("transcription"):
            parsed["transcription"] = transcript
        parsed["ai_generated"] = 1
        return parsed

def _generate_smart_fallback(
    image_bytes: Optional[bytes],
    audio_bytes: Optional[bytes],
    user_notes: Optional[str],
    current_time: datetime,
    time_of_day: str,
    warning: str = ""
) -> Dict[str, Any]:
    """
    Intelligent simulated diary generator when API key is not yet set or network fails.
    """
    has_image = bool(image_bytes)
    has_audio = bool(audio_bytes)
    notes = (user_notes or "").strip()
    
    time_str = current_time.strftime("%H:%M")
    
    if has_image and has_audio:
        title = f"Khoảnh khắc ảnh & giọng nói lúc {time_str}"
        content = (
            f"Một khoảnh khắc được lưu lại vào buổi {time_of_day.lower()} lúc {time_str}. "
            f"Bức ảnh ghi lại không gian thực tế, cùng đoạn âm thanh lưu giữ trọn vẹn những suy nghĩ và cảm xúc ngay lúc đó. "
            + (f"Ghi chú: \"{notes}\". " if notes else "")
            + "Những mảnh ghép ký ức này giúp một ngày trôi qua thêm phần ý nghĩa và đáng nhớ."
        )
        mood = "Hứng khởi"
        mood_emoji = "✨"
        tags = ["khoanh-khac", "hinh-anh", "giong-noi", f"buoi-{time_of_day.lower()}"]
        img_desc = "Ảnh chụp sự kiện đời thực được ghi lại từ camera."
        transcript = notes or "Đoạn ghi âm giọng nói chân thực từ thiết bị."
    elif has_image:
        title = f"Khung cảnh buổi {time_of_day.lower()} lúc {time_str}"
        content = (
            f"Bức ảnh chụp lại khoảnh khắc đáng nhớ vào buổi {time_of_day.lower()}. "
            + (f"Đi kèm lời nhắn: \"{notes}\". " if notes else "")
            + "Có những khoảnh khắc chỉ cần một góc nhìn qua ống kính camera cũng đủ để lưu giữ tâm trạng của cả một ngày."
        )
        mood = "Bình yên"
        mood_emoji = "📸"
        tags = ["anh-chup", "ky-niem", f"buoi-{time_of_day.lower()}"]
        img_desc = "Bức ảnh được chụp trực tiếp từ camera hoặc tải lên."
        transcript = ""
    elif has_audio:
        title = f"Tâm sự bằng giọng nói buổi {time_of_day.lower()}"
        content = (
            f"Một đoạn voice ghi lại những dòng suy nghĩ lúc {time_str}. "
            + (f"Nội dung vắn tắt: \"{notes}\". " if notes else "")
            + "Ghi âm nhật ký bằng giọng nói giúp cảm xúc được giữ nguyên vẹn một cách chân thực nhất."
        )
        mood = "Chiêm nghiệm"
        mood_emoji = "🎙️"
        tags = ["ghi-am", "tam-su", f"buoi-{time_of_day.lower()}"]
        img_desc = ""
        transcript = notes or "Bản ghi âm giọng nói thời gian thực."
    else:
        title = notes[:30] if notes else f"Nhật ký buổi {time_of_day.lower()} lúc {time_str}"
        content = notes or f"Ghi chép nhanh khoảnh khắc trong ngày vào lúc {time_str}."
        mood = "Thư thái"
        mood_emoji = "🌿"
        tags = ["nhat-ky", f"buoi-{time_of_day.lower()}"]
        img_desc = ""
        transcript = ""

    return {
        "title": title,
        "transcription": transcript,
        "image_description": img_desc,
        "content": content,
        "mood": mood,
        "mood_emoji": mood_emoji,
        "time_of_day": time_of_day,
        "tags": tags,
        "ai_generated": 1,
        "note": warning
    }

async def generate_daily_summary(date_str: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesizes all entries of a single day into an overarching daily summary.
    """
    if not entries:
        return {
            "summary": "Ngày này chưa có mục nhật ký nào được ghi lại.",
            "mood_overview": "Chưa xác định",
            "highlights": "Không có sự kiện"
        }
        
    provider = get_setting("ai_provider", "gemini").lower()
    gemini_key = get_setting("gemini_api_key", "").strip()
    
    entries_text = "\n".join([
        f"- Lúc {e.get('entry_time', '')} ({e.get('time_of_day', '')}): Tiêu đề '{e.get('title', '')}', Tâm trạng {e.get('mood_emoji', '')} {e.get('mood', '')}, Nội dung: {e.get('content', '')[:200]}"
        for e in entries
    ])
    
    if gemini_key:
        try:
            model = get_setting("gemini_model", "gemini-2.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
            prompt = f"""
Bạn là người trợ lý viết nhật ký tổng kết ngày chuyên nghiệp.
Hôm nay là ngày: {date_str}.
Dưới đây là các sự kiện đã diễn ra trong ngày của người dùng:
{entries_text}

Hãy tổng kết lại toàn bộ ngày hôm nay thành 1 bài tổng kết ngắn gọn, sâu sắc và truyền cảm hứng.
Trả về JSON đúng cấu trúc sau:
{{
  "summary": "1-2 đoạn văn tổng kết ngày hôm nay một cách mạch lạc, nêu bật hành trình cảm xúc và những điều ý nghĩa đã diễn ra.",
  "mood_overview": "Tổng quan tâm trạng của ngày (ví dụ: Một ngày năng động và trọn vẹn niềm vui)",
  "highlights": "2-3 điểm nhấn đáng nhớ nhất trong ngày, cách nhau bằng dấu chấm phẩy"
}}
"""
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json", "temperature": 0.7}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
        except Exception as e:
            logger.error(f"Daily summary AI failed: {e}")

    # Fallback summary
    moods = [e.get("mood", "") for e in entries if e.get("mood")]
    unique_moods = list(dict.fromkeys(moods))
    titles = [e.get("title", "") for e in entries if e.get("title")]
    
    return {
        "summary": f"Ngày {date_str} có {len(entries)} khoảnh khắc được ghi lại. Từ những việc nhỏ đến những sự kiện nổi bật, tất cả tạo nên một ngày đa dạng và đầy màu sắc.",
        "mood_overview": f"Sắc thái cảm xúc: {', '.join(unique_moods) if unique_moods else 'Bình yên'}",
        "highlights": "; ".join(titles[:3]) if titles else "Các khoảnh khắc thường nhật"
    }
