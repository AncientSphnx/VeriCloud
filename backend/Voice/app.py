from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from predictor import predict
import requests
import os

MODEL_PATH = r"C:\Users\91829\OneDrive\Desktop\VeriCloud\Voice model\src\models\model_final2.pth"  # adjust path if needed

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

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...), user_id: str = Form(None)):
    """
    API endpoint to analyze voice and predict deception.
    Expects file upload and optional user_id.
    Automatically saves report to database if user_id provided.
    """
    # save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # run prediction
        label, confidence = predict(tmp_path, MODEL_PATH)
        
        # Auto-save to database if user_id provided
        if user_id:
            auto_save_report(user_id, "voice", label, confidence)
        
        return {"prediction": label, "confidence": confidence}
    
    finally:
        os.remove(tmp_path)
