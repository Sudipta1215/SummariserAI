from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.youtube_service import extract_transcript_details, generate_gemini_content

# ✅ Prefix removed here because it is already defined in main.py
router = APIRouter(tags=["YouTube Summary"])

class VideoRequest(BaseModel):
    url: str

@router.post("/summarize")
async def summarize_video(request: VideoRequest):
    try:
        transcript, video_id = extract_transcript_details(request.url)
        summary = generate_gemini_content(transcript)
        return {
            "video_id": video_id,
            "summary": summary,
            "thumbnail": f"http://img.youtube.com/vi/{video_id}/0.jpg"
        }
    except Exception as e:
        # It's better to log the actual error for debugging
        print(f"Error in summarize_video: {e}")
        raise HTTPException(status_code=400, detail=str(e))