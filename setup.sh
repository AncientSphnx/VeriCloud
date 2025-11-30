#!/bin/bash

# VeriCloud Setup Script (Linux/macOS)
# Automatically configures environment files for local development

echo "🚀 VeriCloud Setup Script"
echo "=========================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create frontend .env
echo ""
echo "📁 Setting up frontend environment..."
FRONTEND_ENV="$PROJECT_ROOT/frontend/.env"

if [ -f "$FRONTEND_ENV" ]; then
    echo "⚠️  $FRONTEND_ENV already exists. Skipping creation."
else
    cat > "$FRONTEND_ENV" << EOF
# Local Development API URLs
REACT_APP_FACE_API_URL=http://127.0.0.1:8002
REACT_APP_VOICE_API_URL=http://127.0.0.1:8001
REACT_APP_TEXT_API_URL=http://127.0.0.1:8000
REACT_APP_FUSION_API_URL=http://127.0.0.1:8003
REACT_APP_DATABASE_API_URL=http://127.0.0.1:8004
EOF
    echo "✅ Created $FRONTEND_ENV"
fi

# Create backend .env
echo ""
echo "📁 Setting up backend environment..."
BACKEND_ENV="$PROJECT_ROOT/backend/.env"

if [ -f "$BACKEND_ENV" ]; then
    echo "⚠️  $BACKEND_ENV already exists. Skipping creation."
else
    cat > "$BACKEND_ENV" << EOF
# Local Development Configuration
PROJECT_ROOT=$PROJECT_ROOT

# Model Paths (relative to project root)
VOICE_MODEL_PATH=$PROJECT_ROOT/Voice model/src/models/model_final2.pth
FACE_MODEL_PATH=$PROJECT_ROOT/backend/models/face/effective_lie_detector_model.pkl
FACE_SCALER_PATH=$PROJECT_ROOT/backend/models/face/effective_feature_scaler.pkl
TEXT_MODEL_PATH=$PROJECT_ROOT/backend/models/text/logistic_regression.pkl
TEXT_VECTORIZER_PATH=$PROJECT_ROOT/backend/models/text/vectorizer.pkl

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/vericloud

# AWS S3 Configuration (optional - for production)
# AWS_S3_BUCKET=your-bucket-name
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_REGION=us-east-1
EOF
    echo "✅ Created $BACKEND_ENV"
fi

# Verify model paths
echo ""
echo "🔍 Checking model files..."
MISSING_FILES=0

check_model() {
    local model_path="$1"
    local full_path="$PROJECT_ROOT/$model_path"
    
    if [ -f "$full_path" ]; then
        echo "✅ $model_path"
    else
        echo "❌ $model_path (missing)"
        ((MISSING_FILES++))
    fi
}

check_model "Voice model/src/models/model_final2.pth"
check_model "backend/models/face/effective_lie_detector_model.pkl"
check_model "backend/models/face/effective_feature_scaler.pkl"
check_model "backend/models/text/logistic_regression.pkl"
check_model "backend/models/text/vectorizer.pkl"

if [ $MISSING_FILES -eq 0 ]; then
    echo ""
    echo "✅ All model files found!"
else
    echo ""
    echo "⚠️  $MISSING_FILES model files missing. Some features may not work."
fi

# Summary
echo ""
echo "=========================="
echo "📋 Setup Summary:"
echo "   Frontend .env: ✅"
echo "   Backend .env:  ✅"
if [ $MISSING_FILES -eq 0 ]; then
    echo "   Model files:   ✅"
else
    echo "   Model files:   ⚠️"
fi

echo ""
echo "🎯 Next Steps:"
echo "   1. Install dependencies:"
echo "      - Frontend: cd frontend && npm install"
echo "      - Backend: pip install -r backend/*/requirements.txt"
echo "   2. Start backend APIs:"
echo "      - Text: cd backend/Text && uvicorn app:app --port 8000"
echo "      - Voice: cd backend/Voice && uvicorn app:app --port 8001" 
echo "      - Face: cd backend/Face && uvicorn app:app --port 8002"
echo "      - Fusion: cd backend/Fusion && uvicorn app:app --port 8003"
echo "      - Database: cd backend/Database && uvicorn api:app --port 8004"
echo "   3. Start frontend:"
echo "      - cd frontend && npm start"

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "⚠️  Note: Some model files are missing. You may need to:"
    echo "   - Download models from S3 (if configured)"
    echo "   - Train models using the training scripts"
    echo "   - Copy models from backup location"
fi

echo ""
echo "✅ Setup complete!"
