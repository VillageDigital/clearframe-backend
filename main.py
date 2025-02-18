from fastapi import FastAPI, UploadFile, File
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, ClearFrame is live! 🚀"}

@app.get("/status")
def get_status():
    return {"status": "API is running smoothly! ✅"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "query": q}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename, "message": "File received successfully! ✅"}