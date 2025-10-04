import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self, remove_stopwords=True, lemmatize=True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        # Lemmatize if enabled
        if self.lemmatize:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Join tokens back into text
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text
    
    def process_dataframe(self, df, text_column='text'):
        # Create a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Apply text cleaning
        processed_df['cleaned_text'] = processed_df[text_column].apply(self.clean_text)
        
        return processed_df

class FeatureExtractor:
    def __init__(self, vectorizer_type='tfidf', ngram_range=(1, 2), max_features=5000):
        self.vectorizer_type = vectorizer_type
        self.ngram_range = ngram_range
        self.max_features = max_features
        
        if vectorizer_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
        elif vectorizer_type == 'count':
            self.vectorizer = CountVectorizer(ngram_range=ngram_range, max_features=max_features)
        else:
            raise ValueError("vectorizer_type must be 'tfidf' or 'count'")
    
    def extract_features(self, texts):
        return self.vectorizer.fit_transform(texts)
    
    def transform_texts(self, texts):
        return self.vectorizer.transform(texts)
    
    def get_feature_names(self):
        return self.vectorizer.get_feature_names_out()

def extract_linguistic_features(texts):
    """Extract additional linguistic features beyond bag-of-words"""
    features = []
    
    for text in texts:
        # Count sentences
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Average word length
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        # Count capital letters
        capital_count = sum(1 for char in text if char.isupper())
        
        # Count punctuation marks
        punctuation_count = sum(1 for char in text if char in '.,;:!?')
        
        # Count specific words that might indicate deception
        certainty_words = ['absolutely', 'definitely', 'certainly', 'always', 'never', 'every', 'all']
        certainty_count = sum(1 for word in words if word.lower() in certainty_words)
        
        # First-person pronouns
        first_person = sum(1 for word in words if word.lower() in ['i', 'me', 'my', 'mine', 'myself'])
        
        features.append({
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'capital_count': capital_count,
            'punctuation_count': punctuation_count,
            'certainty_words': certainty_count,
            'first_person_pronouns': first_person
        })
    
    return pd.DataFrame(features)

def prepare_dataset(csv_path, test_size=0.2, random_state=42):
    # Load the dataset
    df = pd.read_csv(csv_path)
    
    # Preprocess text
    preprocessor = TextPreprocessor(remove_stopwords=True, lemmatize=True)
    processed_df = preprocessor.process_dataframe(df)
    
    # Extract TF-IDF features
    feature_extractor = FeatureExtractor(vectorizer_type='tfidf', ngram_range=(1, 2), max_features=5000)
    X_tfidf = feature_extractor.extract_features(processed_df['cleaned_text'])
    
    # Extract linguistic features
    X_linguistic = extract_linguistic_features(df['text'])
    
    # Convert labels to numeric
    y = (processed_df['label'] == 'deceptive').astype(int)
    
    # Split the dataset
    X_train_tfidf, X_test_tfidf, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    X_train_linguistic, X_test_linguistic, _, _ = train_test_split(
        X_linguistic, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    return {
        'X_train_tfidf': X_train_tfidf,
        'X_test_tfidf': X_test_tfidf,
        'X_train_linguistic': X_train_linguistic,
        'X_test_linguistic': X_test_linguistic,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': feature_extractor.get_feature_names(),
        'preprocessor': preprocessor,
        'feature_extractor': feature_extractor
    }

if __name__ == "__main__":
    # Example usage
    dataset_path = 'deception_detection_dataset.csv'
    data = prepare_dataset(dataset_path)
    
    print(f"Dataset loaded and preprocessed successfully.")
    print(f"Training set size: {data['X_train_tfidf'].shape[0]} samples")
    print(f"Test set size: {data['X_test_tfidf'].shape[0]} samples")
    print(f"Number of features: {data['X_train_tfidf'].shape[1]} TF-IDF features, {data['X_train_linguistic'].shape[1]} linguistic features")