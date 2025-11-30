#!/usr/bin/env python3
"""
VeriCloud Setup Script
Automatically configures environment files for local development
"""

import os
import sys
from pathlib import Path

def create_frontend_env():
    """Create .env file for frontend with local API URLs"""
    frontend_dir = Path(__file__).parent / "frontend"
    env_file = frontend_dir / ".env"
    
    env_content = """# Local Development API URLs
REACT_APP_FACE_API_URL=http://127.0.0.1:8002
REACT_APP_VOICE_API_URL=http://127.0.0.1:8001
REACT_APP_TEXT_API_URL=http://127.0.0.1:8000
REACT_APP_FUSION_API_URL=http://127.0.0.1:8003
REACT_APP_DATABASE_API_URL=http://127.0.0.1:8004
"""
    
    if env_file.exists():
        print(f"⚠️  {env_file} already exists. Skipping creation.")
        return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def create_backend_env():
    """Create .env file for backend with local paths"""
    backend_dir = Path(__file__).parent / "backend"
    env_file = backend_dir / ".env"
    
    project_root = Path(__file__).parent
    
    env_content = f"""# Local Development Configuration
PROJECT_ROOT={project_root}

# Model Paths (relative to project root)
VOICE_MODEL_PATH={project_root}/Voice model/src/models/model_final2.pth
FACE_MODEL_PATH={project_root}/backend/models/face/effective_lie_detector_model.pkl
FACE_SCALER_PATH={project_root}/backend/models/face/effective_feature_scaler.pkl
TEXT_MODEL_PATH={project_root}/backend/models/text/logistic_regression.pkl
TEXT_VECTORIZER_PATH={project_root}/backend/models/text/vectorizer.pkl

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/vericloud

# AWS S3 Configuration (optional - for production)
# AWS_S3_BUCKET=your-bucket-name
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_REGION=us-east-1
"""
    
    if env_file.exists():
        print(f"⚠️  {env_file} already exists. Skipping creation.")
        return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def verify_model_paths():
    """Verify that model files exist"""
    project_root = Path(__file__).parent
    
    model_paths = [
        "Voice model/src/models/model_final2.pth",
        "backend/models/face/effective_lie_detector_model.pkl",
        "backend/models/face/effective_feature_scaler.pkl",
        "backend/models/text/logistic_regression.pkl",
        "backend/models/text/vectorizer.pkl"
    ]
    
    print("\n🔍 Checking model files...")
    missing_files = []
    
    for model_path in model_paths:
        full_path = project_root / model_path
        if full_path.exists():
            print(f"✅ {model_path}")
        else:
            print(f"❌ {model_path} (missing)")
            missing_files.append(model_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} model files missing. Some features may not work.")
        return False
    else:
        print("\n✅ All model files found!")
        return True

def main():
    """Main setup function"""
    print("🚀 VeriCloud Setup Script")
    print("=" * 50)
    
    # Create frontend .env
    print("\n📁 Setting up frontend environment...")
    frontend_ok = create_frontend_env()
    
    # Create backend .env  
    print("\n📁 Setting up backend environment...")
    backend_ok = create_backend_env()
    
    # Verify model paths
    models_ok = verify_model_paths()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"   Frontend .env: {'✅' if frontend_ok else '⚠️'}")
    print(f"   Backend .env:  {'✅' if backend_ok else '⚠️'}")
    print(f"   Model files:   {'✅' if models_ok else '⚠️'}")
    
    print("\n🎯 Next Steps:")
    print("   1. Install dependencies:")
    print("      - Frontend: cd frontend && npm install")
    print("      - Backend: pip install -r backend/*/requirements.txt")
    print("   2. Start backend APIs:")
    print("      - Text: cd backend/Text && uvicorn app:app --port 8000")
    print("      - Voice: cd backend/Voice && uvicorn app:app --port 8001") 
    print("      - Face: cd backend/Face && uvicorn app:app --port 8002")
    print("      - Fusion: cd backend/Fusion && uvicorn app:app --port 8003")
    print("      - Database: cd backend/Database && uvicorn api:app --port 8004")
    print("   3. Start frontend:")
    print("      - cd frontend && npm start")
    
    if not models_ok:
        print("\n⚠️  Note: Some model files are missing. You may need to:")
        print("   - Download models from S3 (if configured)")
        print("   - Train models using the training scripts")
        print("   - Copy models from backup location")

if __name__ == "__main__":
    main()
