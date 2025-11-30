# VeriCloud - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Automatic Configuration
```bash
# Run the setup script (Python)
python setup.py

# Or on Linux/macOS
./setup.sh
```

This automatically creates all necessary environment files with local API URLs and paths.

### 2. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
pip install -r backend/Text/requirements.txt
pip install -r backend/Voice/requirements.txt
pip install -r backend/Face/requirements.txt
pip install -r backend/Fusion/requirements.txt
pip install -r backend/Database/requirements.txt
```

### 3. Start All Services

**Backend APIs (in separate terminals):**
```bash
# Text Analysis
cd backend/Text
uvicorn app:app --port 8000 --reload

# Voice Analysis  
cd backend/Voice
uvicorn app:app --port 8001 --reload

# Face Analysis
cd backend/Face
uvicorn app:app --port 8002 --reload

# Fusion Analysis
cd backend/Fusion
uvicorn app:app --port 8003 --reload

# Database API
cd backend/Database
uvicorn api:app --port 8004 --reload
```

**Frontend:**
```bash
cd frontend
npm start
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Text API: http://localhost:8000
- Voice API: http://localhost:8001
- Face API: http://localhost:8002
- Fusion API: http://localhost:8003
- Database API: http://localhost:8004

## 📁 Project Structure

```
VeriCloud/
├── frontend/                 # React frontend
│   ├── .env                 # Auto-generated environment variables
│   └── src/
├── backend/                  # Python FastAPI backend
│   ├── .env                 # Auto-generated environment variables
│   ├── Text/                # Text analysis API (port 8000)
│   ├── Voice/               # Voice analysis API (port 8001)
│   ├── Face/                # Face analysis API (port 8002)
│   ├── Fusion/              # Fusion API (port 8003)
│   └── Database/            # Database API (port 8004)
├── Voice model/             # Voice model files
├── Face model/              # Face model files
├── Text model/              # Text model files
├── setup.py                 # Python setup script
├── setup.sh                 # Bash setup script
└── QUICK_START.md          # This file
```

## 🔧 Environment Variables

The setup script creates these files automatically:

**frontend/.env:**
```env
REACT_APP_FACE_API_URL=http://127.0.0.1:8002
REACT_APP_VOICE_API_URL=http://127.0.0.1:8001
REACT_APP_TEXT_API_URL=http://127.0.0.1:8000
REACT_APP_FUSION_API_URL=http://127.0.0.1:8003
REACT_APP_DATABASE_API_URL=http://127.0.0.1:8004
```

**backend/.env:**
```env
PROJECT_ROOT=/path/to/VeriCloud
VOICE_MODEL_PATH=/path/to/VeriCloud/Voice model/src/models/model_final2.pth
FACE_MODEL_PATH=/path/to/VeriCloud/backend/models/face/effective_lie_detector_model.pkl
# ... other model paths
```

## 🎯 What Changed

### ✅ Fixed Issues:
- **Hardcoded paths** replaced with dynamic path resolution using `Path(__file__).parent`
- **Hardcoded API URLs** replaced with environment variables
- **Manual configuration** eliminated with automatic setup scripts

### 🔧 Technical Details:
- Backend uses `Path(__file__).parent.parent.parent` to find project root
- Frontend uses `process.env.REACT_APP_*_API_URL` with localhost fallbacks
- Setup scripts generate environment files automatically
- All paths are now relative to project root

## 🐛 Troubleshooting

**Model files missing?**
- Check if model files exist in the expected locations
- Download from S3 or train new models if needed

**Port conflicts?**
- Change ports in the uvicorn commands
- Update corresponding environment variables

**Environment not loading?**
- Ensure `.env` files exist in `frontend/` and `backend/` directories
- Restart services after changing environment variables

## 🌐 Production Deployment

For production, update the environment variables to point to your deployed APIs:

```env
# frontend/.env (production)
REACT_APP_FACE_API_URL=https://vericloud-face-s8zm.onrender.com
REACT_APP_VOICE_API_URL=https://vericloud-y9c9.onrender.com
REACT_APP_TEXT_API_URL=https://vericloud-text-tho9.onrender.com
REACT_APP_FUSION_API_URL=https://vericloud-fusion-xyz.onrender.com
REACT_APP_DATABASE_API_URL=https://vericloud-db-wbhv.onrender.com
```

## 📞 Support

If you encounter issues:
1. Run `python setup.py` to regenerate environment files
2. Check that all model files exist
3. Verify ports are not in use
4. Check the console output for error messages

---

**✅ Now users can clone the repo and run `python setup.py` for automatic configuration!**
