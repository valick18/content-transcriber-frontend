from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import services
import shutil

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    services.check_ffmpeg()

@app.get("/")
def read_root():
    return {"message": "Python Backend is Running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    job_id: str
    question: str

@app.post("/api/process")
async def process_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    services.jobs[job_id] = {"status": "queued", "url": request.url}
    services.save_jobs()
    background_tasks.add_task(services.process_video, job_id, request.url)
    return {"job_id": job_id}

@app.post("/api/upload")
async def upload_endpoint(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    job_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1]
    file_path = f"{services.DOWNLOAD_DIR}/{job_id}.{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    services.jobs[job_id] = {"status": "queued", "title": file.filename}
    services.save_jobs()
    
    if background_tasks:
        background_tasks.add_task(services.process_upload, job_id, file_path, file.filename)
    
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    job = services.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job["status"], "error": job.get("error")}

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    job = services.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not finished")
    return {"transcript": job["transcript"]}

@app.get("/api/jobs")
async def get_jobs():
    # Return list of jobs with id, status, title (url for now)
    return [
        {"id": k, "status": v["status"], "title": v.get("title", "Unknown Video"), "date": "Today"} 
        for k, v in services.jobs.items()
    ]

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    if job_id in services.jobs:
        del services.jobs[job_id]
        services.save_jobs()
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Job not found")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    job = services.jobs.get(request.job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not ready")
    
    answer = services.ask_question(job["transcript"], request.question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
