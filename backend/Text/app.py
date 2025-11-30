from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from predictor import predict_text  # your text prediction function
import requests
import json
import os

app = FastAPI()

# Database API configuration
DATABASE_API_URL = os.getenv("DATABASE_API_URL", "https://vericloud-db-wbhv.onrender.com")

def auto_save_report(user_id, module_type, prediction, confidence):
    """Automatically save report to database"""
    try:
        report_data = {
            "user_id": user_id,
            "module_type": module_type,
            "prediction": prediction,
            "confidence": confidence
        }
        # Use the unauthenticated endpoint for module APIs
        response = requests.post(f"{DATABASE_API_URL}/api/simple_reports/create_unauth", 
                                json=report_data, timeout=5)
        if response.status_code == 200:
            print(f"✅ {module_type} report saved automatically")
            return True
        else:
            print(f"⚠️ Failed to save {module_type} report: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Database connection error for {module_type}: {e}")
        return False

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict_text")
async def predict_text_endpoint(text: str = Form(...), user_id: str = Form(None)):
    """
    API endpoint to analyze text and predict deception.
    Expects form-data with fields 'text' and optional 'user_id'
    Automatically saves report to database if user_id provided
    """
    label, confidence = predict_text(text)
    
    # Auto-save to database if user_id provided
    if user_id:
        auto_save_report(user_id, "text", label, confidence)
    
    return {"prediction": label, "confidence": confidence}
