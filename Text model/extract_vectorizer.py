import os
import pickle
import joblib
from preprocess import prepare_dataset

def extract_and_save_vectorizer():
    # Load the dataset to get the feature_extractor
    print("Loading dataset to extract vectorizer...")
    dataset_path = 'deception_detection_dataset.csv'
    data = prepare_dataset(dataset_path)
    
    # Extract the vectorizer from the feature_extractor
    vectorizer = data['feature_extractor'].vectorizer
    
    # Save the vectorizer
    vectorizer_path = os.path.join('models', 'vectorizer.pkl')
    print(f"Saving vectorizer to {vectorizer_path}")
    joblib.dump(vectorizer, vectorizer_path)
    print("Vectorizer saved successfully!")

if __name__ == "__main__":
    extract_and_save_vectorizer()