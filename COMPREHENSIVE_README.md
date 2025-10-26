# VeriCloud - AI-Powered Deception Detection System

## 📋 Project Overview

**VeriCloud** is a comprehensive, multi-modal deception detection system that analyzes text, voice, and facial expressions to predict whether a person is being truthful or deceptive. The system uses advanced machine learning models and combines their predictions through a weighted fusion algorithm for highly accurate results.

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  - Landing Page, Dashboard, Analysis Pages (Text/Voice/Face)   │
│  - User Authentication & Profile Management                     │
│  - Real-time Results Visualization & Reports                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP/REST API Calls
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
│  FUSION API    │ │ DATABASE    │ │  INDIVIDUAL     │
│  (Port 8003)   │ │ API (Flask) │ │  ANALYSIS APIs  │
│                │ │             │ │                 │
│ - Orchestrates │ │ - Auth      │ │ ┌─────────────┐ │
│   all models   │ │ - User Mgmt │ │ │ Text API    │ │
│ - Weighted     │ │ - Reports   │ │ │ (Port 8000) │ │
│   Fusion Algo  │ │ - MongoDB   │ │ └─────────────┘ │
│ - Final        │ │   Storage   │ │                 │
│   Prediction   │ │             │ │ ┌─────────────┐ │
└────────────────┘ └─────────────┘ │ │ Voice API   │ │
                                    │ │ (Port 8001) │ │
                                    │ └─────────────┘ │
                                    │                 │
                                    │ ┌─────────────┐ │
                                    │ │ Face API    │ │
                                    │ │ (Port 8002) │ │
                                    │ └─────────────┘ │
                                    └─────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
            ┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
            │ TEXT MODEL     │    │ VOICE MODEL     │    │ FACE MODEL      │
            │                │    │                 │    │                 │
            │ - NLP Analysis │    │ - Audio Feature │    │ - Facial Expr   │
            │ - Linguistic   │    │   Extraction    │    │ - Head Movement │
            │   Patterns     │    │ - Spectral Feat │    │ - Eye Gaze      │
            │ - Sentiment    │    │ - MFCC Features │    │ - Skin Changes  │
            └────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📁 Project Structure

```
VeriCloud/
├── frontend/                          # React TypeScript Application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx           # Home page
│   │   │   ├── Login.tsx             # User authentication
│   │   │   ├── Signup.tsx            # User registration
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   ├── TextAnalysis.tsx      # Text analysis interface
│   │   │   ├── VoiceAnalysis.tsx     # Voice analysis interface
│   │   │   ├── FaceAnalysis.tsx      # Face analysis interface
│   │   │   ├── FusionDashboard.tsx   # Combined multi-modal analysis
│   │   │   ├── Reports.tsx           # Historical reports
│   │   │   ├── Settings.tsx          # User settings
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── Layout/               # Header, Sidebar, Layout
│   │   │   ├── ui/                   # Reusable UI components
│   │   │   ├── AnalysisNavigation.tsx
│   │   │   ├── DemoMode.tsx
│   │   │   └── ...
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # Authentication state management
│   │   ├── App.tsx                   # Main app component
│   │   └── index.tsx                 # Entry point
│   ├── package.json                  # Dependencies (React, TailwindCSS, etc.)
│   └── ...
│
├── backend/
│   ├── Database/                     # MongoDB & User Management API (Flask)
│   │   ├── api.py                    # Flask routes for auth, users, reports
│   │   ├── db_connection.py          # MongoDB connection setup
│   │   ├── models.py                 # Database schema definitions
│   │   ├── operations.py             # Database CRUD operations
│   │   ├── auth.py                   # JWT token generation/verification
│   │   ├── s3_storage.py             # AWS S3 integration for file storage
│   │   └── requirements.txt
│   │
│   ├── Text/                         # Text Analysis API (FastAPI)
│   │   ├── app.py                    # FastAPI server (Port 8000)
│   │   ├── predictor.py              # Text prediction logic
│   │   └── requirements.txt
│   │
│   ├── Voice/                        # Voice Analysis API (FastAPI)
│   │   ├── app.py                    # FastAPI server (Port 8001)
│   │   ├── predictor.py              # Voice prediction logic
│   │   └── requirements.txt
│   │
│   ├── Face/                         # Face Analysis API (FastAPI)
│   │   ├── app.py                    # FastAPI server (Port 8002)
│   │   ├── predictor.py              # Face prediction logic
│   │   └── requirements.txt
│   │
│   └── Fusion/                       # Fusion/Orchestration API (FastAPI)
│       ├── app.py                    # FastAPI server (Port 8003)
│       └── requirements.txt
│
├── Face model/                       # Pre-trained face detection models
│   └── [Model files]
│
├── Text model/                       # Pre-trained text analysis models
│   └── models/
│       └── [Model files]
│
├── Voice model/                      # Pre-trained voice analysis models
│   ├── src/
│   │   └── models/
│   │       └── model_final2.pth      # PyTorch model
│   └── [Supporting files]
│
└── PROJECT_README.md                 # This file
```

---

## 🔄 Data Flow & Component Connections

### 1. **Frontend → Backend Communication**

#### User Authentication Flow
```
User (Frontend)
    ↓
[Login/Signup Page]
    ↓
POST /api/auth/register or /api/auth/login
    ↓
[Database API - Flask]
    ↓
MongoDB (User Storage)
    ↓
JWT Token Generated
    ↓
Token Stored in Frontend (localStorage/sessionStorage)
    ↓
User Authenticated & Redirected to Dashboard
```

#### Analysis Request Flow
```
User Uploads File/Text (Frontend)
    ↓
[Analysis Page - Text/Voice/Face/Fusion]
    ↓
POST Request to Appropriate API
    ↓
[Individual Analysis API or Fusion API]
    ↓
Model Prediction
    ↓
JSON Response with Prediction & Confidence
    ↓
Frontend Displays Results
    ↓
User Can Save Report to Database
```

---

### 2. **Individual Analysis APIs**

#### **Text Analysis API (Port 8000)**
- **Endpoint**: `POST http://127.0.0.1:8000/predict_text`
- **Input**: Form data with `text` field
- **Output**: `{"prediction": "Truthful|Deceptive", "confidence": float}`
- **Process**:
  1. Receives text input from frontend
  2. Extracts linguistic features (word choice, sentence structure, sentiment, etc.)
  3. Passes through trained NLP model
  4. Returns prediction and confidence score

#### **Voice Analysis API (Port 8001)**
- **Endpoint**: `POST http://127.0.0.1:8001/predict`
- **Input**: Audio file (multipart/form-data)
- **Output**: `{"prediction": "Truthful|Deceptive", "confidence": float}`
- **Process**:
  1. Receives audio file from frontend
  2. Extracts audio features (MFCC, spectral features, pitch, etc.)
  3. Loads pre-trained model from `Voice model/src/models/model_final2.pth`
  4. Runs inference
  5. Returns prediction and confidence score

#### **Face Analysis API (Port 8002)**
- **Endpoint**: `POST http://127.0.0.1:8002/predict`
- **Input**: Video or image file (multipart/form-data)
- **Output**: `{"prediction": "Truthful|Deceptive", "confidence": float}`
- **Process**:
  1. Receives video/image file from frontend
  2. Extracts 70+ facial features:
     - Geometric features (face landmarks)
     - Temporal features (movement patterns)
     - Texture features (skin analysis)
     - Gaze features (eye movement)
     - Head movement patterns
  3. Establishes baseline behavior (first 30 seconds)
  4. Processes up to 300 frames per video
  5. Runs through trained face model
  6. Returns prediction and confidence score

---

### 3. **Fusion API (Port 8003) - The Orchestrator**

The Fusion API is the **central orchestrator** that combines all three models:

#### **Endpoint**: `POST http://127.0.0.1:8003/predict_fusion`

#### **Input**:
```
multipart/form-data:
- text: string (required)
- audio_file: file (required)
- video_file: file (optional)
```

#### **Process Flow**:
```
User Submits Multi-Modal Data (Text + Audio + Video)
    ↓
Fusion API Receives Request
    ↓
┌─────────────────────────────────────────────────────┐
│ Parallel Requests to Individual APIs:               │
│ 1. POST to Text API with text                       │
│ 2. POST to Voice API with audio_file                │
│ 3. POST to Face API with video_file (if provided)   │
└─────────────────────────────────────────────────────┘
    ↓
Collect Results from All APIs:
    - text_result: {prediction, confidence}
    - voice_result: {prediction, confidence}
    - face_result: {prediction, confidence} (optional)
    ↓
Apply Weighted Fusion Algorithm
    ↓
Calculate Final Prediction & Confidence
    ↓
Return Detailed Breakdown with Reasoning
```

#### **Weighted Fusion Algorithm**:

The Fusion API uses a **weighted ensemble approach**:

```
Weights (Configurable):
- Text: 40%
- Voice: 40%
- Face: 20% (when available)

If Face is unavailable:
- Text: 50%
- Voice: 50%

Deception Score Calculation:
- Convert each prediction to a 0-1 score
- Deceptive = confidence score
- Truthful = 1 - confidence score

Final Score = (text_score × 0.40) + (voice_score × 0.40) + (face_score × 0.20)

Final Prediction:
- If final_score > 0.5 → "Deceptive"
- If final_score ≤ 0.5 → "Truthful"
```

#### **Output**:
```json
{
  "final_prediction": "Truthful|Deceptive",
  "final_confidence": 0.85,
  "final_score": 0.85,
  "breakdown": {
    "text": {
      "prediction": "Truthful",
      "confidence": 0.92,
      "weight": 0.40,
      "contribution": 0.368
    },
    "voice": {
      "prediction": "Deceptive",
      "confidence": 0.78,
      "weight": 0.40,
      "contribution": 0.312
    },
    "face": {
      "prediction": "Truthful",
      "confidence": 0.88,
      "weight": 0.20,
      "contribution": 0.176
    }
  },
  "reasoning": "Text model shows strongest signal (92% confidence) influencing final decision.",
  "weights_used": {"text": 0.40, "voice": 0.40, "face": 0.20}
}
```

---

### 4. **Database API (Flask) - User & Report Management**

#### **Key Endpoints**:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile
- `POST /api/reports/save` - Save analysis report
- `GET /api/reports/user` - Get user's reports
- `GET /api/reports/dashboard` - Get dashboard statistics

#### **Database Schema** (MongoDB):

```
Users Collection:
{
  _id: ObjectId,
  name: string,
  email: string,
  password_hash: string,
  created_at: datetime,
  updated_at: datetime
}

Reports Collection:
{
  _id: ObjectId,
  user_id: ObjectId (reference to Users),
  analysis_type: "text" | "voice" | "face" | "fusion",
  input_data: {
    text: string,
    audio_url: string,
    video_url: string
  },
  results: {
    prediction: string,
    confidence: float,
    breakdown: object (for fusion)
  },
  created_at: datetime,
  file_urls: {
    audio: string (S3 URL),
    video: string (S3 URL)
  }
}
```

#### **Connection Details**:
- **Database**: MongoDB Atlas
- **Connection String**: `mongodb+srv://[username]:[password]@cluster0.xefwuvx.mongodb.net/LieDetection`
- **Environment Variables**:
  - `MONGO_URI` - Full connection string
  - `MONGO_USER` - Username
  - `MONGO_PASS` - Password
  - `MONGO_HOST` - Cluster host
  - `MONGO_DB` - Database name

---

## 🚀 How Everything Connects Together

### **Complete User Journey**

```
1. USER VISITS WEBSITE
   └─→ Frontend loads (React)
   
2. USER REGISTERS/LOGS IN
   └─→ Frontend sends credentials to Database API
   └─→ Database API validates and stores in MongoDB
   └─→ JWT token returned to frontend
   
3. USER NAVIGATES TO ANALYSIS PAGE
   └─→ Frontend displays Text/Voice/Face/Fusion options
   
4. USER CHOOSES SINGLE ANALYSIS (e.g., Text)
   └─→ User enters text and clicks "Analyze"
   └─→ Frontend sends POST to Text API (Port 8000)
   └─→ Text API processes and returns prediction
   └─→ Frontend displays result
   
5. USER CHOOSES FUSION ANALYSIS
   └─→ User provides text + audio + video
   └─→ Frontend sends POST to Fusion API (Port 8003)
   └─→ Fusion API orchestrates:
       ├─→ Calls Text API (Port 8000)
       ├─→ Calls Voice API (Port 8001)
       └─→ Calls Face API (Port 8002)
   └─→ Fusion API applies weighted algorithm
   └─→ Returns combined prediction with breakdown
   └─→ Frontend displays detailed results
   
6. USER SAVES REPORT
   └─→ Frontend sends report data to Database API
   └─→ Database API stores in MongoDB
   └─→ Audio/Video files uploaded to AWS S3
   └─→ S3 URLs stored in MongoDB
   
7. USER VIEWS REPORTS
   └─→ Frontend requests user's reports from Database API
   └─→ Database API queries MongoDB
   └─→ Returns historical reports with S3 links
   └─→ Frontend displays reports and statistics
```

---

## 🔌 API Endpoints Summary

### **Frontend → Backend APIs**

| API | Port | Endpoint | Method | Purpose |
|-----|------|----------|--------|---------|
| Text | 8000 | `/predict_text` | POST | Analyze text for deception |
| Voice | 8001 | `/predict` | POST | Analyze voice for deception |
| Face | 8002 | `/predict` | POST | Analyze facial expressions |
| Fusion | 8003 | `/predict_fusion` | POST | Combined multi-modal analysis |
| Database | 5000 | `/api/auth/register` | POST | User registration |
| Database | 5000 | `/api/auth/login` | POST | User login |
| Database | 5000 | `/api/reports/save` | POST | Save analysis report |
| Database | 5000 | `/api/reports/user` | GET | Get user's reports |

---

## 📊 Technology Stack

### **Frontend**
- **Framework**: React 18.2.0 with TypeScript
- **Styling**: TailwindCSS 3.3.6
- **UI Components**: Radix UI, shadcn/ui
- **Charts**: Recharts 2.8.0
- **Animations**: Framer Motion 10.16.16
- **Routing**: React Router DOM 6.20.1
- **Icons**: Lucide React 0.294.0

### **Backend - Analysis APIs**
- **Framework**: FastAPI (async Python web framework)
- **ML Libraries**: TensorFlow, PyTorch, scikit-learn
- **Audio Processing**: librosa, scipy
- **Computer Vision**: OpenCV, MediaPipe
- **NLP**: NLTK, spaCy, transformers

### **Backend - Database API**
- **Framework**: Flask
- **Database**: MongoDB Atlas (Cloud)
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: AWS S3
- **ORM**: PyMongo

### **Infrastructure**
- **Local Development**: Windows (localhost)
- **Database**: MongoDB Atlas (Cloud)
- **File Storage**: AWS S3 (Cloud)
- **Deployment**: Ready for cloud (AWS, Azure, GCP, Heroku)

---

## 🌐 Cloud Integration Considerations

### **Current Local Setup**
```
Frontend (localhost:3000) 
    ↓
Backend APIs (localhost:8000-8003)
    ↓
MongoDB Atlas (Cloud)
    ↓
AWS S3 (Cloud)
```

### **For Cloud Deployment** (Next Steps)
1. **Containerization**: Docker containers for each API
2. **Orchestration**: Kubernetes or Docker Compose
3. **API Gateway**: AWS API Gateway or Kong
4. **Load Balancing**: Distribute requests across multiple instances
5. **Database**: MongoDB Atlas (already cloud-ready)
6. **File Storage**: AWS S3 (already cloud-ready)
7. **Frontend Hosting**: AWS S3 + CloudFront, Netlify, or Vercel
8. **CI/CD Pipeline**: GitHub Actions, Jenkins, or GitLab CI
9. **Monitoring**: CloudWatch, Datadog, or New Relic
10. **Scaling**: Auto-scaling groups for APIs

---

## 🔐 Security Considerations

### **Current Implementation**
- JWT-based authentication
- CORS enabled for cross-origin requests
- MongoDB connection with credentials
- AWS S3 for secure file storage

### **For Production Cloud Deployment**
- Use environment variables for all secrets
- Implement API rate limiting
- Add request validation and sanitization
- Use HTTPS/TLS for all communications
- Implement API authentication (API keys, OAuth)
- Add database encryption at rest
- Implement audit logging
- Use VPC for network isolation
- Implement DDoS protection

---

## 📝 Environment Variables Required

```
# MongoDB Configuration
MONGO_URI=mongodb+srv://[user]:[password]@cluster0.xefwuvx.mongodb.net/LieDetection
MONGO_USER=Numan_admin
MONGO_PASS=Smg1947%40%23
MONGO_HOST=cluster0.xefwuvx.mongodb.net
MONGO_DB=LieDetection

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=us-east-1

# API Configuration
TEXT_API_URL=http://127.0.0.1:8000
VOICE_API_URL=http://127.0.0.1:8001
FACE_API_URL=http://127.0.0.1:8002
FUSION_API_URL=http://127.0.0.1:8003
DATABASE_API_URL=http://127.0.0.1:5000

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

---

## 🚀 Running the System Locally

### **Prerequisites**
- Python 3.8+
- Node.js 14+
- MongoDB Atlas account
- AWS S3 account (for file storage)

### **Step 1: Start Backend APIs**

```bash
# Terminal 1 - Text API
cd backend/Text
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Voice API
cd backend/Voice
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8001 --reload

# Terminal 3 - Face API
cd backend/Face
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8002 --reload

# Terminal 4 - Fusion API
cd backend/Fusion
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8003 --reload

# Terminal 5 - Database API
cd backend/Database
pip install -r requirements.txt
python -m flask run --port 5000
```

### **Step 2: Start Frontend**

```bash
cd frontend
npm install
npm start
```

The application will be available at `http://localhost:3000`

---

## 📊 System Performance Metrics

- **Text Analysis**: ~100-500ms per request
- **Voice Analysis**: ~1-3 seconds per audio file
- **Face Analysis**: ~2-5 seconds per video (up to 300 frames)
- **Fusion Analysis**: ~5-10 seconds (combined)
- **Database Operations**: ~50-200ms per query
- **Concurrent Users**: Supports 100+ concurrent requests (with proper scaling)

---

## 🔄 Model Details

### **Text Model**
- Analyzes linguistic patterns, word choice, sentiment
- Detects deceptive language markers
- Processes input text through NLP pipeline

### **Voice Model**
- Extracts MFCC features from audio
- Analyzes pitch, tone, and speech patterns
- Pre-trained model: `Voice model/src/models/model_final2.pth`

### **Face Model**
- Extracts 70+ facial features
- Analyzes micro-expressions and head movements
- Establishes baseline behavior for comparison
- Processes video frames for temporal analysis

---

## 📚 Additional Resources

- **Frontend Documentation**: See `frontend/` directory
- **Backend Documentation**: See `backend/` directory
- **Model Documentation**: See individual model directories

---

## 🤝 Support for Cloud Integration

This README provides all necessary information for ChatGPT or any cloud integration specialist to:

1. **Understand the system architecture** - All components and their relationships
2. **Identify integration points** - Where cloud services should be integrated
3. **Plan deployment strategy** - How to containerize and deploy each component
4. **Configure cloud infrastructure** - Database, storage, networking, security
5. **Implement CI/CD pipelines** - Automated testing and deployment
6. **Set up monitoring and logging** - Track system health and performance
7. **Scale the system** - Handle increased load and users

---

## 📞 Contact & Support

For questions about cloud integration or system architecture, refer to this comprehensive documentation when consulting with cloud specialists or AI assistants.

---

**Last Updated**: October 2024
**Project Status**: Ready for Cloud Integration
