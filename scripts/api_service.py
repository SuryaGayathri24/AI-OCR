from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
import uuid

from scripts.integrated_pipeline import FraudEngine

app = FastAPI(title="Aadhaar Fraud Detection API")
engine = FraudEngine()

UPLOAD_DIR = Path("outputs/api_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix or ".jpg"
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"

    with tmp_path.open("wb") as f:
        f.write(await file.read())

    result = engine.predict(str(tmp_path))

    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run("scripts.api_service:app", host="0.0.0.0", port=8000, reload=True)
