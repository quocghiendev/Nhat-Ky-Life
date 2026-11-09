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
    model = get_setting("gemini_model", "gemini-3.8-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    
    parts: List[Dict[str, Any]] = []
    
    is_past = current_time.date() < datetime.now().date()
    event_date_str = current_time.strftime("%d/%m/%Y")
    event_time_str = current_time.strftime("%H:%M")
    
    if is_past:
        time_context = f"Sự kiện này đã diễn ra trong QUÁ KHỨ (vào ngày {event_date_str} lúc {event_time_str}, buổi {time_of_day}). Hãy viết nhật ký với tâm thế hồi tưởng, hoài niệm, trân trọng một kỷ niệm hoặc khoảnh khắc đã trải qua."
    else:
        time_context = f"Sự kiện này diễn ra vào HÔM NAY (lúc {event_time_str}, buổi {time_of_day}). Hãy viết nhật ký với cảm xúc thời gian thực tươi mới của ngày hôm nay."

    prompt_text = f"""
Bạn là một trợ lý viết nhật ký cá nhân bằng tiếng Việt tinh tế và thấu hiểu.
Nhiệm vụ của bạn: VIẾT NHẬT KÝ HỘ người dùng dựa trên các tệp hình ảnh, âm thanh và ghi chú bổ sung.

THÔNG TIN THỜI ĐIỂM:
- Thời gian sự kiện: Buổi {time_of_day}, lúc {event_time_str} ngày {event_date_str}.
- Ngữ cảnh: {time_context}
- Yêu cầu văn phong: {tone_instruction}

CÁC QUY TẮC PHÂN TÍCH VÀ BIÊN SOẠN BẮT BUỘC TUÂN THỦ:
1. PHÂN TÍCH GIỌNG NÓI & HÌNH ẢNH:
   - Nếu có tệp âm thanh (giọng nói): Lắng nghe kỹ lời kể, sắc thái cảm xúc để hiểu trọn vẹn điều người dùng muốn bày tỏ.
   - Nếu có tệp hình ảnh: Quan sát chi tiết khung cảnh, ánh sáng, con người, sự vật để cảm nhận không gian của sự kiện.
   - Viết caption / nội dung nhật ký tương thích và phản ánh chính xác những gì nhìn thấy trong ảnh hoặc nghe thấy trong âm thanh.

2. VAI TRÒ CỦA GHI CHÚ NHANH (USER NOTES):
   - "Ghi chú nhanh" là phần BỔ SUNG CỰC KỲ QUAN TRỌNG từ người dùng để bạn hiểu rõ hơn bối cảnh và tâm tư đằng sau ảnh/voice. Hãy lồng ghép thông điệp ghi chú này để viết nhật ký hộ một cách tự nhiên và chân thật nhất.

3. QUY TẮC XỬ LÝ KHI THIẾU DỮ LIỆU:
   - NẾU tệp âm thanh hoặc hình ảnh không có gì, bị mờ/nhiễu hoặc AI không hiểu được: HÃY DỰA HOÀN TOÀN VÀO GHI CHÚ NHANH CỦA NGƯỜI DÙNG để viết một bài nhật ký ý nghĩa và đầy đủ.
   - NẾU cả âm thanh, hình ảnh đều không rõ VÀ người dùng CŨNG KHÔNG ĐỂ LẠI GHI CHÚ (hoặc chỉ có ảnh/voice tĩnh mà không có lời): HÃY VIẾT MỘT CAPTION/NHẬT KÝ "VU VƠ" NHƯNG TINH TẾ, nhấn mạnh vào khoảng không gian, âm thanh và hình ảnh để người đọc hiểu được rằng người dùng ĐÃ CÓ MỘT SỰ KIỆN / KHOẢNH KHẮC ĐỜI THỰC ĐÁNG NHỚ diễn ra vào khoảng thời gian đó.

BẮT BUỘC trả về đúng định dạng JSON chuẩn (không bọc trong markdown hoặc text thừa) với các trường sau:
{{
  "title": "Tiêu đề nhật ký ngắn gọn, ý nghĩa, gợi cảm xúc (khoảng 5-10 từ)",
  "transcription": "Gỡ băng nội dung giọng nói trong âm thanh (nếu không có âm thanh hoặc không rõ thì để chuỗi rỗng)",
  "image_description": "Mô tả ngắn gọn khung cảnh trong ảnh (nếu không có ảnh thì để chuỗi rỗng)",
  "content": "Nội dung nhật ký hoàn chỉnh bằng tiếng Việt (1 đến 3 đoạn văn sâu sắc, tự nhiên, viết hộ người dùng theo đúng các quy tắc trên)",
  "mood": "Tâm trạng nổi bật nhất (ví dụ: Vui vẻ, Hạnh phúc, Bình yên, Chiêm nghiệm, Náo nhiệt, Hoài niệm...)",
  "mood_emoji": "1 emoji phù hợp nhất với tâm trạng (ví dụ: 😊, ☕, 🌿, 🌅, ✨, 🎉, 🍃...)",
  "time_of_day": "{time_of_day}",
  "tags": ["tag1", "tag2", "tag3"]
}}
"""
    if user_notes:
        prompt_text += f"\nGhi chú bổ sung từ người dùng (rất quan trọng): {user_notes}\n"

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
    
    is_past = current_time.date() < datetime.now().date()
    event_date_str = current_time.strftime("%d/%m/%Y")
    event_time_str = current_time.strftime("%H:%M")
    
    if is_past:
        time_context = f"Sự kiện này đã diễn ra trong QUÁ KHỨ (ngày {event_date_str} lúc {event_time_str}, buổi {time_of_day}). Hãy viết nhật ký theo góc nhìn hồi tưởng, hoài niệm, trân trọng một kỷ niệm đã qua."
    else:
        time_context = f"Sự kiện này diễn ra vào HÔM NAY (lúc {event_time_str}, buổi {time_of_day}). Hãy viết nhật ký với cảm xúc tươi mới của ngày hôm nay."

    prompt_text = f"""
Bạn là một trợ lý viết nhật ký cá nhân bằng tiếng Việt tinh tế và thấu hiểu.
Nhiệm vụ: VIẾT NHẬT KÝ HỘ người dùng dựa trên hình ảnh, âm thanh và ghi chú bổ sung.

THÔNG TIN THỜI ĐIỂM:
- Thời gian: Buổi {time_of_day}, lúc {event_time_str} ngày {event_date_str}.
- Ngữ cảnh: {time_context}
- Yêu cầu văn phong: {tone_instruction}

QUY TẮC BẮT BUỘC:
1. Đọc và phân tích kỹ hình ảnh và lời nói ({transcript if transcript else 'không có âm thanh'}). Viết caption/comment nhật ký tương thích và phản ánh đúng những gì nhìn thấy trong ảnh hoặc nghe thấy trong âm thanh.
2. GHI CHÚ NHANH TỪ NGƯỜI DÙNG: {user_notes if user_notes else '(Không có)'}. Đây là phần BỔ SUNG QUAN TRỌNG để AI hiểu trọn vẹn ngữ cảnh và viết nhật ký hộ.
3. NẾU tệp âm thanh hoặc hình ảnh không có gì hoặc không hiểu được: Hãy dựa hoàn toàn vào ghi chú nhanh của người dùng để viết nhật ký.
4. NẾU cả âm thanh, hình ảnh đều không rõ VÀ không có ghi chú: Hãy viết một CAPTION/NHẬT KÝ "VU VƠ" NHƯNG TINH TẾ, nhấn mạnh vào khung cảnh âm thanh và hình ảnh để người đọc hiểu được rằng người dùng ĐÃ CÓ MỘT SỰ KIỆN / KHOẢNH KHẮC ĐỜI THỰC ĐÁNG NHỚ diễn ra vào khoảng thời gian đó.

Trả về JSON chuẩn:
{{
  "title": "Tiêu đề nhật ký (5-10 từ gợi cảm xúc)",
  "transcription": "{transcript}",
  "image_description": "Mô tả bức ảnh (nếu có)",
  "content": "Nội dung bài viết nhật ký hoàn chỉnh (1 đến 3 đoạn văn sâu sắc, tự nhiên, viết hộ người dùng theo đúng các quy tắc trên)",
  "mood": "Tâm trạng",
  "mood_emoji": "emoji phù hợp",
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
    Intelligent simulated diary generator following exact user instructions:
    - Base on notes if audio/image is missing or unclear.
    - If no notes, write whimsical evocative caption emphasizing moment occurred at that time.
    - Adapt tone for past or present events.
    """
    has_image = bool(image_bytes)
    has_audio = bool(audio_bytes)
    notes = (user_notes or "").strip()
    
    is_past = current_time.date() < datetime.now().date()
    date_str = current_time.strftime("%d/%m/%Y")
    time_str = current_time.strftime("%H:%M")
    
    past_prefix = f"Nhìn lại ngày {date_str}, " if is_past else ""
    
    # CASE 1: User provided notes (Ghi chú nhanh là phần bổ sung quan trọng để AI viết hộ)
    if notes:
        title = notes[:35] if len(notes) <= 35 else (notes[:32] + "...")
        if has_image and has_audio:
            content = (
                f"{past_prefix}một khoảnh khắc đáng nhớ vào buổi {time_of_day.lower()} lúc {time_str}. "
                f"Hình ảnh và giọng nói đã ghi lại trọn vẹn không gian thực tế, hòa cùng những dòng tâm sự: \"{notes}\". "
                "Từng chi tiết nhỏ nhặt nhất trong ngày bỗng trở nên thật sống động và ý nghĩa khi được lưu giữ lại như thế này."
            )
            mood = "Hứng khởi"
            mood_emoji = "✨"
        elif has_image:
            content = (
                f"{past_prefix}bức ảnh chụp lại khoảnh khắc đáng nhớ vào buổi {time_of_day.lower()} lúc {time_str}. "
                f"Đi cùng lời nhắn gửi: \"{notes}\". "
                "Khung cảnh qua ống kính kết hợp với dòng cảm nghĩ đã tạo nên một trang nhật ký chân thật, vẹn nguyên cảm xúc."
            )
            mood = "Bình yên"
            mood_emoji = "📸"
        elif has_audio:
            content = (
                f"{past_prefix}một đoạn voice chia sẻ lúc {time_str}. "
                f"Những điều được gửi gắm: \"{notes}\". "
                "Thanh âm chân thực kết hợp cùng dòng suy nghĩ này đã giúp lưu lại trọn vẹn tâm trạng của thời điểm ấy."
            )
            mood = "Chiêm nghiệm"
            mood_emoji = "🎙️"
        else:
            content = (
                f"{past_prefix}ghi chép nhanh vào buổi {time_of_day.lower()} lúc {time_str}: \"{notes}\". "
                "Dù chỉ là đôi dòng ngắn ngủi, đây vẫn là một mảnh ghép quý giá đánh dấu một sự kiện trong hành trình của mình."
            )
            mood = "Bình yên"
            mood_emoji = "🌿"
            
        tags = ["nhat-ky", f"buoi-{time_of_day.lower()}", "ky-niem"]
        img_desc = "Ảnh sự kiện thực tế được ghi lại." if has_image else ""
        transcript = notes if has_audio else ""

    # CASE 2: No notes provided -> Write a whimsical, evocative caption emphasizing sound & image
    else:
        title = f"Một thoáng {time_of_day.lower()} vu vơ lúc {time_str}"
        if has_image and has_audio:
            content = (
                f"{past_prefix}một khoảng lặng đọng lại lúc {time_str} buổi {time_of_day.lower()}. "
                "Khung hình và thanh âm đã thay lời muốn nói, đánh dấu một sự kiện tĩnh lặng nhưng đáng nhớ trong đời sống thường nhật. "
                "Có những khoảnh khắc trôi qua không cần quá nhiều lời lẽ, chỉ cần một góc nhìn và một nhịp thở của thời gian cũng đủ để biết mình đã hiện diện trọn vẹn ở nơi đó."
            )
            mood = "Lắng đọng"
            mood_emoji = "🍃"
            tags = ["khoanh-khac", "hinh-anh", "giong-noi", f"buoi-{time_of_day.lower()}"]
            img_desc = "Ảnh chụp sự kiện đời thực được ghi lại từ camera."
            transcript = "Âm thanh nền và thanh âm tự nhiên của khoảnh khắc."
        elif has_image:
            content = (
                f"{past_prefix}một góc nhìn bình yên được ghi lại qua ống kính vào buổi {time_of_day.lower()} lúc {time_str}. "
                "Bức ảnh thay cho mọi lời kể vu vơ, nhấn mạnh rằng đã có một sự kiện thực tế diễn ra vào đúng khoảnh khắc này, "
                "lặng lẽ ghi dấu một nét vẽ đẹp vào cuốn nhật ký thời gian."
            )
            mood = "Chiêm nghiệm"
            mood_emoji = "📸"
            tags = ["anh-chup", "khoanh-khac", f"buoi-{time_of_day.lower()}"]
            img_desc = "Bức ảnh chụp lại không gian thực tế."
            transcript = ""
        elif has_audio:
            content = (
                f"{past_prefix}một đoạn âm thanh lưu giữ thanh âm xung quanh vào buổi {time_of_day.lower()} lúc {time_str}. "
                "Tiếng vọng của khoảnh khắc ấy như một lời nhắc nhở vu vơ nhưng đầy chất thơ rằng mình đã trải qua một sự kiện có thật, "
                "mộc mạc và chân thành."
            )
            mood = "Lắng đọng"
            mood_emoji = "🎙️"
            tags = ["ghi-am", "thanh-am", f"buoi-{time_of_day.lower()}"]
            img_desc = ""
            transcript = "Thanh âm mộc mạc của sự kiện đời thực."
        else:
            content = (
                f"{past_prefix}khoảnh khắc đánh dấu một sự kiện diễn ra vào buổi {time_of_day.lower()} lúc {time_str}. "
                "Những dấu mốc thời gian giản dị nhưng luôn nhắc nhở về từng bước đi qua mỗi ngày."
            )
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
            model = get_setting("gemini_model", "gemini-3.8-flash")
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
