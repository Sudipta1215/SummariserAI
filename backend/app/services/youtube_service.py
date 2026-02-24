import os
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """


def extract_video_id(youtube_url):
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0].split("?")[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    else:
        return youtube_url.split("/")[-1].split("?")[0].split("=")[-1]


def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        transcript = " ".join([snippet.text for snippet in fetched])
        return transcript, video_id
    except Exception as e:
        raise Exception(f"Could not retrieve transcript: {str(e)}")


# ✅ Keep old name so youtube.py router import doesn't break
def generate_gemini_content(transcript_text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": PROMPT + transcript_text}
        ]
    )
    return response.choices[0].message.content

