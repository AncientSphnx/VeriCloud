import os
import sys
import joblib
import pandas as pd
import boto3
import tempfile

# Add the Text model directory to the path
text_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Text model'))
if text_model_path not in sys.path:
    sys.path.insert(0, text_model_path)

from preprocess import TextPreprocessor, extract_linguistic_features
import scipy.sparse as sp
import numpy as np


# ----------------------------
# Download Model from S3
# ----------------------------
def download_model_from_s3(bucket, s3_model_key, s3_vectorizer_key):
    """
    Downloads model and vectorizer from AWS S3 to a temporary directory.
    Returns local file paths.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('S3_REGION')
    )
    print("AWS_ACCESS_KEY:", os.getenv('AWS_ACCESS_KEY'))
    print("AWS_SECRET_KEY:", os.getenv('AWS_SECRET_KEY'))
    print("S3_BUCKET_NAME:", os.getenv('S3_BUCKET_NAME'))
    print("TEXT_MODEL_KEY:", os.getenv('TEXT_MODEL_KEY'))

    tmp_dir = tempfile.mkdtemp()

    local_model_path = os.path.join(tmp_dir, os.path.basename(s3_model_key))
    local_vectorizer_path = os.path.join(tmp_dir, os.path.basename(s3_vectorizer_key))

    print(f"Downloading text model from s3://{bucket}/{s3_model_key}")
    s3.download_file(bucket, s3_model_key, local_model_path)

    print(f"Downloading vectorizer from s3://{bucket}/{s3_vectorizer_key}")
    s3.download_file(bucket, s3_vectorizer_key, local_vectorizer_path)

    return local_model_path, local_vectorizer_path


def load_model(model_name='logistic_regression'):
    """
    Load the trained deception detection model and its vectorizer from S3 or local.
    """
    
    model = None
    vectorizer = None
    
    # Try to load from S3 first
    try:
        bucket = os.getenv("S3_BUCKET_NAME")
        s3_model_key = os.getenv("TEXT_MODEL_KEY", "models/text/v1/ensemble_20251003_202351.pkl")
        s3_vectorizer_key = os.getenv("TEXT_VECTORIZER_KEY", "models/text/v1/vectorizer.pkl")
        
        model_path, vectorizer_path = download_model_from_s3(bucket, s3_model_key, s3_vectorizer_key)
        print("✅ Text model and vectorizer loaded successfully from S3.")
        
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        return model, vectorizer
        
    except Exception as e:
        print(f"⚠️ Failed to load model from S3: {e}")
    
    # Fallback to local
    try:
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Text model', 'models'))
        model_files = [f for f in os.listdir(model_dir) if f.startswith(model_name) and f.endswith('.pkl')]
        
        if not model_files:
            raise FileNotFoundError(f"No {model_name} model found in {model_dir}")
        
        # Get the most recent model file
        latest_model = sorted(model_files)[-1]
        model_path = os.path.join(model_dir, latest_model)
        print(f"Using local model: {model_path}")
        model = joblib.load(model_path)
        
        # Load vectorizer if available
        vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
        if os.path.exists(vectorizer_path):
            vectorizer = joblib.load(vectorizer_path)
        else:
            print("⚠️ Vectorizer not found. Using dummy features.")
            vectorizer = None
        
        return model, vectorizer
        
    except Exception as e:
        raise RuntimeError(f"❌ Text model not found locally or in S3: {e}")


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


def predict_text(text, threshold=0.50):
    """
    Predict deception (Truthful / Deceptive) for a given text.
    Returns label and confidence as a tuple.
    """
    model, vectorizer = load_model('logistic_regression')
    features = prepare_text(text, vectorizer)
    
    # Get probability for deceptive class
    deceptive_prob = model.predict_proba(features)[0][1] if hasattr(model, "predict_proba") else 0.0
    
    # Apply threshold (lowered from default 0.5 to 0.4)
    if deceptive_prob >= threshold:
        label = "Deceptive"
        confidence = deceptive_prob
    else:
        label = "Truthful"
        confidence = 1 - deceptive_prob
    
    return label, confidence


# Example usage
if __name__ == "__main__":
    test_text = input("Enter text to test for deception: ")
    label, confidence = predict_text(test_text)
    print(f"\nPrediction: {label} (Confidence: {confidence:.2f})")
