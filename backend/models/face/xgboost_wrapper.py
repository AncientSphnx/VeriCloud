
import xgboost as xgb
import numpy as np

class XGBoostModelWrapper:
    """Wrapper that loads XGBoost model from UBJ format."""
    
    def __init__(self, ubj_path):
        self.ubj_path = ubj_path
        self.booster = None
        self._load_model()
    
    def _load_model(self):
        """Load model from UBJ file."""
        self.booster = xgb.Booster()
        self.booster.load_model(self.ubj_path)
    
    def predict(self, X):
        """Make predictions."""
        dmatrix = xgb.DMatrix(X)
        return self.booster.predict(dmatrix)
    
    def predict_proba(self, X):
        """Get prediction probabilities."""
        dmatrix = xgb.DMatrix(X)
        proba = self.booster.predict(dmatrix)
        # Convert to probabilities if needed
        if len(proba.shape) == 1:
            # Binary classification
            neg_proba = 1 - proba
            return np.column_stack([neg_proba, proba])
        return proba
    
    def __getstate__(self):
        """For pickling."""
        return {'ubj_path': self.ubj_path}
    
    def __setstate__(self, state):
        """For unpickling."""
        self.ubj_path = state['ubj_path']
        self._load_model()
