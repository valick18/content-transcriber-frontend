# YouTube Transcriber & Chat App

A mobile-first web application to download, transcribe, and chat with YouTube videos using Groq API.

## Features
- **Download & Transcribe**: Paste a YouTube link to get a full transcript.
- **Chat with Video**: Ask questions about the video content using Llama3 via Groq.
- **Mobile-First Design**: Optimized for mobile devices (PWA-ready).
- **Dark Mode**: Premium dark aesthetic.

## Project Structure
- `backend/`: FastAPI Python server (handles downloading, splitting, transcribing).
- `frontend/`: React Vite application (UI).

## Prerequisites
- **Docker**: For containerization and deployment.
- **Node.js**: For frontend development.
- **Groq API Key**: Required for transcription and chat.

## Local Development

### Backend
1.  Navigate to `backend/`.
2.  Create a `.env` file with your Groq API key:
    ```
    GROQ_API_KEY=your_key_here
    ```
3.  Build and run with Docker (recommended as it handles ffmpeg):
    ```bash
    docker build -t youtube-backend .
    docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here youtube-backend
    ```
    Or if you have Python and ffmpeg installed locally:
    ```bash
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

### Frontend
1.  Navigate to `frontend/`.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the dev server:
    ```bash
    npm run dev
    ```
4.  Open `http://localhost:5173` (or the port shown).

## Deployment (Google Cloud Vertex / Cloud Run)
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
