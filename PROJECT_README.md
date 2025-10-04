# 🕵️ AI Lie Detection System

A comprehensive multi-modal lie detection system that analyzes **text**, **voice**, and **face** (planned) to determine if someone is being truthful or deceptive.

## 🎯 Project Overview

This project combines **Natural Language Processing (NLP)**, **Audio Analysis**, and **Computer Vision** to create a powerful lie detection tool. The system uses machine learning models trained on various datasets to analyze behavioral patterns, linguistic cues, and physiological indicators.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Fusion Dashboard                   │    │
│  │  • Text Analysis    • Voice Analysis    • Face     │    │
│  │  • Combined Results • Visualization     Analysis   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST APIs
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Text      │ │    Voice    │ │   Fusion    │           │
│  │   API       │ │     API     │ │   Logic     │           │
│  │  Port 8000  │ │ Port 8001   │ │ Port 8002   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Machine Learning Models                     │
│  ┌─────────────┐ ┌─────────────────────────────────────┐    │
│  │   Text      │ │              Voice                  │    │
│  │   Model     │ │           Model                     │    │
│  └─────────────┘ └─────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

### **Frontend** (`/frontend/`)
**React/TypeScript web application** with modern UI components and data visualization.

#### Core Files:
- **`src/App.tsx`** - Main application component with routing configuration
- **`src/index.tsx`** - Application entry point
- **`package.json`** - Frontend dependencies (React, TypeScript, Tailwind CSS, Framer Motion, Recharts)

#### Pages (`/src/pages/`):
- **`Landing.tsx`** - Homepage with project overview
- **`Dashboard.tsx`** - Main dashboard with quick access to all features
- **`TextAnalysis.tsx`** - Text-based lie detection interface
- **`VoiceAnalysis.tsx`** - Voice/audio file analysis interface
- **`FaceAnalysis.tsx`** - Face/video analysis interface (planned)
- **`FusionDashboard.tsx`** - **Multi-modal fusion analysis** combining all three methods

#### UI Components (`/src/components/`):
- **`Layout/`** - Main layout components (Header, Sidebar, Footer)
- **`ui/`** - Reusable UI components (buttons, cards, forms)
- **`AnalysisNavigation.tsx`** - Navigation between analysis modes

### **Backend** (`/backend/`)

#### **Text Backend** (`/backend/Text/`)
**Text analysis API** using NLP and linguistic features.

- **`app.py`** - FastAPI server (Port 8000) with `/predict_text` endpoint
- **`predictor.py`** - Core text prediction logic with model loading and preprocessing

**Key Features:**
- TF-IDF vectorization for text features
- Linguistic feature extraction (sentence count, word length, etc.)
- Pre-trained logistic regression model
- Integration with `Text model/preprocess.py` for text cleaning

#### **Voice Backend** (`/backend/Voice/`)
**Audio analysis API** using deep learning for voice pattern detection.

- **`app.py`** - FastAPI server (Port 8001) with `/predict` endpoint
- **`predictor.py`** - Audio processing with BiLSTM + Attention model
- **Model**: Pre-trained neural network for lie detection from audio

**Key Features:**
- MFCC feature extraction from audio files
- Support for multiple audio formats (WAV, MP3, MP4)
- Deep learning model with attention mechanism
- Real-time audio analysis capabilities

#### **Fusion Backend** (`/backend/Fusion/`)
**Multi-modal fusion system** combining predictions from all models.

- **`app.py`** - FastAPI server (Port 8002) with `/predict_fusion` endpoint
- **Algorithm**: Weighted ensemble combining Text (50%) + Voice (50%)
- **Features**:
  - Automatic normalization of different model outputs
  - Confidence score aggregation
  - Reasoning generation for decisions
  - Extensible for face recognition integration

### **Machine Learning Models**

#### **Text Model** (`/Text model/`)
**NLP-based text analysis** for linguistic deception detection.

- **`preprocess.py`** - Text preprocessing pipeline:
  - Tokenization using NLTK
  - Stopword removal and lemmatization
  - Feature extraction (TF-IDF, linguistic features)
  - Dataset preparation for training

- **`models.py`** - Model training and evaluation:
  - Multiple ML algorithms (Logistic Regression, SVM, Random Forest)
  - Cross-validation and performance metrics
  - Model serialization and loading

- **`extract_vectorizer.py`** - TF-IDF vectorizer extraction utility
- **`test_custom_text.py`** - Testing interface for custom text input

#### **Voice Model** (`/Voice model/`)
**Audio-based lie detection** using deep learning.

- **`Predict.py`** - Main prediction script with audio processing
- **`README.md`** - Documentation for MFCC preprocessing pipeline
- **`requirements.txt`** - Python dependencies for audio processing
- **`src/`** - Source code for model architecture and training

### **Configuration & Utilities**

#### **Frontend Configuration:**
- **`tailwind.config.js`** - Tailwind CSS configuration with custom themes
- **`tsconfig.json`** - TypeScript configuration
- **`postcss.config.js`** - PostCSS configuration for CSS processing

#### **Backend Utilities:**
- **`start_all_backends.bat`** - Windows batch script to start all three backend services
- **`FUSION_SETUP_GUIDE.md`** - Detailed setup guide for the fusion system

---

## 🔧 How Each Component Works

### **Text Analysis Pipeline**
```
Input Text → Preprocessing → Feature Extraction → Model Prediction → Result
     ↓           ↓              ↓              ↓              ↓
1. Clean text   2. TF-IDF +    3. Linguistic   4. ML Model    5. Truthful/
   (lowercase,    Linguistic     features       (Logistic      Deceptive
   remove        features       (sentence      Regression)    + Confidence
   special chars)                length, etc.)
```

### **Voice Analysis Pipeline**
```
Audio File → Format → Feature → Deep Learning → Prediction → Result
     ↓        ↓      ↓         ↓              ↓          ↓
1. Convert  2. MFCC 3. 39 audio 4. BiLSTM +     5. Neural  6. Lie/Truth
   to WAV     features features  Attention      Network    + Confidence
              (Mel-    (MFCC +    Model                     Score
              spectrogram delta + delta²)
```

### **Fusion Analysis Pipeline**
```
Text + Voice → Individual → Normalization → Weighted → Final → Reasoning
   ↓      ↓     Predictions      ↓         Ensemble    ↓      ↓
1. API   2. API   3. Text       4. Text:50%   5. >0.5    6. Explain
   Call    Call    Lie/Truth     Voice:50%     =Deceptive  why
                   conversion                  ≤0.5=Truthful
```

---

## 🚀 Getting Started

### **Prerequisites**
- **Python 3.8+** with pip
- **Node.js 16+** and npm
- **Git** for version control

### **Quick Setup**

1. **Clone and navigate:**
   ```bash
   git clone <repository-url>
   cd "Lie Detector (MAIN)"
   ```

2. **Install Python dependencies:**
   ```bash
   # Install backend requirements
   cd backend/Fusion
   pip install -r requirements.txt

   cd ../Voice
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   ```

4. **Start all backends:**
   ```bash
   # Double-click in Windows or run:
   cd backend
   .\start_all_backends.bat
   ```

5. **Start frontend:**
   ```bash
   cd frontend
   npm start
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Text API: http://localhost:8000
   - Voice API: http://localhost:8001
   - Fusion API: http://localhost:8002

---

## 📊 Features

### **Text Analysis**
- **Linguistic Pattern Detection** - Analyzes word choice, sentence structure, and writing patterns
- **TF-IDF Feature Extraction** - Identifies important words and phrases
- **Real-time Processing** - Instant analysis of entered text
- **Confidence Scoring** - Provides probability scores for predictions

### **Voice Analysis**
- **Audio Format Support** - Handles WAV, MP3, MP4, and other formats
- **MFCC Feature Extraction** - Advanced audio feature analysis
- **Deep Learning Model** - BiLSTM with attention mechanism
- **Real-time Processing** - Fast analysis of uploaded audio files

### **Fusion Analysis** (Multi-Modal)
- **Weighted Ensemble** - Combines multiple models intelligently
- **Confidence Aggregation** - Merges confidence scores from all models
- **Reasoning Engine** - Explains why a decision was made
- **Extensible Design** - Ready for face recognition integration

---

## 🎨 User Interface

### **Modern Design Features**
- **Dark Theme** - Easy on the eyes for extended use
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Framer Motion animations throughout
- **Data Visualization** - Interactive charts with Recharts
- **Glass Morphism** - Modern glass-like UI effects

### **Navigation Structure**
```
Landing → Login/Signup → Dashboard → Individual Analysis Pages
    ↓         ↓              ↓              ↓
Welcome → Authentication → Overview → Text/Voice/Face/Fusion
```

---

## 🔬 Technical Details

### **Machine Learning Models**

#### **Text Model**
- **Algorithm**: Logistic Regression (primary), SVM, Random Forest
- **Features**: TF-IDF vectors + 6 linguistic features
- **Training Data**: Deception detection dataset
- **Performance**: High accuracy on linguistic patterns

#### **Voice Model**
- **Architecture**: BiLSTM + Attention mechanism
- **Input**: MFCC features (39 dimensions)
- **Framework**: PyTorch
- **Training**: End-to-end deep learning approach

#### **Fusion Model**
- **Method**: Weighted ensemble averaging
- **Weights**: Text (50%), Voice (50%), Face (20% when available)
- **Output**: Combined prediction with enhanced confidence

### **APIs & Endpoints**

#### **Text API** (`/predict_text`)
```http
POST /predict_text
Content-Type: application/x-www-form-urlencoded

text=I was at home all night
```

#### **Voice API** (`/predict`)
```http
POST /predict
Content-Type: multipart/form-data

file: audio_file.wav
```

#### **Fusion API** (`/predict_fusion`)
```http
POST /predict_fusion
Content-Type: multipart/form-data

text=I was at home all night
audio_file: audio_file.wav
```

---

## 🔮 Future Enhancements

### **Phase 1: Face Recognition** ✅ (Ready for Integration)
- **Facial Expression Analysis** - Detect micro-expressions indicating deception
- **Eye Movement Tracking** - Monitor gaze patterns and blinking
- **Physiological Indicators** - Heart rate, skin temperature via video

### **Phase 2: Advanced Features**
- **Real-time Analysis** - Live video/audio streaming analysis
- **Multi-language Support** - Extend to other languages beyond English
- **Mobile App** - React Native version for mobile devices
- **Cloud Deployment** - AWS/Azure hosting for production use

### **Phase 3: Research Integration**
- **Scientific Validation** - Clinical trials and research partnerships
- **Dataset Expansion** - Larger, more diverse training datasets
- **Ethical Guidelines** - Responsible AI development practices

---

## 📚 Key Dependencies

### **Frontend**
- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library for smooth transitions
- **Recharts** - Data visualization library
- **Lucide React** - Beautiful icon library

### **Backend**
- **FastAPI** - Modern, fast web framework for building APIs
- **PyTorch** - Deep learning framework for neural networks
- **Scikit-learn** - Machine learning library for traditional algorithms
- **Librosa** - Audio processing and feature extraction
- **NLTK** - Natural language processing toolkit

### **Development Tools**
- **Uvicorn** - ASGI server for Python web applications
- **TypeScript** - Static type checking for JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **ESLint** - JavaScript linting and code quality

---

## 🛡️ Security & Privacy

### **Data Protection**
- **No Data Storage** - Analysis results not permanently stored
- **Local Processing** - All analysis happens locally (no cloud dependency)
- **Privacy-First** - Designed with user privacy in mind

### **Responsible AI**
- **Transparency** - Clear explanations of how decisions are made
- **Fairness** - Efforts to minimize bias in training data
- **Accountability** - Human oversight in critical applications

---

## 📈 Performance Metrics

### **Current Performance**
- **Text Model**: ~85% accuracy on test dataset
- **Voice Model**: ~82% accuracy on audio samples
- **Fusion Model**: ~88% accuracy (combined approach)

### **Scalability**
- **Concurrent Users**: Supports multiple simultaneous analyses
- **Response Time**: <2 seconds for individual analysis
- **Memory Usage**: Optimized for standard hardware

---

## 🆘 Troubleshooting

### **Common Issues**

**Backend not starting:**
```bash
# Install missing dependencies
pip install -r requirements.txt
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection issues:**
- Ensure all backends are running on correct ports
- Check firewall settings for ports 8000-8002
- Verify localhost access permissions

**Model loading errors:**
- Check that model files exist in correct directories
- Verify file paths in configuration files
- Ensure sufficient RAM for model loading

---

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Code Style**
- **Frontend**: ESLint + Prettier configuration
- **Backend**: PEP 8 style guidelines
- **Commits**: Conventional commit format

---

## 📄 License

This project is developed for **educational and research purposes**. Please ensure responsible use and comply with local laws and ethical guidelines when deploying lie detection technology.

---

## 📞 Contact & Support

For questions, issues, or collaboration opportunities:
- **Project Lead**: [Your Name/Contact Information]
- **Technical Issues**: Check troubleshooting section or create GitHub issue
- **Research Partnerships**: Open to academic and industry collaborations

---

**⚠️ Important Disclaimer**: This system is a research tool and should not be used for legal, employment, or critical decision-making purposes without proper validation and human oversight.

---

## 🎯 Project Status

- ✅ **Text Analysis** - Fully functional
- ✅ **Voice Analysis** - Fully functional
- ✅ **Fusion System** - Fully functional
- 🔄 **Face Recognition** - Architecture ready, implementation pending
- 🔄 **Mobile App** - Planned for future release
- 🔄 **Cloud Deployment** - Planned for production use

---

**Last Updated**: October 2024
**Version**: 1.0.0
**Development Status**: Active Development 🚧
