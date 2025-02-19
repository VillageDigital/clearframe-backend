from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends, HTTPException, Security
from typing import List, Dict
import uuid
import os
import json
from PIL import Image
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()

# Security: Simple API Key Authentication (Replace with Firebase Auth later if needed)
API_KEY = "your-secure-api-key"
api_key_header = APIKeyHeader(name="X-API-KEY")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Job tracking storage (Use Firestore later if needed)
JOB_STATUS_FILE = "job_status.json"

def load_job_status():
    if os.path.exists(JOB_STATUS_FILE):
        with open(JOB_STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_job_status(job_id, status, results=None):
    job_data = load_job_status()
    job_data[job_id] = {"status": status, "results": results}
    with open(JOB_STATUS_FILE, "w") as f:
        json.dump(job_data, f)

def process_image_batch(file_paths: List[str], processing_options: dict, job_id: str):
    """Background task to process multiple images."""
    results = []
    
    for path in file_paths:
        try:
            with Image.open(path) as img:
                # Apply processing options
                if processing_options.get("resize"):
                    width, height = processing_options["resize"]
                    img = img.resize((width, height), Image.LANCZOS)
                
                if processing_options.get("format"):
                    output_path = f"{os.path.splitext(path)[0]}.{processing_options['format']}"
                    img.save(output_path, 
                             quality=processing_options.get("quality", 85),
                             optimize=True)
                    results.append({"original": path, "processed": output_path})
        except Exception as e:
            results.append({"original": path, "error": str(e)})
    
    save_job_status(job_id, "completed", results)

@app.post("/api/batch-process/")
async def create_batch_job(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    api_key: str = Security(verify_api_key),  # Secure API
    width: int = None,
    height: int = None,
    output_format: str = None,
    quality: int = 85
):
    job_id = str(uuid.uuid4())
    job_dir = f"temp/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    
    file_paths = []
    for file in files:
        temp_path = f"{job_dir}/{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        file_paths.append(temp_path)
    
    processing_options = {
        "resize": (width, height) if width and height else None,
        "format": output_format,
        "quality": quality
    }

    save_job_status(job_id, "processing")
    background_tasks.add_task(process_image_batch, file_paths, processing_options, job_id)
    
    return {"job_id": job_id, "status": "processing", "file_count": len(files)}

@app.get("/api/job-status/{job_id}")
async def get_job_status(job_id: str, api_key: str = Security(verify_api_key)):
    job_data = load_job_status()
    if job_id not in job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_data[job_id]

@app.get("/api/get-processed/{job_id}/{filename}")
async def get_processed_image(job_id: str, filename: str, api_key: str = Security(verify_api_key)):
    file_path = f"temp/{job_id}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
