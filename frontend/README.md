# AI-Driven Lie Detection System

A comprehensive React-based web application that uses artificial intelligence to detect deception through multi-modal analysis of voice patterns, facial expressions, and handwriting characteristics.

## 🚀 Features

### Core Analysis Methods
- **Voice Analysis**: Real-time audio recording and analysis of pitch, MFCC coefficients, jitter, and shimmer
- **Face Analysis**: Live webcam facial expression detection and micro-expression analysis
- **Handwriting Analysis**: Image-based handwriting pattern recognition and graphological analysis
- **Fusion Dashboard**: Advanced ensemble algorithm combining all three methods for enhanced accuracy

### User Experience
- **Modern UI**: Dark futuristic theme with neon highlights (blue, purple, green)
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Processing**: Instant analysis with confidence scores
- **Interactive Charts**: Beautiful data visualizations using Recharts
- **Smooth Animations**: Framer Motion powered transitions and effects

### Authentication & Security
- **User Authentication**: Secure login/signup system with session management
- **Protected Routes**: Analysis features accessible only to authenticated users
- **Data Privacy**: Local processing with encrypted data transmission

### Additional Features
- **Demo Mode**: Interactive demonstration for judges and evaluators
- **Reports & Analytics**: Historical analysis tracking and export capabilities
- **Comprehensive Documentation**: About, How It Works, FAQ, and Contact pages
- **Dark Mode Toggle**: Customizable theme preferences

## 🛠 Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: TailwindCSS with custom neon theme
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Routing**: React Router DOM
- **Build Tool**: Create React App

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-lie-detection-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 🏗 Project Structure

```
src/
├── components/
│   ├── ui/                 # Reusable UI components
│   ├── Layout/            # Layout components (Header, Sidebar, Layout)
│   ├── DemoMode.tsx       # Interactive demo component
│   └── ProtectedRoute.tsx # Route protection
├── pages/
│   ├── Landing.tsx        # Landing page
│   ├── Login.tsx          # Authentication pages
│   ├── Signup.tsx
│   ├── Dashboard.tsx      # Main dashboard
│   ├── VoiceAnalysis.tsx  # Voice analysis page
│   ├── FaceAnalysis.tsx   # Face analysis page
│   ├── HandwritingAnalysis.tsx # Handwriting analysis page
│   ├── FusionDashboard.tsx # Combined analysis results
│   ├── Reports.tsx        # Historical reports
│   ├── About.tsx          # Project information
│   ├── HowItWorks.tsx     # Technical documentation
│   ├── FAQ.tsx            # Frequently asked questions
│   └── Contact.tsx        # Contact form
├── contexts/
│   └── AuthContext.tsx    # Authentication context
├── config/
│   └── api.ts            # API configuration and mock responses
├── lib/
│   └── utils.ts          # Utility functions
└── App.tsx               # Main application component
```

## 🎯 Usage

### Getting Started
1. **Sign Up**: Create a new account or log in with existing credentials
2. **Dashboard**: Access the main dashboard with quick action cards
3. **Analysis**: Choose from voice, face, or handwriting analysis
4. **Results**: View detailed analysis results with confidence scores
5. **Reports**: Track your analysis history and export data

### Analysis Methods

#### Voice Analysis
- Record audio directly or upload audio files
- Supports various audio formats (WAV, MP3, etc.)
- Real-time feature extraction and visualization
- Confidence scoring with detailed breakdowns

#### Face Analysis
- Live webcam integration for real-time analysis
- Video file upload support
- Micro-expression detection
- Emotion classification and confidence metrics

#### Handwriting Analysis
- Image upload or camera capture
- Graphological feature extraction
- Pressure, slant, and spacing analysis
- Deception indicator identification

#### Fusion Dashboard
- Combines results from all three methods
- Weighted ensemble algorithm
- Historical performance tracking
- Enhanced accuracy through multi-modal analysis

## 🔧 Configuration

### API Configuration
The system uses mock responses for demonstration. To integrate with a real backend:

1. Update `src/config/api.ts` with your API endpoints
2. Replace mock responses with actual API calls
3. Configure authentication endpoints
4. Set up data persistence

### Environment Variables
Create a `.env` file in the root directory:
```env
REACT_APP_API_URL=http://localhost:3001/api
REACT_APP_DEMO_MODE=true
```

## 🎨 Customization

### Theme Colors
The application uses a custom neon color palette defined in `tailwind.config.js`:
- **Neon Blue**: `#00d4ff`
- **Neon Purple**: `#8b5cf6`
- **Neon Green**: `#00ff88`
- **Neon Pink**: `#ff0080`

### Adding New Analysis Methods
1. Create a new page component in `src/pages/`
2. Add routing in `src/App.tsx`
3. Update navigation in `src/components/Layout/Sidebar.tsx`
4. Add mock responses in `src/config/api.ts`

## 📊 Demo Mode

The application includes a comprehensive demo mode for presentations:
- Simulates all three analysis methods
- Shows realistic processing times
- Displays sample results with confidence scores
- Perfect for demonstrations and evaluations

Access demo mode through the "Demo" button in the header or run it programmatically.

## 🔒 Security Considerations

- All analysis is performed client-side when possible
- User data is stored locally with encryption
- Session management with secure token handling
- No sensitive data transmitted without user consent

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Netlify/Vercel
1. Connect your repository to your deployment platform
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Configure environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **React Team** for the excellent framework
- **Tailwind CSS** for the utility-first CSS framework
- **Radix UI** for accessible component primitives
- **Framer Motion** for smooth animations
- **Recharts** for beautiful data visualizations

## 📞 Support

For support, email support@ai-lie-detection.com or join our community discussions.

---

**Built with ❤️ by the AI Lie Detection Team**
