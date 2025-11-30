from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import tempfile
import os
import boto3
from typing import Optional
import uuid
from datetime import datetime
import sys
import os

# Ensure backend package is in Python path for imports to work on Render
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_project_root = os.path.dirname(_backend_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Add parent directory to path for imports (fallback)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Database.s3_storage import upload_analysis_file, upload_analysis_data
    from Database.operations import (
        create_new_analysis, update_analysis_files, update_analysis_results,
        update_analysis_status, add_analysis_error, create_new_session
    )
    DB_INTEGRATION_AVAILABLE = True
    print("✅ Database integration available")
except ImportError as e:
    print(f"⚠️ Database integration not available: {e}")
    DB_INTEGRATION_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("🔄 Running without database storage (fusion results only)")
    DB_INTEGRATION_AVAILABLE = False

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend API Endpoints (with local fallbacks)
TEXT_API = "https://vericloud-text-tho9.onrender.com/predict_text"
VOICE_API = "https://vericloud-y9c9.onrender.com/predict"
FACE_API = "https://vericloud-face-s8zm.onrender.com/predict"

# Local fallback URLs
LOCAL_TEXT_API = "http://127.0.0.1:8000/predict_text"
LOCAL_VOICE_API = "http://127.0.0.1:8001/predict"
LOCAL_FACE_API = "http://127.0.0.1:8002/predict"

def call_api_with_fallback(render_url: str, local_url: str, *args, **kwargs):
    """Try Render API first, fallback to local API if it fails"""
    try:
        print(f"🔍 Trying Render API at: {render_url}")
        response = requests.post(render_url, *args, **kwargs)
        print(f"📡 Render API response status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as render_error:
        print(f"❌ Render API failed: {str(render_error)}")
        print(f"🔄 Falling back to local API at: {local_url}")
        try:
            response = requests.post(local_url, *args, **kwargs)
            print(f"🏠 Local API response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except Exception as local_error:
            print(f"❌ Local API also failed: {str(local_error)}")
            raise render_error  # Raise the original Render error

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
    # For now: Text 35%, Voice 35%, Face 30% (when available)
    # Reduced text/voice weights due to bias issues
    if face_result:
        weights = {"text": 0.35, "voice": 0.35, "face": 0.30}
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
        results["text"] = call_api_with_fallback(TEXT_API, LOCAL_TEXT_API, data=text_form)
        print(f"📝 Text API result: {results['text']}")
    except Exception as e:
        print(f"❌ Text API error: {str(e)}")
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
                results["voice"] = call_api_with_fallback(VOICE_API, LOCAL_VOICE_API, files=files)
                print(f"🎤 Voice API result: {results['voice']}")
            
            # Clean up
            os.remove(tmp_path)
        except Exception as e:
            print(f"❌ Voice API error: {str(e)}")
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
                results["face"] = call_api_with_fallback(FACE_API, LOCAL_FACE_API, files=files)
                print(f"👤 Face API result: {results['face']}")
            
            # Clean up
            os.remove(tmp_path)
        except Exception as e:
            print(f"❌ Face API error: {str(e)}")
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
    
    print(f"🔍 Fusion validation (simple endpoint):")
    print(f"   Text valid: {text_valid} (prediction: {results['text'].get('prediction')})")
    print(f"   Voice valid: {voice_valid} (prediction: {results['voice'].get('prediction')})")
    print(f"   Face valid: {face_valid} (prediction: {results['face'].get('prediction')})")
    
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


@app.post("/predict_fusion_with_storage")
async def predict_fusion_with_storage(
    text: str = Form(...),
    user_id: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None)
):
    """
    Enhanced fusion endpoint that:
    1. Uploads files to S3 with organized structure
    2. Stores analysis in MongoDB
    3. Runs predictions (text, voice, face)
    4. Stores results in MongoDB
    5. Returns complete analysis with file URLs
    """
    if not DB_INTEGRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database integration not available")
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Create or use existing session
    if not session_id:
        try:
            session_id = create_new_session(user_id)
        except Exception as e:
            print(f"⚠️ Failed to create session: {e}")
            session_id = str(uuid.uuid4())  # Fallback to UUID
    
    try:
        # Step 1: Create analysis record in MongoDB
        if DB_INTEGRATION_AVAILABLE:
            try:
                create_new_analysis(user_id, session_id, analysis_id)
                update_analysis_status(analysis_id, "processing", {
                    "processing_start_time": datetime.utcnow()
                })
            except Exception as e:
                print(f"⚠️ Failed to create analysis record: {e}")
                # Continue anyway - we'll still return results
        else:
            print("🔄 Skipping database storage - running in memory mode")
        
        results = {}
        errors = {}
        file_urls = {}
        
        # Step 2: Upload video file to S3 and run Face analysis
        if video_file:
            try:
                # Save video temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as tmp:
                    content = await video_file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                # Upload to S3
                if DB_INTEGRATION_AVAILABLE:
                    try:
                        video_s3_data = upload_analysis_file(tmp_path, user_id, analysis_id, 'video')
                        file_urls['video'] = video_s3_data
                        
                        # Update MongoDB with video file info
                        update_analysis_files(analysis_id, 'video', video_s3_data)
                    except Exception as e:
                        print(f"⚠️ Failed to upload video to S3: {e}")
                else:
                    print("🔄 Skipping S3 upload - running in memory mode")
                
                # Call Face API
                try:
                    with open(tmp_path, 'rb') as f:
                        files = {'file': (video_file.filename, f, video_file.content_type)}
                        results["face"] = call_api_with_fallback(FACE_API, LOCAL_FACE_API, files=files, timeout=300)
                        print(f"👤 Face API result: {results['face']}")
                        
                        # Store face results in MongoDB
                        if DB_INTEGRATION_AVAILABLE:
                            try:
                                update_analysis_results(analysis_id, 'face', {
                                    'prediction': results["face"].get('prediction'),
                                    'confidence': results["face"].get('confidence'),
                                    'features': results["face"].get('features')
                                })
                            except Exception as e:
                                print(f"⚠️ Failed to store face results: {e}")
                except Exception as e:
                    print(f"❌ Face API error: {str(e)}")
                    errors["face"] = str(e)
                    results["face"] = {"prediction": "Unknown", "confidence": 0.0}
                    if DB_INTEGRATION_AVAILABLE:
                        try:
                            add_analysis_error(analysis_id, f"Face analysis failed: {str(e)}")
                        except Exception as db_e:
                            print(f"⚠️ Failed to store error: {db_e}")
                
                # Clean up temp file
                os.remove(tmp_path)
                
            except Exception as e:
                errors["face"] = f"Video processing failed: {str(e)}"
                results["face"] = {"prediction": "Unknown", "confidence": 0.0}
        else:
            errors["face"] = "No video file provided"
            results["face"] = {"prediction": "Unknown", "confidence": 0.0}
        
        # Step 3: Upload audio file to S3 and run Voice analysis
        if audio_file:
            try:
                # Save audio temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as tmp:
                    content = await audio_file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                # Upload to S3
                try:
                    audio_s3_data = upload_analysis_file(tmp_path, user_id, analysis_id, 'audio')
                    file_urls['audio'] = audio_s3_data
                    
                    # Update MongoDB with audio file info
                    update_analysis_files(analysis_id, 'audio', audio_s3_data)
                except Exception as e:
                    print(f"⚠️ Failed to upload audio to S3: {e}")
                
                # Call Voice API
                try:
                    with open(tmp_path, 'rb') as f:
                        files = {'file': (audio_file.filename, f, audio_file.content_type)}
                        results["voice"] = call_api_with_fallback(VOICE_API, LOCAL_VOICE_API, files=files, timeout=300)
                        print(f"🎤 Voice API result: {results['voice']}")
                        
                        # Store voice results in MongoDB
                        update_analysis_results(analysis_id, 'voice', {
                            'prediction': results["voice"].get('prediction'),
                            'confidence': results["voice"].get('confidence'),
                            'features': results["voice"].get('features')
                        })
                except Exception as e:
                    print(f"❌ Voice API error: {str(e)}")
                    errors["voice"] = str(e)
                    results["voice"] = {"prediction": "Unknown", "confidence": 0.0}
                    add_analysis_error(analysis_id, f"Voice analysis failed: {str(e)}")
                
                # Clean up temp file
                os.remove(tmp_path)
                
            except Exception as e:
                errors["voice"] = f"Audio processing failed: {str(e)}"
                results["voice"] = {"prediction": "Unknown", "confidence": 0.0}
        else:
            errors["voice"] = "No audio file provided"
            results["voice"] = {"prediction": "Unknown", "confidence": 0.0}
        
        # Step 4: Upload transcript to S3 and run Text analysis
        try:
            # Upload transcript to S3
            try:
                transcript_s3_data = upload_analysis_data(
                    text, user_id, analysis_id, 'transcript', '.txt'
                )
                file_urls['transcript'] = transcript_s3_data
                transcript_s3_data['text_content'] = text
                transcript_s3_data['word_count'] = len(text.split())
                
                # Update MongoDB with transcript info
                update_analysis_files(analysis_id, 'transcript', transcript_s3_data)
            except Exception as e:
                print(f"⚠️ Failed to upload transcript to S3: {e}")
            
            # Call Text API
            text_form = {"text": text}
            results["text"] = call_api_with_fallback(TEXT_API, LOCAL_TEXT_API, data=text_form, timeout=60)
            print(f"📝 Text API result: {results['text']}")
            
            # Store text results in MongoDB
            update_analysis_results(analysis_id, 'text', {
                'prediction': results["text"].get('prediction'),
                'confidence': results["text"].get('confidence'),
                'features': results["text"].get('features')
            })
        except Exception as e:
            errors["text"] = str(e)
            results["text"] = {"prediction": "Unknown", "confidence": 0.0}
            add_analysis_error(analysis_id, f"Text analysis failed: {str(e)}")
        
        # Step 5: Apply Fusion Algorithm
        text_valid = results["text"]["prediction"] != "Unknown"
        voice_valid = results["voice"]["prediction"] != "Unknown"
        face_valid = results["face"]["prediction"] != "Unknown"
        
        print(f"🔍 Fusion validation:")
        print(f"   Text valid: {text_valid} (prediction: {results['text'].get('prediction')})")
        print(f"   Voice valid: {voice_valid} (prediction: {results['voice'].get('prediction')})")
        print(f"   Face valid: {face_valid} (prediction: {results['face'].get('prediction')})")
        
        if text_valid and voice_valid:
            if face_valid:
                fusion_result = weighted_fusion(results["text"], results["voice"], results["face"])
            else:
                fusion_result = weighted_fusion(results["text"], results["voice"])
            
            # Store fusion results in MongoDB
            update_analysis_results(analysis_id, 'fusion', {
                'final_prediction': fusion_result['final_prediction'],
                'final_confidence': fusion_result['final_confidence'],
                'final_score': fusion_result['final_score'],
                'breakdown': fusion_result['breakdown'],
                'reasoning': fusion_result['reasoning'],
                'weights_used': fusion_result['weights_used']
            })
            
            # Mark analysis as completed
            update_analysis_status(analysis_id, "completed", {
                "models_used": ["text", "voice"] + (["face"] if face_valid else [])
            })
        else:
            fusion_result = {
                "final_prediction": "Error",
                "final_confidence": 0.0,
                "final_score": 0.0,
                "breakdown": results,
                "reasoning": "Text and Voice models are required for fusion. One or both failed.",
                "weights_used": {}
            }
            
            # Mark analysis as failed
            update_analysis_status(analysis_id, "failed")
            add_analysis_error(analysis_id, "Insufficient valid predictions for fusion")
        
        # Add errors and file URLs to response
        if errors:
            fusion_result["errors"] = errors
        
        fusion_result["file_urls"] = file_urls
        fusion_result["analysis_id"] = analysis_id
        fusion_result["session_id"] = session_id
        fusion_result["user_id"] = user_id
        
        return fusion_result
        
    except Exception as e:
        # Mark analysis as failed
        try:
            update_analysis_status(analysis_id, "failed")
            add_analysis_error(analysis_id, f"Critical error: {str(e)}")
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "text_api": TEXT_API,
        "voice_api": VOICE_API,
        "face_api": FACE_API,
        "db_integration": DB_INTEGRATION_AVAILABLE
    }
