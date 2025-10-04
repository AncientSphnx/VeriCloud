import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_auc_score, roc_curve
import joblib

class DeceptionDetectionModel:
    def __init__(self, model_type='logistic_regression', use_linguistic_features=True):
        self.model_type = model_type
        self.use_linguistic_features = use_linguistic_features
        self.model = self._create_model()
        self.is_fitted = False
    
    def _create_model(self):
        if self.model_type == 'logistic_regression':
            return LogisticRegression(max_iter=1000, class_weight='balanced')
        elif self.model_type == 'random_forest':
            return RandomForestClassifier(n_estimators=100, class_weight='balanced')
        elif self.model_type == 'gradient_boosting':
            return GradientBoostingClassifier(n_estimators=100)
        elif self.model_type == 'svm':
            return SVC(kernel='linear', probability=True, class_weight='balanced')
        elif self.model_type == 'naive_bayes':
            return MultinomialNB()
        elif self.model_type == 'neural_network':
            return MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _combine_features(self, X_tfidf, X_linguistic=None):
        if self.use_linguistic_features and X_linguistic is not None:
            # Convert linguistic features to sparse matrix for compatibility with TF-IDF
            X_linguistic_sparse = X_linguistic.astype(np.float32).values
            return hstack([X_tfidf, X_linguistic_sparse])
        else:
            return X_tfidf
    
    def fit(self, X_tfidf, y, X_linguistic=None):
        X = self._combine_features(X_tfidf, X_linguistic)
        self.model.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X_tfidf, X_linguistic=None):
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        X = self._combine_features(X_tfidf, X_linguistic)
        return self.model.predict(X)
    
    def predict_proba(self, X_tfidf, X_linguistic=None):
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        X = self._combine_features(X_tfidf, X_linguistic)
        return self.model.predict_proba(X)
    
    def cross_validate(self, X_tfidf, y, X_linguistic=None, cv=5):
        X = self._combine_features(X_tfidf, X_linguistic)
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
        return scores
    
    def save_model(self, filepath):
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        joblib.dump(self, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        return joblib.load(filepath)

def tune_hyperparameters(model_type, X_tfidf, y, X_linguistic=None, use_linguistic_features=True):
    """Perform hyperparameter tuning for the specified model type"""
    X = X_tfidf
    if use_linguistic_features and X_linguistic is not None:
        X_linguistic_sparse = X_linguistic.astype(np.float32).values
        X = hstack([X_tfidf, X_linguistic_sparse])
    
    param_grid = {}
    
    if model_type == 'logistic_regression':
        model = LogisticRegression(max_iter=1000, class_weight='balanced')
        param_grid = {
            'C': [0.01, 0.1, 1, 10, 100],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }
    elif model_type == 'random_forest':
        model = RandomForestClassifier(class_weight='balanced')
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    elif model_type == 'gradient_boosting':
        model = GradientBoostingClassifier()
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10]
        }
    elif model_type == 'svm':
        model = SVC(probability=True, class_weight='balanced')
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto', 0.1, 0.01]
        }
    elif model_type == 'naive_bayes':
        model = MultinomialNB()
        param_grid = {
            'alpha': [0.01, 0.1, 0.5, 1.0, 2.0]
        }
    elif model_type == 'neural_network':
        model = MLPClassifier(max_iter=1000)
        param_grid = {
            'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive']
        }
    else:
        raise ValueError(f"Unsupported model type for tuning: {model_type}")
    
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1', n_jobs=-1)
    grid_search.fit(X, y)
    
    print(f"Best parameters for {model_type}: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_, grid_search.best_params_, grid_search.best_score_

def train_ensemble_model(models_list, X_tfidf, y, X_linguistic=None, use_linguistic_features=True):
    """Train an ensemble of models and use majority voting for prediction"""
    trained_models = []
    
    for model_type in models_list:
        model = DeceptionDetectionModel(model_type=model_type, use_linguistic_features=use_linguistic_features)
        model.fit(X_tfidf, y, X_linguistic)
        trained_models.append(model)
    
    return EnsembleModel(trained_models, use_linguistic_features)

class EnsembleModel:
    def __init__(self, models, use_linguistic_features=True):
        self.models = models
        self.use_linguistic_features = use_linguistic_features
    
    def predict(self, X_tfidf, X_linguistic=None):
        predictions = []
        
        for model in self.models:
            pred = model.predict(X_tfidf, X_linguistic)
            predictions.append(pred)
        
        # Stack predictions and take majority vote
        stacked_preds = np.column_stack(predictions)
        final_pred = np.apply_along_axis(
            lambda x: np.argmax(np.bincount(x)), 
            axis=1, 
            arr=stacked_preds
        )
        
        return final_pred
    
    def predict_proba(self, X_tfidf, X_linguistic=None):
        probas = []
        
        for model in self.models:
            prob = model.predict_proba(X_tfidf, X_linguistic)
            probas.append(prob)
        
        # Average the probabilities
        avg_proba = np.mean(probas, axis=0)
        
        return avg_proba

def train_all_models(data):
    """Train all model types and return a dictionary of trained models"""
    model_types = [
        'logistic_regression',
        'random_forest',
        'gradient_boosting',
        'svm',
        'naive_bayes',
        'neural_network'
    ]
    
    trained_models = {}
    
    for model_type in model_types:
        print(f"Training {model_type} model...")
        model = DeceptionDetectionModel(model_type=model_type, use_linguistic_features=True)
        model.fit(
            data['X_train_tfidf'], 
            data['y_train'], 
            data['X_train_linguistic']
        )
        trained_models[model_type] = model
    
    # Also train an ensemble model
    print("Training ensemble model...")
    ensemble = train_ensemble_model(
        model_types,
        data['X_train_tfidf'],
        data['y_train'],
        data['X_train_linguistic']
    )
    trained_models['ensemble'] = ensemble
    
    return trained_models

if __name__ == "__main__":
    from preprocess import prepare_dataset
    
    # Load and preprocess the dataset
    dataset_path = 'deception_detection_dataset.csv'
    data = prepare_dataset(dataset_path)
    
    # Train a logistic regression model as an example
    model = DeceptionDetectionModel(model_type='logistic_regression', use_linguistic_features=True)
    model.fit(
        data['X_train_tfidf'], 
        data['y_train'], 
        data['X_train_linguistic']
    )
    
    # Make predictions
    y_pred = model.predict(
        data['X_test_tfidf'], 
        data['X_test_linguistic']
    )
    
    # Print accuracy
    accuracy = accuracy_score(data['y_test'], y_pred)
    print(f"Logistic Regression Accuracy: {accuracy:.4f}")