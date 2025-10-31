from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import tempfile
import os
import boto3
from typing import Optional

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend endpoints
TEXT_API = "https://vericloud-text-tho9.onrender.com/predict_text"
VOICE_API = "https://vericloud-y9c9.onrender.com/predict"
FACE_API = "https://vericloud-face-s8zm.onrender.com/predict"

# ----------------------------
# S3 Configuration
# ----------------------------
def get_s3_client():
    """Get an S3 client with configured credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )


def download_from_s3(bucket, s3_key):
    """
    Download a file from S3 to a temporary location.
    Returns the local file path.
    """
    try:
        s3_client = get_s3_client()
        tmp_dir = tempfile.mkdtemp()
        local_path = os.path.join(tmp_dir, os.path.basename(s3_key))
        
        print(f"Downloading from s3://{bucket}/{s3_key}")
        s3_client.download_file(bucket, s3_key, local_path)
        
        return local_path
    except Exception as e:
        print(f"⚠️ Failed to download from S3: {e}")
        raise

def weighted_fusion(text_result, voice_result, face_result=None):
    """
    Weighted ensemble fusion algorithm
    Returns final prediction and detailed breakdown
    """
    # Normalize prediction labels to standard format
    def normalize_prediction(result):
        pred = result["prediction"]
        if pred in ["Lie", "Deceptive"]:
            return "Deceptive"
        elif pred in ["Truth", "Truthful"]:
            return "Truthful"
        return pred
    
    text_result["prediction"] = normalize_prediction(text_result)
    voice_result["prediction"] = normalize_prediction(voice_result)
    if face_result:
        face_result["prediction"] = normalize_prediction(face_result)
    
    # Weights (can be tuned based on model performance)
    # For now: Text 40%, Voice 40%, Face 20% (when available)
    if face_result:
        weights = {"text": 0.40, "voice": 0.40, "face": 0.20}
    else:
        # Redistribute when face is not available
        weights = {"text": 0.50, "voice": 0.50, "face": 0.0}
    
    # Convert predictions to deception scores (0-1, where 1 = Deceptive)
    def get_deception_score(result):
        # Confidence should be normalized to 0-1 range
        confidence = result["confidence"]
        if confidence > 1:
            confidence = confidence / 100.0
        
        if result["prediction"] == "Deceptive":
            return confidence
        else:  # Truthful
            return 1 - confidence
    
    scores = {
        "text": get_deception_score(text_result),
        "voice": get_deception_score(voice_result),
    }
    
    if face_result:
        scores["face"] = get_deception_score(face_result)
    
    # Calculate weighted average
    final_score = sum(scores[m] * weights[m] for m in scores)
    
    # Decision threshold
    final_prediction = "Deceptive" if final_score > 0.5 else "Truthful"
    final_confidence = final_score if final_score > 0.5 else (1 - final_score)
    
    # Normalize confidence to 0-1 range for display
    def normalize_confidence(conf):
        return conf / 100.0 if conf > 1 else conf
    
    # Build breakdown
    breakdown = {
        "text": {
            "prediction": text_result["prediction"],
            "confidence": normalize_confidence(text_result["confidence"]),
            "weight": weights["text"],
            "contribution": scores["text"] * weights["text"]
        },
        "voice": {
            "prediction": voice_result["prediction"],
            "confidence": normalize_confidence(voice_result["confidence"]),
            "weight": weights["voice"],
            "contribution": scores["voice"] * weights["voice"]
        }
    }
    
    if face_result:
        breakdown["face"] = {
            "prediction": face_result["prediction"],
            "confidence": face_result["confidence"],
            "weight": weights["face"],
            "contribution": scores["face"] * weights["face"]
        }
    
    # Generate reasoning
    models_agree = len(set(breakdown[m]["prediction"] for m in breakdown)) == 1
    if models_agree:
        reasoning = f"All models agree on {final_prediction.lower()} prediction with high confidence."
    else:
        high_conf_models = [m for m in breakdown if breakdown[m]["confidence"] > 0.7]
        if high_conf_models:
            dominant = max(high_conf_models, key=lambda m: breakdown[m]["confidence"])
            reasoning = f"{dominant.capitalize()} model shows strongest signal ({breakdown[dominant]['confidence']*100:.1f}% confidence) influencing final decision."
        else:
            reasoning = "Models show mixed signals. Decision based on weighted consensus."
    
    return {
        "final_prediction": final_prediction,
        "final_confidence": final_confidence,
        "final_score": final_score,
        "breakdown": breakdown,
        "reasoning": reasoning,
        "weights_used": weights
    }


@app.post("/predict_fusion")
async def predict_fusion(
    text: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None)
):
    """
    Fusion endpoint that combines text, voice, and face predictions
    """
    results = {}
    errors = {}
    
    # 1. Text Analysis
    try:
        text_form = {"text": text}
        text_response = requests.post(TEXT_API, data=text_form)
        text_response.raise_for_status()
        results["text"] = text_response.json()
    except Exception as e:
        errors["text"] = str(e)
        results["text"] = {"prediction": "Unknown", "confidence": 0.0}
    
    # 2. Voice Analysis
    if audio_file:
        try:
            # Save audio file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as tmp:
                content = await audio_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Call voice API
            with open(tmp_path, 'rb') as f:
                files = {'file': (audio_file.filename, f, audio_file.content_type)}
                voice_response = requests.post(VOICE_API, files=files)
                voice_response.raise_for_status()
                results["voice"] = voice_response.json()
            
            # Clean up
            os.remove(tmp_path)
        except Exception as e:
            errors["voice"] = str(e)
            results["voice"] = {"prediction": "Unknown", "confidence": 0.0}
    else:
        errors["voice"] = "No audio file provided"
        results["voice"] = {"prediction": "Unknown", "confidence": 0.0}
    
    # 3. Face Analysis
    if video_file:
        try:
            # Save video file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as tmp:
                content = await video_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Call face API
            with open(tmp_path, 'rb') as f:
                files = {'file': (video_file.filename, f, video_file.content_type)}
                face_response = requests.post(FACE_API, files=files)
                face_response.raise_for_status()
                results["face"] = face_response.json()
            
            # Clean up
            os.remove(tmp_path)
        except Exception as e:
            errors["face"] = str(e)
            results["face"] = {"prediction": "Unknown", "confidence": 0.0}
    else:
        errors["face"] = "No video file provided"
        results["face"] = {"prediction": "Unknown", "confidence": 0.0}
    
    # 4. Apply Fusion Algorithm
    # Check if we have at least text and voice
    text_valid = results["text"]["prediction"] != "Unknown"
    voice_valid = results["voice"]["prediction"] != "Unknown"
    face_valid = results["face"]["prediction"] != "Unknown"
    
    if text_valid and voice_valid:
        if face_valid:
            # All three models available
            fusion_result = weighted_fusion(results["text"], results["voice"], results["face"])
        else:
            # Only text and voice
            fusion_result = weighted_fusion(results["text"], results["voice"])
    else:
        # Fallback if text or voice failed
        fusion_result = {
            "final_prediction": "Error",
            "final_confidence": 0.0,
            "final_score": 0.0,
            "breakdown": results,
            "reasoning": "Text and Voice models are required for fusion. One or both failed to provide predictions.",
            "weights_used": {}
        }
    
    # Add errors to response if any
    if errors:
        fusion_result["errors"] = errors
    
    return fusion_result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "text_api": TEXT_API,
        "voice_api": VOICE_API,
        "face_api": FACE_API
    }
