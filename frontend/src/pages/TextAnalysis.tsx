import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Type, 
  FileText, 
  Zap,
  BarChart3,
  MessageSquare,
  Brain,
  CheckCircle,
  AlertCircle,
  TrendingUp
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui'
import { AnalysisNavigation } from '../components/AnalysisNavigation'
import { useAuth } from '../contexts/AuthContext'
import { getConfidenceDescription, getConfidenceColor, getConfidenceBadgeVariant } from '../utils/confidenceUtils'

interface AnalysisResult {
  prediction: string
  confidence: number
}

// Helper component for displaying confidence results
const ConfidenceResultDisplay: React.FC<{ result: AnalysisResult }> = ({ result }) => {
  const confidenceResult = getConfidenceDescription(result.prediction, result.confidence);
  
  return (
    <div className="text-center space-y-4 p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
      <div className="flex items-center justify-center gap-3">
        {confidenceResult.prediction.toLowerCase().includes('truthful') ? (
          <CheckCircle className="h-12 w-12 text-green-600" />
        ) : (
          <AlertCircle className="h-12 w-12 text-red-600" />
        )}
        <h3 className="text-3xl font-display font-bold">
          <span className={confidenceResult.colorClass}>
            {confidenceResult.prediction}
          </span>
        </h3>
      </div>
      <Badge variant={getConfidenceBadgeVariant(result.confidence)} className="mb-2">
        {confidenceResult.descriptiveLevel}
      </Badge>
      <p className="text-muted-foreground">
        {confidenceResult.description}
      </p>
    </div>
  );
};

export const TextAnalysis: React.FC = () => {
  const { user } = useAuth()
  const [textInput, setTextInput] = useState<string>('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const analyzeText = async () => {
    if (!textInput.trim()) return

    setIsAnalyzing(true)
    setError(null)
    setResult(null)
    
    try {
      // Create FormData for the request
      const formData = new FormData()
      formData.append('text', textInput)
      
      // Add user_id for auto-save if user is logged in
      if (user?.id) {
        formData.append('user_id', user.id)
        console.log('📤 Sending user_id:', user.id)
      } else {
        console.warn('⚠️ No user logged in - report will not be saved')
      }
      
      // Call the backend API
      const textApiUrl = process.env.REACT_APP_TEXT_API_URL || 'http://127.0.0.1:8000'
      const response = await fetch(`${textApiUrl}/predict_text`, {
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
      setError(err instanceof Error ? err.message : 'Failed to analyze text. Please ensure the backend is running.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const clearAnalysis = () => {
    setTextInput('')
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
          Text-Based Lie Detection
        </h1>
        <p className="text-muted-foreground text-lg">
          Analyze written text for deception patterns using advanced NLP and linguistic analysis
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Text Input Section */}
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
                Enter the text you want to analyze for deception patterns
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Text Input Area */}
              <div className="space-y-2">
                <Label htmlFor="textInput">Text to Analyze</Label>
                <textarea
                  id="textInput"
                  placeholder="Enter or paste the text you want to analyze for deception patterns..."
                  value={textInput}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTextInput(e.target.value)}
                  className="min-h-[200px] resize-none flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={isAnalyzing}
                />
                <p className="text-sm text-muted-foreground">
                  {textInput.length} characters • Minimum 50 characters recommended
                </p>
              </div>

              {/* Analysis Controls */}
              <div className="flex gap-4">
                <Button
                  onClick={analyzeText}
                  disabled={!textInput.trim() || textInput.length < 10 || isAnalyzing}
                  variant="brand"
                  size="lg"
                  className="flex-1"
                >
                  {isAnalyzing ? (
                    <>
                      <Zap className="h-4 w-4 mr-2 animate-pulse" />
                      Analyzing Text...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      Analyze Text
                    </>
                  )}
                </Button>
                
                {textInput && (
                  <Button
                    onClick={clearAnalysis}
                    variant="outline"
                    size="lg"
                    disabled={isAnalyzing}
                  >
                    Clear
                  </Button>
                )}
              </div>

              {/* Analysis Features */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MessageSquare className="h-4 w-4" />
                  Linguistic Patterns
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText className="h-4 w-4" />
                  Semantic Analysis
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <BarChart3 className="h-4 w-4" />
                  Statistical Modeling
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Brain className="h-4 w-4" />
                  AI-Powered Detection
                </div>
              </div>
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
              <CardDescription>
                AI-powered deception detection results
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {!result && !error && (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center space-y-4">
                    <Type className="h-16 w-16 text-muted-foreground mx-auto" />
                    <h3 className="text-xl font-display font-semibold text-muted-foreground">
                      Ready for Analysis
                    </h3>
                    <p className="text-muted-foreground max-w-sm">
                      Enter text and click "Analyze Text" to see results
                    </p>
                  </div>
                </div>
              )}
              
              {error && (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center space-y-4">
                    <AlertCircle className="h-16 w-16 text-red-500 mx-auto" />
                    <h3 className="text-xl font-display font-semibold text-red-600">
                      Analysis Failed
                    </h3>
                    <p className="text-muted-foreground max-w-sm">
                      {error}
                    </p>
                  </div>
                </div>
              )}
              
              {result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4 }}
                  className="space-y-6"
                >
                  {/* Prediction Result */}
                  <ConfidenceResultDisplay result={result} />
                  
                  {/* Confidence Score */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Confidence Score
                      </Label>
                      <span className="text-2xl font-bold text-blue-600">
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${result.confidence * 100}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className={`h-full rounded-full ${
                          result.prediction === 'Truthful' 
                            ? 'bg-gradient-to-r from-green-400 to-green-600' 
                            : 'bg-gradient-to-r from-red-400 to-red-600'
                        }`}
                      />
                    </div>
                    
                    <p className="text-sm text-muted-foreground">
                      Model confidence in the prediction
                    </p>
                  </div>
                  
                  {/* Additional Info */}
                  <div className="pt-4 border-t space-y-2">
                    <h4 className="font-semibold text-sm">Analysis Details</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Text Length</p>
                        <p className="font-medium">{textInput.length} characters</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Model Used</p>
                        <p className="font-medium">Logistic Regression</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
