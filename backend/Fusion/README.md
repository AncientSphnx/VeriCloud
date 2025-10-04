# Fusion Backend

This backend combines predictions from Text and Voice models using a weighted ensemble approach.

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

Start the fusion backend on port 8002:

```bash
cd "C:\Users\91829\OneDrive\Desktop\Lie Detector (MAIN)\backend\Fusion"
uvicorn app:app --reload --port 8002
```

## Required Services

The fusion backend depends on these services running:

1. **Text Backend** - Port 8000
   ```bash
   cd "../Text"
   uvicorn app:app --reload --port 8000
   ```

2. **Voice Backend** - Port 8001
   ```bash
   cd "../Voice"
   uvicorn app:app --reload --port 8001
   ```

## API Endpoints

### POST /predict_fusion

Combines text and voice analysis for a final prediction.

**Request:**
- `text` (form-data): The text statement to analyze
- `audio_file` (file): Audio file for voice analysis

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
      "weight": 0.5,
      "contribution": 0.29
    },
    "voice": {
      "prediction": "Deceptive",
      "confidence": 0.85,
      "weight": 0.5,
      "contribution": 0.425
    }
  },
  "reasoning": "Voice model shows strongest signal (85.0% confidence) influencing final decision.",
  "weights_used": {
    "text": 0.5,
    "voice": 0.5
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
  "voice_api": "http://127.0.0.1:8001/predict"
}
```

## Fusion Algorithm

The weighted ensemble uses these default weights:
- Text: 50%
- Voice: 50%

The algorithm:
1. Converts each model's prediction to a deception score (0-1)
2. Calculates weighted average
3. Applies 0.5 threshold for final decision
4. Provides reasoning based on model agreement and confidence levels

## Future Enhancements

When face recognition is added:
- Weights will be redistributed: Text 40%, Voice 40%, Face 20%
- Update the `weighted_fusion()` function to include face results
