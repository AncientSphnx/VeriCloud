import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, CheckCircle } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { MOCK_RESPONSES } from '../config/api'

interface DemoModeProps {
  onDemoComplete?: (results: any) => void
}

export const DemoMode: React.FC<DemoModeProps> = ({ onDemoComplete }) => {
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [results, setResults] = useState<any>(null)

  const demoSteps = [
    { name: 'Voice Analysis', duration: 2000, result: MOCK_RESPONSES.VOICE_ANALYSIS.data },
    { name: 'Face Analysis', duration: 2500, result: MOCK_RESPONSES.FACE_ANALYSIS.data },
    { name: 'Text Analysis', duration: 2000, result: MOCK_RESPONSES.textAnalysis },
    { name: 'Fusion Processing', duration: 1500, result: MOCK_RESPONSES.FUSION_RESULT.data }
  ]

  const runDemo = async () => {
    setIsRunning(true)
    setCurrentStep(0)
    setResults(null)

    // TODO: Connect to your Python models here for actual demo
    // This is just a placeholder demo mode
    
    alert('Demo mode will be connected to your Python models. This is just a UI placeholder.')
    
    setIsRunning(false)
  }

  return (
    <Card className="glass-morphism border-neon-pink/30">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center space-x-2">
          <Play className="h-6 w-6 text-neon-pink" />
          <span>Demo Mode</span>
        </CardTitle>
        <CardDescription>
          Experience our AI lie detection system with simulated data
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {!isRunning && !results && (
          <div className="text-center">
            <Button
              onClick={runDemo}
              variant="brand"
              size="lg"
              className="px-8"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Demo
            </Button>
          </div>
        )}

        {isRunning && (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-neon-pink mb-2">
                Running Analysis Demo...
              </h3>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-neon-pink h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((currentStep + 1) / demoSteps.length) * 100}%` }}
                />
              </div>
            </div>

            {demoSteps.map((step, index) => (
              <motion.div
                key={step.name}
                initial={{ opacity: 0.3 }}
                animate={{ 
                  opacity: index <= currentStep ? 1 : 0.3,
                  scale: index === currentStep ? 1.05 : 1
                }}
                transition={{ duration: 0.3 }}
                className={`flex items-center space-x-3 p-3 rounded-lg ${
                  index <= currentStep ? 'bg-neon-pink/10 border border-neon-pink/30' : 'bg-muted/20'
                }`}
              >
                {index < currentStep ? (
                  <CheckCircle className="h-5 w-5 text-neon-green" />
                ) : index === currentStep ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-neon-pink" />
                ) : (
                  <div className="h-5 w-5 rounded-full border-2 border-muted" />
                )}
                <span className={index <= currentStep ? 'text-neon-pink' : 'text-muted-foreground'}>
                  {step.name}
                </span>
              </motion.div>
            ))}
          </div>
        )}

        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-4"
          >
            <div className="text-center">
              <h3 className="text-lg font-semibold text-neon-green mb-2">
                Demo Complete!
              </h3>
              <p className="text-muted-foreground">
                All analysis methods have been simulated successfully
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-neon-blue/10 rounded-lg border border-neon-blue/30">
                <div className="text-sm text-neon-blue font-medium">Voice</div>
                <div className="text-lg font-bold">{results.voice.result}</div>
                <div className="text-xs text-muted-foreground">
                  {(results.voice.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center p-3 bg-neon-purple/10 rounded-lg border border-neon-purple/30">
                <div className="text-sm text-neon-purple font-medium">Face</div>
                <div className="text-lg font-bold">{results.face.result}</div>
                <div className="text-xs text-muted-foreground">
                  {(results.face.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center p-3 bg-neon-green/10 rounded-lg border border-neon-green/30">
                <div className="text-sm text-neon-green font-medium">Handwriting</div>
                <div className="text-lg font-bold">{results.handwriting.result}</div>
                <div className="text-xs text-muted-foreground">
                  {(results.handwriting.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center p-3 bg-neon-pink/10 rounded-lg border border-neon-pink/30">
                <div className="text-sm text-neon-pink font-medium">Final</div>
                <div className="text-lg font-bold">{results.fusion.finalResult}</div>
                <div className="text-xs text-muted-foreground">
                  {(results.fusion.overallConfidence * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="text-center">
              <Button
                onClick={() => {
                  setResults(null)
                  setCurrentStep(0)
                }}
                variant="outline"
              >
                Run Demo Again
              </Button>
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
