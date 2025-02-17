from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, ClearFrame is live! 🚀"}
@app.get("/status")
def check_status():
    return {"status": "API is running smoothly! ✅"}