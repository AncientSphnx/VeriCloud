import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  Zap, 
  CheckCircle, 
  AlertTriangle,
  Brain,
  Activity,
  Target,
  Mic,
  Type,
  Upload,
  FileAudio,
  AlertCircle,
  Camera
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui'
import { getConfidenceDescription, getConfidenceColor, getConfidenceBadgeVariant } from '../utils/confidenceUtils'
import { 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { AnalysisNavigation } from '../components/AnalysisNavigation'

interface FusionResult {
  final_prediction: string
  final_confidence: number
  final_score: number
  breakdown: {
    text: {
      prediction: string
      confidence: number
      weight: number
      contribution: number
    }
    voice: {
      prediction: string
      confidence: number
      weight: number
      contribution: number
    }
    face: {
      prediction: string
      confidence: number
      weight: number
      contribution: number
    }
  }
  reasoning: string
  weights_used: Record<string, number>
  errors?: Record<string, string>
}

// Helper component for displaying fusion confidence results
const FusionConfidenceDisplay: React.FC<{ fusionResult: FusionResult }> = ({ fusionResult }) => {
  const confidenceResult = getConfidenceDescription(fusionResult.final_prediction, fusionResult.final_confidence);
  
  return (
    <>
      <div className="flex items-center justify-center gap-3 mb-2">
        {confidenceResult.prediction.toLowerCase().includes('truthful') ? (
          <CheckCircle className="h-12 w-12 text-green-600" />
        ) : (
          <AlertTriangle className="h-12 w-12 text-red-600" />
        )}
        <CardTitle className={`text-4xl font-display ${confidenceResult.colorClass}`}>
          {confidenceResult.prediction}
        </CardTitle>
      </div>
      <Badge variant={getConfidenceBadgeVariant(fusionResult.final_confidence)} className="mb-2">
        {confidenceResult.descriptiveLevel}
      </Badge>
      <CardDescription className="text-lg">
        {confidenceResult.description}
      </CardDescription>
    </>
  );
};

export const FusionDashboard: React.FC = () => {
  const [fusionResult, setFusionResult] = useState<FusionResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [textInput, setTextInput] = useState<string>('')
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runFusionAnalysis = async () => {
    if (!textInput.trim() || !audioFile) {
      setError('Please provide both text and audio file for fusion analysis.')
      return
    }

    setIsAnalyzing(true)
    setError(null)
    setFusionResult(null)
    
    try {
      const formData = new FormData()
      formData.append('text', textInput)
      formData.append('audio_file', audioFile)
      if (videoFile) {
        formData.append('video_file', videoFile)
      }
      
      const fusionApiUrl = process.env.REACT_APP_FUSION_API_URL || 'http://127.0.0.1:8003'
      const response = await fetch(`${fusionApiUrl}/predict_fusion`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setFusionResult(data)
    } catch (err) {
      console.error('Fusion analysis error:', err)
      setError(err instanceof Error ? err.message : 'Failed to perform fusion analysis. Ensure all backends are running.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const clearAll = () => {
    setTextInput('')
    setAudioFile(null)
    setVideoFile(null)
    setFusionResult(null)
    setError(null)
  }

  // Prepare chart data
  const individualResults = fusionResult ? [
    { 
      method: 'Text', 
      confidence: fusionResult.breakdown.text.confidence * 100,
      prediction: fusionResult.breakdown.text.prediction,
      fill: '#3b82f6'
    },
    { 
      method: 'Voice', 
      confidence: fusionResult.breakdown.voice.confidence * 100,
      prediction: fusionResult.breakdown.voice.prediction,
      fill: '#8b5cf6'
    },
    ...(fusionResult.breakdown.face ? [{
      method: 'Face',
      confidence: fusionResult.breakdown.face.confidence * 100,
      prediction: fusionResult.breakdown.face.prediction,
      fill: '#ec4899'
    }] : [])
  ] : []

  const methodDistribution = fusionResult ? [
    { 
      name: 'Text Analysis', 
      value: fusionResult.weights_used.text * 100, 
      fill: '#3b82f6' 
    },
    { 
      name: 'Voice Analysis', 
      value: fusionResult.weights_used.voice * 100, 
      fill: '#8b5cf6' 
    },
    ...(fusionResult.weights_used.face ? [{
      name: 'Face Analysis',
      value: fusionResult.weights_used.face * 100,
      fill: '#ec4899'
    }] : [])
  ] : []

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
          Fusion Dashboard
        </h1>
        <p className="text-muted-foreground text-lg">
          Combine and analyze results from all detection methods for comprehensive lie detection
        </p>
      </motion.div>

      {/* Input Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Text Input */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Type className="h-5 w-5 text-blue-600" />
                Text Input
              </CardTitle>
              <CardDescription>
                Enter the statement to analyze
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="textInput">Text</Label>
                <textarea
                  id="textInput"
                  placeholder="Enter the text statement..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  className="min-h-[150px] resize-none flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={isAnalyzing}
                />
                <p className="text-sm text-muted-foreground">
                  {textInput.length} characters
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Audio Input */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-purple-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5 text-purple-600" />
                Audio Input
              </CardTitle>
              <CardDescription>
                Upload the corresponding audio file
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="audioFile">Audio File</Label>
                <div className="flex flex-col items-center justify-center border-2 border-dashed border-muted rounded-lg p-8 hover:border-primary/50 transition-colors">
                  <input
                    id="audioFile"
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                    className="hidden"
                    disabled={isAnalyzing}
                  />
                  <label htmlFor="audioFile" className="cursor-pointer text-center">
                    {audioFile ? (
                      <>
                        <FileAudio className="h-12 w-12 text-purple-600 mx-auto mb-2" />
                        <p className="text-sm font-medium">{audioFile.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </>
                    ) : (
                      <>
                        <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Click to upload audio file</p>
                        <p className="text-xs text-muted-foreground mt-1">WAV, MP3, or other audio formats</p>
                      </>
                    )}
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Video Input */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-pink-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-pink-600" />
                Video Input
              </CardTitle>
              <CardDescription>
                Upload a video file for face analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="videoFile">Video File</Label>
                <div className="flex flex-col items-center justify-center border-2 border-dashed border-muted rounded-lg p-8 hover:border-primary/50 transition-colors">
                  <input
                    id="videoFile"
                    type="file"
                    accept="video/*"
                    onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                    className="hidden"
                    disabled={isAnalyzing}
                  />
                  <label htmlFor="videoFile" className="cursor-pointer text-center">
                    {videoFile ? (
                      <>
                        <Camera className="h-12 w-12 text-pink-600 mx-auto mb-2" />
                        <p className="text-sm font-medium">{videoFile.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {(videoFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </>
                    ) : (
                      <>
                        <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Click to upload video</p>
                        <p className="text-xs text-muted-foreground mt-1">MP4, WebM, or other video formats</p>
                      </>
                    )}
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Run Analysis Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex gap-4 justify-center"
      >
        <Button
          onClick={runFusionAnalysis}
          disabled={!textInput.trim() || !audioFile || isAnalyzing}
          variant="brand"
          size="lg"
          className="px-12"
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
              Running Fusion Analysis...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4 mr-2" />
              Run Fusion Analysis
            </>
          )}
        </Button>
        
        {(textInput || audioFile || videoFile) && (
          <Button
            onClick={clearAll}
            variant="outline"
            size="lg"
            disabled={isAnalyzing}
          >
            Clear All
          </Button>
        )}
      </motion.div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="border-red-500/50 bg-red-500/10">
            <CardContent className="flex items-center gap-3 py-4">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500">{error}</p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {fusionResult && (
        <>
          {/* Final Result */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card className={`shadow-elegant-lg bg-card/50 backdrop-blur-sm ${
              fusionResult.final_prediction === 'Truthful' 
                ? 'border-green-500/50' 
                : 'border-red-500/50'
            }`}>
              <CardHeader className="text-center">
                <FusionConfidenceDisplay fusionResult={fusionResult} />
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${fusionResult.final_confidence * 100}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    className={`h-4 rounded-full ${
                      fusionResult.final_prediction === 'Truthful' 
                        ? 'bg-gradient-to-r from-green-400 to-green-600' 
                        : 'bg-gradient-to-r from-red-400 to-red-600'
                    }`}
                  />
                </div>
                <div className="text-center p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm font-medium mb-1">Analysis Reasoning</p>
                  <p className="text-sm text-muted-foreground">
                    {fusionResult.reasoning}
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-4 pt-2">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Weighted Score</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {(fusionResult.final_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Models Combined</p>
                    <p className="text-2xl font-bold text-purple-600">{Object.keys(fusionResult.breakdown).length}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Confidence</p>
                    <p className="text-2xl font-bold text-pink-600">
                      {(fusionResult.final_confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Individual Method Results */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <h2 className="text-2xl font-semibold mb-6 text-blue-600">
              Individual Model Results
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Text Analysis Result */}
              <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
                <CardHeader className="text-center">
                  <Type className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <CardTitle>Text Analysis</CardTitle>
                  <CardDescription className={`text-lg font-semibold ${
                    fusionResult.breakdown.text.prediction === 'Truthful' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {fusionResult.breakdown.text.prediction}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {(fusionResult.breakdown.text.confidence * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">Model Confidence</p>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${fusionResult.breakdown.text.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="pt-3 border-t space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Weight:</span>
                      <span className="font-medium">{(fusionResult.breakdown.text.weight * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Contribution:</span>
                      <span className="font-medium">{(fusionResult.breakdown.text.contribution * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Voice Analysis Result */}
              <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-purple-600/30">
                <CardHeader className="text-center">
                  <Mic className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                  <CardTitle>Voice Analysis</CardTitle>
                  <CardDescription className={`text-lg font-semibold ${
                    fusionResult.breakdown.voice.prediction === 'Truthful' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {fusionResult.breakdown.voice.prediction}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {(fusionResult.breakdown.voice.confidence * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">Model Confidence</p>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${fusionResult.breakdown.voice.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="pt-3 border-t space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Weight:</span>
                      <span className="font-medium">{(fusionResult.breakdown.voice.weight * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Contribution:</span>
                      <span className="font-medium">{(fusionResult.breakdown.voice.contribution * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Voice Analysis Result */}
              <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-purple-600/30">
                <CardHeader className="text-center">
                  <Mic className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                  <CardTitle>Voice Analysis</CardTitle>
                  <CardDescription className={`text-lg font-semibold ${
                    fusionResult.breakdown.voice.prediction === 'Truthful' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {fusionResult.breakdown.voice.prediction}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {(fusionResult.breakdown.voice.confidence * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">Model Confidence</p>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${fusionResult.breakdown.voice.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="pt-3 border-t space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Weight:</span>
                      <span className="font-medium">{(fusionResult.breakdown.voice.weight * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Contribution:</span>
                      <span className="font-medium">{(fusionResult.breakdown.voice.contribution * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Face Analysis Result (if available) */}
              {fusionResult.breakdown.face && (
                <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-pink-600/30">
                  <CardHeader className="text-center">
                    <Camera className="h-8 w-8 text-pink-600 mx-auto mb-2" />
                    <CardTitle>Face Analysis</CardTitle>
                    <CardDescription className={`text-lg font-semibold ${
                      fusionResult.breakdown.face.prediction === 'Truthful' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {fusionResult.breakdown.face.prediction}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-pink-600 mb-2">
                        {(fusionResult.breakdown.face.confidence * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">Model Confidence</p>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-pink-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${fusionResult.breakdown.face.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="pt-3 border-t space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Weight:</span>
                        <span className="font-medium">{(fusionResult.breakdown.face.weight * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Contribution:</span>
                        <span className="font-medium">{(fusionResult.breakdown.face.contribution * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </motion.div>

          {/* Confidence Comparison Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-muted/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  <span>Model Confidence Comparison</span>
                </CardTitle>
                <CardDescription>
                  Side-by-side comparison of individual model confidences
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={individualResults}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="method" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }} 
                    />
                    <Bar dataKey="confidence" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Method Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-muted/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-purple-600" />
                  Model Weight Distribution
                </CardTitle>
                <CardDescription>
                  How each model contributes to the final decision
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={methodDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name.split(' ')[0]}: ${value.toFixed(0)}%`}
                    >
                      {methodDistribution.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }} 
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}

    </div>
  )
}
