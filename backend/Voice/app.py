from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from predictor import predict

MODEL_PATH = r"C:\Users\91829\OneDrive\Desktop\Lie Detector (MAIN)\Voice model\src\models\model_final2.pth"  # adjust path if needed

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    # save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # run prediction
    label, confidence = predict(tmp_path, MODEL_PATH)

    os.remove(tmp_path)

    return {"prediction": label, "confidence": confidence}
