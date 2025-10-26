# Face Analysis API

This is the FastAPI backend for face-based deception detection using the face model.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
uvicorn app:app --host 127.0.0.1 --port 8002 --reload
```

The API will be available at `http://127.0.0.1:8002`

## API Endpoints

### POST /predict
Analyzes a video or image file for deception detection.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the video/image

**Response:**
```json
{
  "prediction": "Truthful|Deceptive",
  "confidence": 0.85
}
```

**Example using curl:**
```bash
curl -X POST -F "file=@video.mp4" http://127.0.0.1:8002/predict
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "face-analysis"
}
```

## How It Works

1. **Feature Extraction**: The API uses MediaPipe Face Mesh to detect facial landmarks and extract 70+ deception-relevant features including:
   - Geometric features (eye/mouth ratios, asymmetry)
   - Temporal features (blink detection, movement patterns)
   - Texture features (LBP, HOG, skin texture)
   - Eye gaze features
   - Skin analysis features
   - Head movement features

2. **Baseline Establishment**: The model establishes a baseline of normal behavior during the first 30 seconds

3. **Prediction**: Uses the trained model to classify frames as Truthful or Deceptive

4. **Aggregation**: Results from multiple frames are aggregated to provide a final prediction with confidence score

## Supported File Formats

- **Video**: MP4, WebM, AVI, MOV, etc.
- **Image**: JPG, PNG, BMP, etc.

## Notes

- The API automatically detects whether the input is a video or image based on the file extension
- Processing time depends on video length (typically 10-30 seconds for a 30-second video)
- The model requires a clear view of the face for accurate detection
- Minimum video duration: ~1 second
- Recommended video duration: 10-30 seconds for better accuracy

## Integration with Frontend

The frontend (FaceAnalysis.tsx) connects to this API at:
```
POST http://127.0.0.1:8002/predict
```

The frontend sends video/image files and receives predictions with confidence scores.
