import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.meeting_service import process_meeting

router = APIRouter(tags=["Meeting Summarizer"])

# Ensure an uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process-meeting")
async def summarize_meeting(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Run the meeting processing pipeline
        result = process_meeting(file_path)
        
        return {
            "filename": file.filename,
            "transcript": result["transcript"],
            "summary": result["summary"]
        }
    
    except Exception as e:
        print(f"Error processing meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 3. Clean up the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)