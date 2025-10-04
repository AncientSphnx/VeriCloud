import os
import sys
import joblib
import pandas as pd

# Add the Text model directory to the path
text_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Text model'))
if text_model_path not in sys.path:
    sys.path.insert(0, text_model_path)

from preprocess import TextPreprocessor, extract_linguistic_features
import scipy.sparse as sp
import numpy as np

def load_model(model_name='logistic_regression'):
    """
    Load the trained deception detection model and its vectorizer.
    """
    # Path to models directory in Text model folder
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Text model', 'models'))
    model_files = [f for f in os.listdir(model_dir) if f.startswith(model_name) and f.endswith('.pkl')]
    
    if not model_files:
        raise FileNotFoundError(f"No {model_name} model found in {model_dir}")
    
    # Get the most recent model file
    latest_model = sorted(model_files)[-1]
    model_path = os.path.join(model_dir, latest_model)
    print(f"Loading model: {model_path}")
    model = joblib.load(model_path)
    
    # Load vectorizer if available
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
    if os.path.exists(vectorizer_path):
        vectorizer = joblib.load(vectorizer_path)
    else:
        print("⚠️ Vectorizer not found. Using dummy features.")
        vectorizer = None
    
    return model, vectorizer


def prepare_text(text, vectorizer=None):
    """
    Preprocess and extract features from the input text.
    """
    preprocessor = TextPreprocessor()
    cleaned_text = preprocessor.clean_text(text)

    # TF-IDF features
    if vectorizer:
        tfidf_features = vectorizer.transform([cleaned_text])
    else:
        tfidf_features = sp.csr_matrix((1, 1))  # Dummy placeholder
    
    # Linguistic features
    linguistic_features = extract_linguistic_features(pd.Series([text]))

    # Combine both (if applicable)
    try:
        X_combined = sp.hstack([tfidf_features, linguistic_features])
    except Exception:
        # Fallback if dimensions mismatch
        X_combined = tfidf_features
    
    return X_combined


def predict_text(text):
    """
    Predict deception (Truthful / Deceptive) for a given text.
    Returns label and confidence as a tuple.
    """
    model, vectorizer = load_model('logistic_regression')
    features = prepare_text(text, vectorizer)
    
    # Make prediction
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1] if hasattr(model, "predict_proba") else None

    label = "Deceptive" if prediction == 1 else "Truthful"
    confidence = float(probability) if probability is not None else 0.0
    return label, confidence


# Example usage
if __name__ == "__main__":
    test_text = input("Enter text to test for deception: ")
    label, confidence = predict_text(test_text)
    print(f"\nPrediction: {label} (Confidence: {confidence:.2f})")
