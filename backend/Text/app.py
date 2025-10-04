from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from predictor import predict_text  # your text prediction function

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict_text")
async def predict_text_endpoint(text: str = Form(...)):
    """
    API endpoint to analyze text and predict deception.
    Expects form-data with a field named 'text'
    """
    label, confidence = predict_text(text)
    return {"prediction": label, "confidence": confidence}
