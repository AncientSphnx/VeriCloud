import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Camera, 
  Upload, 
  Play, 
  Square, 
  Zap,
  Video,
  FileVideo,
  BarChart3,
  TrendingUp,
  Activity,
  AlertCircle
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { AnalysisNavigation } from '../components/AnalysisNavigation'
import { useAuth } from '../contexts/AuthContext'

interface AnalysisResult {
  prediction: string
  confidence: number
}

export const FaceAnalysis: React.FC = () => {
  const { user } = useAuth()
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isCapturing, setIsCapturing] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file)
      const url = URL.createObjectURL(file)
      setVideoUrl(url)
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 }, 
        audio: false 
      })
      setStream(mediaStream)
      setIsCapturing(true)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
      setIsCapturing(false)
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }
  }

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob)
            setVideoUrl(url)
            setVideoFile(new File([blob], 'capture.jpg', { type: 'image/jpeg' }))
          }
        })
      }
    }
  }

  const analyzeVideo = async () => {
    if (!videoFile) return

    setIsAnalyzing(true)
    setError(null)
    setResult(null)
    
    try {
      const formData = new FormData()
      formData.append('file', videoFile)
      
      // Add user_id for auto-save if user is logged in
      if (user?.id) {
        formData.append('user_id', user.id)
        console.log('📤 Face analysis sending user_id:', user.id)
      } else {
        console.warn('⚠️ No user logged in - face report will not be saved')
      }
      
      const faceApiUrl = process.env.REACT_APP_FACE_API_URL || 'http://127.0.0.1:8002'
      
      // No timeout - let the API process as long as needed
      const response = await fetch(`${faceApiUrl}/predict`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setResult(data)
      
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err instanceof Error ? err.message : 'Failed to analyze video. Please ensure the backend is running.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const clearAnalysis = () => {
    setVideoFile(null)
    setVideoUrl(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-8">
      {/* Navigation */}
      <AnalysisNavigation />
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-4xl font-display font-bold mb-4 text-blue-600">
          Face Analysis
        </h1>
        <p className="text-muted-foreground text-lg">
          Analyze facial expressions, micro-expressions, and behavioral patterns for deception detection
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Video Input Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-blue-600" />
                Video Input
              </CardTitle>
              <CardDescription>
                Upload a video file or use your camera for real-time analysis
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* File Upload */}
              <div className="space-y-2">
                <Label htmlFor="videoFile">Upload Video File</Label>
                <Input
                  id="videoFile"
                  type="file"
                  accept="video/*"
                  onChange={handleFileUpload}
                  className="cursor-pointer"
                />
              </div>

              {/* Camera Controls */}
              <div className="space-y-4">
                <Label>Camera Capture</Label>
                {!isCapturing ? (
                  <Button
                    onClick={startCamera}
                    variant="outline"
                    size="lg"
                    className="w-full"
                  >
                    <Video className="h-4 w-4 mr-2" />
                    Start Camera
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div className="relative bg-black rounded-lg overflow-hidden">
                      <video
                        ref={videoRef}
                        autoPlay
                        muted
                        className="w-full h-48 object-cover"
                      />
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        onClick={captureImage}
                        variant="success"
                        size="sm"
                        className="flex-1"
                      >
                        <Camera className="h-4 w-4 mr-2" />
                        Capture
                      </Button>
                      <Button
                        onClick={stopCamera}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        <Square className="h-4 w-4 mr-2" />
                        Stop
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Video Preview */}
              {videoUrl && !isCapturing && (
                <div className="space-y-2">
                  <Label>Video Preview</Label>
                  <div className="relative bg-black rounded-lg overflow-hidden">
                    <video
                      src={videoUrl}
                      controls
                      className="w-full h-48 object-cover"
                    />
                  </div>
                </div>
              )}

              {/* Analyze Button */}
              <Button
                onClick={analyzeVideo}
                disabled={(!videoUrl && !stream) || isAnalyzing}
                variant="brand"
                size="lg"
                className="w-full"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Analyze Video
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-muted/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                Analysis Results
              </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center h-96">
              {error ? (
                <div className="text-center space-y-4">
                  <AlertCircle className="h-16 w-16 text-red-500 mx-auto" />
                  <h3 className="text-xl font-display font-semibold text-red-600">Error</h3>
                  <p className="text-muted-foreground max-w-sm">{error}</p>
                </div>
              ) : result ? (
                <div className="text-center space-y-6 w-full">
                  <div>
                    <h3 className="text-2xl font-display font-bold mb-2">
                      <span className={result.prediction === 'Deceptive' ? 'text-red-600' : 'text-green-600'}>
                        {result.prediction}
                      </span>
                    </h3>
                    <p className="text-muted-foreground">Confidence: {(result.confidence * 100).toFixed(2)}%</p>
                  </div>
                  <Button onClick={clearAnalysis} variant="outline" size="sm">
                    Clear Results
                  </Button>
                </div>
              ) : (
                <div className="text-center space-y-4">
                  <Camera className="h-16 w-16 text-muted-foreground mx-auto" />
                  <h3 className="text-xl font-display font-semibold text-muted-foreground">
                    Ready for Face Analysis
                  </h3>
                  <p className="text-muted-foreground max-w-sm">
                    Upload a video file or use your camera, then click "Analyze Video" to detect deception.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Hidden canvas for image capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
