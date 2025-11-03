from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from predictor import predict_face, load_face_model

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load model on startup to avoid timeout on first request
@app.on_event("startup")
async def startup_event():
    try:
        print("[INFO] Pre-loading Face model on startup...")
        load_face_model()
        print("[INFO] Face model loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not pre-load model: {e}")
        print("[INFO] Will load on first request instead")


@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    """
    API endpoint to analyze face video/image and predict deception.
    Expects a video or image file.
    """
    # Determine if file is video or image based on content type
    is_video = file.content_type.startswith('video/') if file.content_type else True
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        # Run prediction
        label, confidence = predict_face(tmp_path, is_video=is_video)
        
        return {"prediction": label, "confidence": confidence}
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Try to load model to ensure it's working
        load_face_model()
        return {"status": "ok", "service": "face-analysis", "model": "loaded"}
    except Exception as e:
        return {"status": "error", "service": "face-analysis", "error": str(e)}, 503
