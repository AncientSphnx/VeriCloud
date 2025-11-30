// API Configuration - easily replaceable with real backend endpoints
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:3001/api',
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      SIGNUP: '/auth/signup',
      LOGOUT: '/auth/logout',
      VERIFY: '/auth/verify',
    },
    ANALYSIS: {
      VOICE: '/analysis/voice',
      FACE: '/analysis/face',
      TEXT: '/analysis/text',
      FUSION: '/analysis/fusion',
    },
    USER: {
      PROFILE: '/user/profile',
      REPORTS: '/user/reports',
      HISTORY: '/user/history',
    },
    FEEDBACK: '/feedback',
  },
}

// Demo mode configuration
export const DEMO_CONFIG = {
  ENABLED: true,
  AUTO_FILL_DELAY: 1000,
  ANALYSIS_DELAY: 3000,
}

// Mock API responses for demo purposes
export const MOCK_RESPONSES = {
  VOICE_ANALYSIS: {
    success: true,
    data: {
      result: 'Truth',
      confidence: 0.87,
      features: {
        pitch: { mean: 180.5, variance: 25.3 },
        mfcc: [12.5, -8.2, 4.1, -2.8, 1.9],
        jitter: 0.012,
        shimmer: 0.045,
        spectralCentroid: 2500.8,
      },
      timestamp: new Date().toISOString(),
    },
  },
  FACE_ANALYSIS: {
    success: true,
    data: {
      result: 'Lie',
      confidence: 0.73,
      emotions: {
        neutral: 0.45,
        happy: 0.12,
        sad: 0.08,
        angry: 0.15,
        fear: 0.10,
        disgust: 0.05,
        surprise: 0.05,
      },
      microExpressions: ['eye_movement', 'lip_compression', 'brow_furrow'],
      timestamp: new Date().toISOString(),
    },
  },
  textAnalysis: {
    result: 'Truth',
    confidence: 87,
    metrics: [
      { name: 'Linguistic Complexity', value: 78 },
      { name: 'Emotional Indicators', value: 65 },
      { name: 'Consistency Score', value: 92 },
      { name: 'Semantic Coherence', value: 84 },
      { name: 'Stress Markers', value: 23 }
    ],
    radarData: [
      { subject: 'Truthfulness', A: 87 },
      { subject: 'Confidence', A: 78 },
      { subject: 'Consistency', A: 92 },
      { subject: 'Clarity', A: 84 },
      { subject: 'Emotion', A: 65 },
      { subject: 'Structure', A: 89 }
    ],
    indicators: [
      'High semantic consistency throughout the text',
      'Natural language flow with minimal hesitation markers',
      'Consistent emotional tone and vocabulary usage',
      'No significant contradictory statements detected',
      'Appropriate level of detail for the context'
    ],
    timestamp: new Date().toISOString(),
  },
  FUSION_RESULT: {
    success: true,
    data: {
      finalResult: 'Truth',
      overallConfidence: 0.84,
      individualResults: {
        voice: { result: 'Truth', confidence: 0.87 },
        face: { result: 'Lie', confidence: 0.73 },
        text: { result: 'Truth', confidence: 0.87 },
      },
      weightedScore: 0.84,
      timestamp: new Date().toISOString(),
    },
  },
}
