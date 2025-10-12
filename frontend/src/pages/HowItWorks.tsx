import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Mic, 
  Camera, 
  PenTool, 
  Type, 
  BarChart3,
  Brain,
  Zap,
  Target,
  ArrowRight,
  Play
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Button } from '../components/ui/button'

export const HowItWorks: React.FC = () => {
  const [activeDemo, setActiveDemo] = useState<string | null>(null)

  const analysisSteps = [
    {
      step: '01',
      title: 'Data Input',
      description: 'User provides voice recording, video, or text sample',
      icon: Target,
      color: 'white-700'
    },
    {
      step: '02',
      title: 'Feature Extraction',
      description: 'AI algorithms extract relevant patterns and characteristics',
      icon: Brain,
      color: 'white-700'
    },
    {
      step: '03',
      title: 'Model Analysis',
      description: 'Trained models analyze features for deception indicators',
      icon: Zap,
      color: 'white-700'
    },
    {
      step: '04',
      title: 'Result Generation',
      description: 'System provides truth/lie determination with confidence score',
      icon: BarChart3,
      color: 'white-700'
    }
  ]

  const voiceFeatures = [
    { name: 'Pitch Variation', description: 'Changes in fundamental frequency patterns' },
    { name: 'MFCC Coefficients', description: 'Mel-frequency cepstral coefficients for spectral analysis' },
    { name: 'Jitter & Shimmer', description: 'Voice quality measurements for irregularities' },
    { name: 'Spectral Features', description: 'Frequency domain characteristics of speech' },
    { name: 'Prosodic Features', description: 'Rhythm, stress, and intonation patterns' }
  ]

  const faceFeatures = [
    { name: 'Micro-expressions', description: 'Brief involuntary facial expressions' },
    { name: 'Eye Movement', description: 'Gaze patterns and blink rate analysis' },
    { name: 'Facial Action Units', description: 'Individual muscle movements in the face' },
    { name: 'Emotion Recognition', description: 'Detection of basic and complex emotions' },
    { name: 'Head Pose', description: 'Orientation and movement of the head' }
  ]

  const textFeatures = [
    { name: 'Lexical Richness', description: 'Diversity and sophistication of word usage' },
    { name: 'Sentiment Polarity', description: 'Emotional tone conveyed through the text' },
    { name: 'Syntactic Complexity', description: 'Depth and structure of grammatical constructions' },
    { name: 'Semantic Consistency', description: 'Logical coherence and meaning alignment across sentences' },
    { name: 'Deceptive Linguistic Cues', description: 'Use of uncertainty, negations, or distancing language patterns' }
  ]

  return (
    <div className="space-y-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <h1 className="text-5xl font-bold mb-4">
          <span className="text-white-900 font-bold">How It Works</span>
        </h1>
        <p className="text-xl text-white-700 max-w-3xl mx-auto">
          Understanding the science and technology behind our AI-driven lie detection system
        </p>
      </motion.div>

      {/* Process Overview */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <h2 className="text-3xl font-bold mb-8 text-center text-white-900">
          Analysis Process
        </h2>
        <div className="grid md:grid-cols-4 gap-6">
          {analysisSteps.map((step, index) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
            >
              <Card className={`glass-morphism border-${step.color}/30 text-center`}>
                <CardContent className="p-6">
                  <div className={`text-4xl font-bold text-${step.color}/30 mb-4`}>
                    {step.step}
                  </div>
                  <step.icon className={`h-12 w-12 text-${step.color} mx-auto mb-4`} />
                  <h3 className={`text-lg font-semibold text-${step.color} mb-2`}>
                    {step.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Detailed Analysis Methods */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <h2 className="text-3xl font-bold mb-8 text-center text-white-900">
          Analysis Methods
        </h2>
        <Tabs defaultValue="voice" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="voice" className="flex items-center space-x-2">
              <Mic className="h-4 w-4" />
              <span>Voice Analysis</span>
            </TabsTrigger>
            <TabsTrigger value="face" className="flex items-center space-x-2">
              <Camera className="h-4 w-4" />
              <span>Face Analysis</span>
            </TabsTrigger>
            <TabsTrigger value="text" className="flex items-center space-x-2">
              <Type className="h-4 w-4" />
              <span>Text Analysis</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="voice">
            <Card className="glass-morphism border-white-300/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Mic className="h-6 w-6 text-white-800" />
                  <span>Voice Pattern Analysis</span>
                </CardTitle>
                <CardDescription>
                  Our voice analysis system examines multiple acoustic and linguistic features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-4 text-white-900">Key Features Analyzed:</h4>
                    <div className="space-y-3">
                      {voiceFeatures.map((feature, index) => (
                        <div key={feature.name} className="p-3 bg-white-50 rounded-lg border border-white-200">
                          <h5 className="font-medium text-white-900">{feature.name}</h5>
                          <p className="text-sm text-white-600">{feature.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold text-white-900">How It Works:</h4>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">1</div>
                        <p className="text-sm text-white-700">Audio preprocessing and noise reduction</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">2</div>
                        <p className="text-sm text-white-700">Feature extraction using signal processing techniques</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">3</div>
                        <p className="text-sm text-white-700">Machine learning model analyzes patterns</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">4</div>
                        <p className="text-sm text-white-700">Confidence score calculation and result generation</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="face">
            <Card className="glass-morphism border-white-300/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Camera className="h-6 w-6 text-white-800" />
                  <span>Facial Expression Analysis</span>
                </CardTitle>
                <CardDescription>
                  Advanced computer vision techniques to detect micro-expressions and emotional cues
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-4 text-white-900">Key Features Analyzed:</h4>
                    <div className="space-y-3">
                      {faceFeatures.map((feature, index) => (
                        <div key={feature.name} className="p-3 bg-white-50 rounded-lg border border-white-200">
                          <h5 className="font-medium text-white-900">{feature.name}</h5>
                          <p className="text-sm text-white-600">{feature.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold text-white-900">Detection Process:</h4>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">1</div>
                        <p className="text-sm text-white-700">Face detection and landmark identification</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">2</div>
                        <p className="text-sm text-white-700">Real-time tracking of facial movements</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">3</div>
                        <p className="text-sm text-white-700">Micro-expression detection using temporal analysis</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">4</div>
                        <p className="text-sm text-white-700">Emotion classification and deception scoring</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="text">
            <Card className="glass-morphism border-white-300/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Type className="h-6 w-6 text-white-800" />
                  <span>Text Pattern Analysis</span>
                </CardTitle>
                <CardDescription>
                  Graphological analysis combined with machine learning for deception detection
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-4 text-white-900">Key Features Analyzed:</h4>
                    <div className="space-y-3">
                      {textFeatures.map((feature, index) => (
                        <div key={feature.name} className="p-3 bg-white-50 rounded-lg border border-white-200">
                          <h5 className="font-medium text-white-900">{feature.name}</h5>
                          <p className="text-sm text-white-600">{feature.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-4">
  <h4 className="font-semibold text-white-900">Analysis Pipeline:</h4>
  <div className="space-y-4">
    <div className="flex items-start space-x-3">
      <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">1</div>
      <p className="text-sm text-white-700">Text preprocessing including tokenization, stopword removal, and normalization</p>
    </div>
    <div className="flex items-start space-x-3">
      <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">2</div>
      <p className="text-sm text-white-700">Linguistic feature extraction covering syntax, semantics, and sentiment cues</p>
    </div>
    <div className="flex items-start space-x-3">
      <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">3</div>
      <p className="text-sm text-white-700">Computation of deceptive linguistic indicators such as uncertainty, negations, and emotional shifts</p>
    </div>
    <div className="flex items-start space-x-3">
      <div className="w-6 h-6 bg-white-700 rounded-full flex items-center justify-center text-xs font-bold text-white">4</div>
      <p className="text-sm text-white-700">Classification using trained NLP models to predict truthfulness scores</p>
    </div>
  </div>
</div>

                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.section>

      {/* Fusion Algorithm */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Card className="glass-morphism border-white-300/50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-2xl">
              <BarChart3 className="h-6 w-6 text-white-800" />
              <span>Multi-Modal Fusion Algorithm</span>
            </CardTitle>
            <CardDescription>
              Advanced ensemble method combining results from all three analysis types
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-semibold mb-4 text-white-900">Fusion Process:</h4>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white-200 rounded-full flex items-center justify-center">
                      <Mic className="h-4 w-4 text-white-700" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Voice confidence: 95%</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white-200 rounded-full flex items-center justify-center">
                      <Camera className="h-4 w-4 text-white-700" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Face confidence: 98%</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white-200 rounded-full flex items-center justify-center">
                      <Type className="h-4 w-4 text-white-700" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Text confidence: 97%</span>
                  </div>
                  <div className="border-t border-muted pt-4 mt-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-white-200 rounded-full flex items-center justify-center">
                        <BarChart3 className="h-4 w-4 text-white-700" />
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-semibold">Final result: 96% Truth</span>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-4 text-white-900">Algorithm Features:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Weighted ensemble based on individual method reliability</li>
                  <li>• Dynamic confidence adjustment based on data quality</li>
                  <li>• Conflict resolution when methods disagree</li>
                  <li>• Uncertainty quantification for borderline cases</li>
                  <li>• Continuous learning from new data</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  )
}
