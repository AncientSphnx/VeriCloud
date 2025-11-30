import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Mic, 
  Upload, 
  Play, 
  Pause, 
  Square, 
  Zap
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { Badge } from '../components/ui'
import { AnalysisNavigation } from '../components/AnalysisNavigation'
import { useAuth } from '../contexts/AuthContext'
import { getConfidenceDescription, getConfidenceColor, getConfidenceBadgeVariant } from '../utils/confidenceUtils'

interface AnalysisResult {
  prediction: string
  confidence: number
}

// Helper component for displaying confidence results
const ConfidenceResultDisplay: React.FC<{ 
  result: AnalysisResult; 
  onClearAnalysis: () => void;
}> = ({ result, onClearAnalysis }) => {
  const confidenceResult = getConfidenceDescription(result.prediction, result.confidence);
  
  return (
    <div className="text-center space-y-4">
      <h3 className="text-xl font-display font-semibold">
        <span className={confidenceResult.colorClass}>
          {confidenceResult.prediction}
        </span>
      </h3>
      <Badge variant={getConfidenceBadgeVariant(result.confidence)} className="mb-2">
        {confidenceResult.descriptiveLevel}
      </Badge>
      <p className="text-muted-foreground text-sm mb-3">{confidenceResult.description}</p>
      <div className="flex items-center justify-center space-x-2">
        <span className="text-sm text-muted-foreground">Confidence:</span>
        <div className="w-32 bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${getConfidenceColor(result.confidence)}`}
            style={{ width: `${(result.confidence * 100).toFixed(2)}%` }}
          />
        </div>
        <span className="text-sm font-medium">{(result.confidence * 100).toFixed(2)}%</span>
      </div>
      <Button onClick={onClearAnalysis} variant="outline" size="sm" className="mt-4">
        Clear Results
      </Button>
    </div>
  );
};

export const VoiceAnalysis: React.FC = () => {
  const { user } = useAuth()
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<{ prediction: string; confidence: number } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [stream, setStream] = useState<MediaStream | null>(null)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [recordingTime, setRecordingTime] = useState(0)

  const audioRef = useRef<HTMLAudioElement | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const clearAnalysis = () => {
    setResult(null)
    setError(null)
    setAudioFile(null)
    setAudioUrl(null)
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type.startsWith('audio/')) {
      setAudioFile(file)
      const url = URL.createObjectURL(file)
      setAudioUrl(url)
      setResult(null) // reset old result
    }
  }

  const startRecording = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setStream(mediaStream)
      
      const recorder = new MediaRecorder(mediaStream)
      setMediaRecorder(recorder)
      
      const chunks: Blob[] = []
      recorder.ondataavailable = (event) => {
        chunks.push(event.data)
      }
      
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' })
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)
        setAudioFile(new File([blob], 'recording.wav', { type: 'audio/wav' }))
        setResult(null) // reset old result
      }
      
      recorder.start()
      setIsRecording(true)
      setRecordingTime(0)
      
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } catch (error) {
      console.error('Error accessing microphone:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
      
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
        setStream(null)
      }
    }
  }

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        audioRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const analyzeAudio = async () => {
    if (!audioFile) return
    setIsAnalyzing(true)

    try {
      const formData = new FormData()
      formData.append('file', audioFile)
      
      // Add user_id for auto-save if user is logged in
      if (user?.id) {
        formData.append('user_id', user.id)
        console.log('📤 Voice analysis sending user_id:', user.id)
      } else {
        console.warn('⚠️ No user logged in - voice report will not be saved')
      }

      const voiceApiUrl = process.env.REACT_APP_VOICE_API_URL || 'http://127.0.0.1:8001'
      const response = await fetch(`${voiceApiUrl}/predict`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to analyze audio')

      const data = await response.json()
      console.log('Prediction result:', data)
      setResult(data) // update state
    } catch (error) {
      console.error('Error analyzing audio:', error)
      setResult({ prediction: 'Error', confidence: 0 })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-8">
      {/* Navigation */}
      <AnalysisNavigation />
      
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
        <h1 className="text-4xl font-display font-bold mb-4 text-blue-600">Voice Analysis</h1>
        <p className="text-muted-foreground text-lg">
          Analyze vocal patterns, stress indicators, and speech characteristics for deception detection
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.1 }}>
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5 text-blue-600" />
                Audio Input
              </CardTitle>
              <CardDescription>Upload an audio file or record your voice for analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Upload */}
              <div className="space-y-2">
                <Label htmlFor="audioFile">Upload Audio File</Label>
                <Input id="audioFile" type="file" accept="audio/*" onChange={handleFileUpload} className="cursor-pointer" />
              </div>

              {/* Record */}
              <div className="space-y-4">
                <Label>Record Audio</Label>
                <div className="flex items-center gap-4">
                  {!isRecording ? (
                    <Button onClick={startRecording} variant="outline" size="lg">
                      <Mic className="h-4 w-4 mr-2" />
                      Start Recording
                    </Button>
                  ) : (
                    <Button onClick={stopRecording} variant="destructive" size="lg">
                      <Square className="h-4 w-4 mr-2" />
                      Stop Recording
                    </Button>
                  )}

                  {isRecording && (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                      <span className="text-sm font-mono">{formatTime(recordingTime)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Playback */}
              {audioUrl && (
                <div className="space-y-4">
                  <Label>Audio Preview</Label>
                  <div className="flex items-center gap-4">
                    <Button onClick={togglePlayback} variant="outline" size="sm">
                      {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    </Button>
                    <span className="text-sm text-muted-foreground">{audioFile?.name || 'Recording'}</span>
                  </div>
                  <audio ref={audioRef} src={audioUrl} onEnded={() => setIsPlaying(false)} className="hidden" />
                </div>
              )}

              {/* Analyze */}
              <Button onClick={analyzeAudio} disabled={!audioUrl || isAnalyzing} variant="brand" size="lg" className="w-full">
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Analyze Voice
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-muted/30">
            <CardContent className="flex items-center justify-center h-96">
              {result ? (
                <ConfidenceResultDisplay result={result} onClearAnalysis={clearAnalysis} />
              ) : (
                <div className="text-center space-y-4">
                  <Mic className="h-16 w-16 text-muted-foreground mx-auto" />
                  <h3 className="text-xl font-display font-semibold text-muted-foreground">Ready for Voice Analysis</h3>
                  <p className="text-muted-foreground max-w-sm">
                    Upload an audio file or record your voice, then click "Analyze Voice".
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
