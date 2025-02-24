from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends, HTTPException, Security
from typing import List, Dict
import uuid
import os
import json
from PIL import Image
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader

# FastAPI app setup
app = FastAPI()

# 🔑 API Key Authentication
API_KEY = "new-super-secure-key-12345"
api_key_header = APIKeyHeader(name="X-API-KEY")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Not authenticated")

# Job tracking storage
JOB_STATUS_FILE = "job_status.json"

def load_job_status():
    if os.path.exists(JOB_STATUS_FILE):
        with open(JOB_STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_job_status(job_id, status, results=None):
    job_data = load_job_status()
    job_data[job_id] = {"status": status, "results": results or []}
    with open(JOB_STATUS_FILE, "w") as f:
        json.dump(job_data, f, indent=4)

# 🔥 IMAGE PROCESSING FUNCTION (Fully Fixed)
def process_image_batch(file_paths: List[str], processing_options: dict, job_id: str):
    """Processes multiple images and ensures full compatibility."""
    results = []
    print(f"🔥 Processing Job ID: {job_id}, Files: {file_paths}")

    for path in file_paths:
        try:
            print(f"📂 Opening image: {path}")
            with Image.open(path) as img:
                # Ensure compatibility for formats like WebP, PNG, etc.
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")  # Convert for non-RGB formats

                # Set output directory & filename
                job_dir = os.path.dirname(path)
                output_format = processing_options.get("format", "JPEG")  # Default: JPEG
                output_format = output_format.upper()  # Ensure correct format for PIL

                # Ensure format consistency for JPG
                format_mapping = {"JPG": "JPEG", "WEBP": "WEBP", "PNG": "PNG"}
                output_format = format_mapping.get(output_format, output_format)

                output_filename = f"{os.path.splitext(os.path.basename(path))[0]}.{output_format.lower()}"
                output_path = os.path.join(job_dir, output_filename)

                # Resize if needed
                if processing_options.get("resize"):
                    width, height = processing_options["resize"]
                    img = img.resize((width, height), Image.LANCZOS)

                # Save the processed image
                print(f"💾 Saving processed image to: {output_path}")
                img.save(output_path, format=output_format, quality=processing_options.get("quality", 85), optimize=True)

                results.append({"original": path, "processed": output_path})

        except Exception as e:
            print(f"❌ ERROR processing {path}: {e}")
            results.append({"original": path, "error": str(e)})

    # ✅ Save results in job tracking
    save_job_status(job_id, "completed", results)
    print(f"✅ Job {job_id} completed! Results: {results}")

# 📂 API Endpoint: Upload & Process Images
@app.post("/api/batch-process/", dependencies=[Depends(verify_api_key)])
async def create_batch_job(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
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
        temp_path = os.path.join(job_dir, file.filename)
        print(f"⬆️ Saving uploaded file: {temp_path}")  # Debugging
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        file_paths.append(temp_path)

    processing_options = {
        "resize": (width, height) if width and height else None,
        "format": output_format or "JPEG",  # Default to JPEG
        "quality": quality
    }

    save_job_status(job_id, "processing")
    background_tasks.add_task(process_image_batch, file_paths, processing_options, job_id)

    return {"job_id": job_id, "status": "processing", "file_count": len(files)}

# 📊 API Endpoint: Check Job Status
@app.get("/api/job-status/{job_id}", dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: str):
    job_data = load_job_status()
    if job_id not in job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_data[job_id]

# 📥 API Endpoint: Download Processed Image
@app.get("/api/get-processed/{job_id}/{filename}", dependencies=[Depends(verify_api_key)])
async def get_processed_image(job_id: str, filename: str):
    file_path = os.path.join("temp", job_id, filename)
    print(f"📥 Retrieving processed file: {file_path}")  # Debugging
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
