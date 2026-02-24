import os
from groq import Groq
from moviepy.video.io.VideoFileClip import VideoFileClip
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_audio(video_path: str, audio_output: str = "meeting_audio.mp3") -> str:
    """Extract audio from video file."""
    print(f"🎬 Extracting audio from: {video_path}")
    
    # Check if file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    with VideoFileClip(video_path) as clip:
        # ✅ FIXED: Removed 'verbose' and 'logger' for MoviePy 2.0+ compatibility
        # If you want to see progress in the terminal now, MoviePy uses a different system,
        # but leaving it empty is the safest way to fix the crash.
        if clip.audio is not None:
            clip.audio.write_audiofile(audio_output)
        else:
            raise ValueError("The provided video file has no audio track.")
            
    print(f"✅ Audio saved to: {audio_output}")
    return audio_output

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Whisper Large V3 Turbo via Groq."""
    print(f"🎙️ Transcribing audio...")
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            language="en",
            temperature=0.0
        )
    print("✅ Transcription complete.")
    return transcription.text

def generate_summary(transcript_text: str) -> str:
    """Generate meeting summary using LLaMA 3.3 70B via Groq."""
    print("📝 Generating summary...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert meeting summarizer. "
                    "Summarize the following meeting transcript clearly and concisely. "
                    "Structure your response with these sections:\n\n"
                    "## 📌 Key Discussion Points\n"
                    "## ✅ Decisions Made\n"
                    "## 🎯 Action Items\n"
                    "## 📋 Overall Summary"
                )
            },
            {
                "role": "user",
                "content": transcript_text
            }
        ],
        temperature=0.5,
        max_tokens=1024
    )
    return response.choices[0].message.content

def process_meeting(source_path: str) -> dict:
    """
    Full pipeline: video/audio → transcript → summary.
    """
    video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    audio_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    ext = os.path.splitext(source_path)[1].lower()

    if ext in video_extensions:
        audio_path = extract_audio(source_path)
    elif ext in audio_extensions:
        audio_path = source_path
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    transcript = transcribe_audio(audio_path)
    summary = generate_summary(transcript)

    return {
        "transcript": transcript,
        "summary": summary
    }

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SOURCE_FILE = "meeting.mp4"

    if not os.path.exists(SOURCE_FILE):
        print(f"❌ File not found: {SOURCE_FILE}")
    else:
        try:
            result = process_meeting(SOURCE_FILE)
            print("\n" + "="*60)
            print("📄 TRANSCRIPT")
            print("="*60)
            print(result["transcript"])

            print("\n" + "="*60)
            print("📝 MEETING SUMMARY")
            print("="*60)
            print(result["summary"])

            with open("transcript.txt", "w", encoding="utf-8") as f:
                f.write(result["transcript"])
            with open("summary.txt", "w", encoding="utf-8") as f:
                f.write(result["summary"])
            print("\n✅ Saved transcript.txt and summary.txt")
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")