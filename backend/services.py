import os
import glob
import json
import uuid
import logging
import yt_dlp
import subprocess
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

JOBS_FILE = "jobs.json"

def load_jobs():
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_jobs():
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

jobs = load_jobs()

def check_ffmpeg():
    import shutil
    if not shutil.which("ffmpeg"):
        logger.error("FFmpeg not found! Please install FFmpeg and add it to your PATH.")

def process_video(job_id: str, url: str):
    try:
        jobs[job_id]["status"] = "downloading"
        save_jobs()
        
        # 1. Download Audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_DIR}/{job_id}.%(ext)s',
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        audio_path = f"{DOWNLOAD_DIR}/{job_id}.mp3"
        
        # 2. Split Audio (if necessary)
        jobs[job_id]["status"] = "splitting"
        save_jobs()
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        chunk_files = []
        
        if file_size > 24 * 1024 * 1024:  # > 24MB
            # Use ffmpeg to split directly
            chunk_pattern = f"{DOWNLOAD_DIR}/{job_id}_part%03d.mp3"
            try:
                subprocess.run([
                    "ffmpeg", "-i", audio_path,
                    "-f", "segment",
                    "-segment_time", "600", # 10 minutes
                    "-c", "copy",
                    chunk_pattern
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                chunk_files = sorted(glob.glob(f"{DOWNLOAD_DIR}/{job_id}_part*.mp3"))
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg split failed: {e}")
                raise e
        else:
            chunk_files.append(audio_path)
            
        # 3. Transcribe
        jobs[job_id]["status"] = "transcribing"
        save_jobs()
        full_transcript = ""
        
        for chunk_file in chunk_files:
            with open(chunk_file, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(chunk_file, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0
                )
                full_transcript += transcription.text + " "
        
        # Cleanup
        try:
            os.remove(audio_path)
            for f in chunk_files:
                if f != audio_path:
                    os.remove(f)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["transcript"] = full_transcript.strip()
        jobs[job_id]["title"] = url # Placeholder title
        save_jobs()
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        save_jobs()

def process_upload(job_id: str, file_path: str, original_filename: str):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["title"] = original_filename
        save_jobs()
        
        audio_path = file_path
        
        # 2. Split Audio (if necessary)
        jobs[job_id]["status"] = "splitting"
        save_jobs()
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        chunk_files = []
        
        if file_size > 24 * 1024 * 1024:  # > 24MB
            # Use ffmpeg to split directly
            chunk_pattern = f"{DOWNLOAD_DIR}/{job_id}_part%03d.mp3"
            try:
                subprocess.run([
                    "ffmpeg", "-i", audio_path,
                    "-f", "segment",
                    "-segment_time", "600", # 10 minutes
                    "-c", "copy",
                    chunk_pattern
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                chunk_files = sorted(glob.glob(f"{DOWNLOAD_DIR}/{job_id}_part*.mp3"))
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg split failed: {e}")
                raise e
        else:
            chunk_files.append(audio_path)
            
        # 3. Transcribe
        jobs[job_id]["status"] = "transcribing"
        save_jobs()
        full_transcript = ""
        
        for chunk_file in chunk_files:
            with open(chunk_file, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(chunk_file, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0
                )
                full_transcript += transcription.text + " "
        
        # Cleanup
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            for f in chunk_files:
                if f != audio_path and os.path.exists(f):
                    os.remove(f)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["transcript"] = full_transcript.strip()
        save_jobs()
        
    except Exception as e:
        logger.error(f"Upload job failed: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        save_jobs()

def ask_question(transcript: str, question: str):
    try:
        logger.info(f"Asking question: {question}")
        # Truncate transcript to avoid context window limits (approx 6k tokens)
        max_chars = 15000 # Reduced to 15k to be safe
        if len(transcript) > max_chars:
            logger.warning("Transcript too long, truncating...")
            truncated_transcript = transcript[:max_chars] + "...[TRUNCATED]"
        else:
            truncated_transcript = transcript

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer the user's question based ONLY on the provided video transcript. If the answer is not in the transcript, say so."
                },
                {
                    "role": "user",
                    "content": f"Transcript: {truncated_transcript}\n\nQuestion: {question}"
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return f"Error: {str(e)}"
