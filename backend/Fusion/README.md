# Fusion Backend

This backend combines predictions from Text, Voice, and Face models using a weighted ensemble approach.

## Setup

### Prerequisites
- Python 3.8+
- FastAPI
- Requests

### Installation

```bash
pip install fastapi uvicorn requests
```

## Running the Server

Start the fusion backend on port 8003:

```bash
cd backend/Fusion
uvicorn app:app --reload --port 8003
```

## Required Services

The fusion backend depends on these services running:

1. **Text Backend** - Port 8000
   ```bash
   cd backend/Text
   uvicorn app:app --reload --port 8000
   ```

2. **Voice Backend** - Port 8001
   ```bash
   cd backend/Voice
   uvicorn app:app --reload --port 8001
   ```

3. **Face Backend** - Port 8002
   ```bash
   cd backend/Face
   uvicorn app:app --reload --port 8002
   ```

## API Endpoints

### POST /predict_fusion

Combines text, voice, and face analysis for a final prediction.

**Request:**
- `text` (form-data): The text statement to analyze
- `audio_file` (file): Audio file for voice analysis (optional)
- `video_file` (file): Video file for face analysis (optional)

**Response:**
```json
{
  "final_prediction": "Deceptive",
  "final_confidence": 0.73,
  "final_score": 0.65,
  "breakdown": {
    "text": {
      "prediction": "Truthful",
      "confidence": 0.42,
      "weight": 0.4,
      "contribution": 0.168
    },
    "voice": {
      "prediction": "Deceptive",
      "confidence": 0.85,
      "weight": 0.4,
      "contribution": 0.34
    },
    "face": {
      "prediction": "Deceptive",
      "confidence": 0.78,
      "weight": 0.2,
      "contribution": 0.156
    }
  },
  "reasoning": "All models agree on deceptive prediction with high confidence.",
  "weights_used": {
    "text": 0.4,
    "voice": 0.4,
    "face": 0.2
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "text_api": "http://127.0.0.1:8000/predict_text",
  "voice_api": "http://127.0.0.1:8001/predict",
  "face_api": "http://127.0.0.1:8002/predict"
}
```

## Fusion Algorithm

The weighted ensemble uses these default weights:
- **Text: 40%** (linguistic patterns and content analysis)
- **Voice: 40%** (vocal stress, pitch, and speech patterns)
- **Face: 20%** (facial expressions, micro-expressions, and behavioral patterns)

When face data is not provided:
- Text: 50%, Voice: 50%

The algorithm:
1. Normalizes predictions to standard format (Truthful/Deceptive)
2. Converts each model's prediction to a deception score (0-1)
3. Calculates weighted average of all available models
4. Applies 0.5 threshold for final decision
5. Provides reasoning based on model agreement and confidence levels
6. Returns detailed breakdown showing each model's contribution
