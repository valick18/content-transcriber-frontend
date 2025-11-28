# Content Transcriber & Chat App

A mobile-first web application to download, transcribe, and chat with YouTube videos using Groq API.

## Features
- **Download & Transcribe**: Paste a YouTube link to get a full transcript.
- **Chat with Video**: Ask questions about the video content using Llama3 via Groq.
- **Mobile-First Design**: Optimized for mobile devices (PWA-ready).
- **Dark Mode**: Premium dark aesthetic.

## Architecture
- **Frontend**: React + Vite (Deployed on **Vercel**)
- **Backend**: FastAPI + Python (Deployed on **Railway**)

## Development

### Frontend
1.  Install dependencies:
    ```bash
    npm install
    ```
2.  Run the dev server:
    ```bash
    npm run dev
    ```
3.  Open `http://localhost:5173`.

## Deployment

### Frontend (Vercel)
The frontend is deployed on Vercel. It connects to the backend via the `VITE_API_URL` environment variable.

### Backend (Railway)
The backend is deployed on Railway. See `RAILWAY_DEPLOYMENT.md` for details.
