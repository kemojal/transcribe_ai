import cloudinary
import os 
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from .metrics import (
    audio_file_size_bytes,
    audio_processing_duration_seconds,
    audio_format_errors_total,
    transcription_requests_total,
    transcription_duration_seconds,
    transcription_failures_total,
    transcription_confidence_score,
    transcription_queue_size,
    custom_metrics
)
import time
from typing import Optional

# from app.utils.helpers import create_text_clip
from .api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TranscribeAI API")

# Initialize Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)

# Add custom metrics
for metric in custom_metrics():
    instrumentator.add(metric)

# Instrument the app
instrumentator.instrument(app).expose(app)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "https://editube-kemojals-projects.vercel.app",
    "http://localhost:5173/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
          
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET") 
)

app.include_router(api_router)

@app.get("/")
async def read_item():
    return {"hello word"}

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = "default",
    confidence_threshold: Optional[float] = 0.8
):
    try:
        # Record file size
        file_size = os.path.getsize(file.filename)
        audio_file_size_bytes.labels(format=file.content_type).observe(file_size)

        # Start processing timer
        start_time = time.time()

        # Process audio file
        try:
            # Your audio processing logic here
            processing_time = time.time() - start_time
            audio_processing_duration_seconds.labels(format=file.content_type).observe(processing_time)
        except Exception as e:
            audio_format_errors_total.labels(error_type=str(type(e).__name__)).inc()
            raise HTTPException(status_code=400, detail=f"Audio processing error: {str(e)}")

        # Record transcription request
        transcription_requests_total.labels(model=model).inc()

        # Start transcription timer
        transcription_start = time.time()

        try:
            # Your transcription logic here
            transcription_time = time.time() - transcription_start
            transcription_duration_seconds.labels(model=model).observe(transcription_time)

            # Record confidence score
            confidence_score = 0.95  # Replace with actual confidence score
            transcription_confidence_score.labels(model=model).set(confidence_score)

            return {
                "transcription": "Your transcription result here",
                "confidence": confidence_score
            }
        except Exception as e:
            transcription_failures_total.labels(error_type=str(type(e).__name__)).inc()
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue-size")
async def get_queue_size():
    # Update queue size metric
    current_queue_size = 0  # Replace with actual queue size
    transcription_queue_size.set(current_queue_size)
    return {"queue_size": current_queue_size}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )