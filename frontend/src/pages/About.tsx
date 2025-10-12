import React from 'react'
import { motion } from 'framer-motion'
import { 
  Target, 
  Users, 
  Lightbulb, 
  Award,
  Github,
  Linkedin,
  Mail
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'

export const About: React.FC = () => {
  const teamMembers = [
    {
      name: 'Numan',
      role: 'Voice Recognition',
    },
    {
      name: 'Gagan Kumar',
      role: 'Face Recognition',
    },
    {
      name: 'Niharaka S P',
      role: 'Cloud Integration & Deployment',
    },
    {
      name: 'Pretty Evanglin',
      role: 'Text Recognition',
    }
  ]

  /*const timeline = [
    {
      phase: 'Research Phase',
      period: 'Jan 2023 - Mar 2023',
      description: 'Literature review and feasibility study on multi-modal lie detection',
      color: 'white-700'
    },
    {
      phase: 'Data Collection',
      period: 'Apr 2023 - Jun 2023',
      description: 'Gathered diverse datasets for voice, facial, and handwriting analysis',
      color: 'white-700'
    },
    {
      phase: 'Model Development',
      period: 'Jul 2023 - Sep 2023',
      description: 'Developed and trained individual AI models for each detection method',
      color: 'white-700'
    },
    {
      phase: 'Fusion Algorithm',
      period: 'Oct 2023 - Dec 2023',
      description: 'Created advanced fusion algorithm to combine multiple detection methods',
      color: 'white-700'
    },
    {
      phase: 'System Integration',
      period: 'Jan 2024 - Mar 2024',
      description: 'Built user-friendly interface and integrated all components',
      color: 'white-700'
    },
    {
      phase: 'Testing & Validation',
      period: 'Apr 2024 - Present',
      description: 'Extensive testing and continuous improvement based on user feedback',
      color: 'white-700'
    }
  ]*/

  return (
    <div className="space-y-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <h1 className="text-5xl font-bold mb-4">
          <span className="text-black-900 font-bold">About Our Project</span>
        </h1>
        <p className="text-xl text-black-700 max-w-3xl mx-auto">
          Revolutionizing truth detection through cutting-edge AI technology and multi-modal analysis
        </p>
      </motion.div>

      {/* Problem Statement */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <Card className="glass-morphism border-blue-300/50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-2xl">
              <Target className="h-6 w-6 text-blue-700" />
              <span>The Problem We're Solving</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-lg text-white-800">
              Traditional lie detection methods rely on single modalities and often lack accuracy and reliability. 
              Polygraph tests, while widely used, have significant limitations and are not admissible in many legal contexts.
            </p>
            <p className="text-lg text-white-800">
              Our society needs more accurate, non-invasive, and scientifically sound methods for truth verification 
              in various applications including law enforcement, security screening, and psychological assessment.
            </p>
          </CardContent>
        </Card>
      </motion.section>

      {/* Our Solution */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Card className="glass-morphism border-white-300/50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-2xl">
              <Lightbulb className="h-6 w-6 text-white-700" />
              <span>Our Innovative Solution</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-lg text-white-800">
              We've developed a comprehensive AI-driven system that combines three distinct analysis methods:
            </p>
            <div className="grid md:grid-cols-4 gap-6 mt-6">
              <div className="text-center p-4 bg-white-50 rounded-lg border border-white-200">
                <h3 className="font-semibold text-white-900 mb-2">Voice Analysis</h3>
                <p className="text-sm text-white-600">
                  Analyzes pitch, tone, MFCC coefficients, jitter, and shimmer patterns
                </p>
              </div>
              <div className="text-center p-4 bg-white-50 rounded-lg border border-white-200">
                <h3 className="font-semibold text-white-900 mb-2">Facial Recognition</h3>
                <p className="text-sm text-white-600">
                  Detects micro-expressions, eye movements, and emotional patterns
                </p>
              </div>
              <div className="text-center p-4 bg-white-50 rounded-lg border border-white-200">
                <h3 className="font-semibold text-white-900 mb-2">Text Analysis</h3>
                <p className="text-sm text-white-600">
                  Examines pressure, slant, spacing, and other graphological features
                </p>
              </div>
              <div className="flex item-center justify-center">
                <div className="text-center p-4 bg-white-50 rounded-lg border border-white-200">
                  <h3 className="font-semibold text-white-900 mb-2">Fusion</h3>
                    <p className="text-sm text-white-600">
                      Examines pressure, slant, spacing, and other graphological features
                    </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.section>

      {/* Project Timeline 
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <h2 className="text-3xl font-bold mb-8 text-center text-white-900">
          Project Timeline
        </h2>
        <div className="space-y-6">
          {timeline.map((item, index) => (
            <motion.div
              key={item.phase}
              initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
            >
              <Card className="glass-morphism border-white-300/50">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-white-900">
                      {item.phase}
                    </h3>
                    <span className="text-sm text-white-600">
                      {item.period}
                    </span>
                  </div>
                  <p className="text-white-700">{item.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>*/}

      {/* Team Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <h2 className="text-3xl font-bold mb-8 text-center text-white-900">
          Meet Our Team
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {teamMembers.map((member, index) => (
            <motion.div
              key={member.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
            >
              <Card className="glass-morphism border-muted/30 text-center">
                <CardContent className="p-6">
                  <div className="w-24 h-24 bg-gradient-to-br from-white-100 to-white-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <Users className="h-12 w-12 text-white-700" />
                  </div>
                  <h3 className="font-semibold text-lg mb-1 text-white-900">{member.name}</h3>
                  <p className="text-white-700 text-sm mb-3">{member.role}</p>
                  <div className="flex justify-center space-x-2">
                    <Button variant="ghost" size="sm">
                      <Linkedin className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Github className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Mail className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Impact & Future */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <Card className="glass-morphism border-white-300/50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-2xl">
              <Award className="h-6 w-6 text-white-700" />
              <span>Impact & Future Vision</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-lg text-white-800">
              Our AI-driven lie detection system has the potential to revolutionize various fields:
            </p>
            <ul className="list-disc list-inside space-y-2 text-white-700">
              <li>Enhanced security screening at airports and border crossings</li>
              <li>Improved accuracy in criminal investigations and legal proceedings</li>
              <li>Better assessment tools for psychological and therapeutic applications</li>
              <li>Corporate fraud detection and employee screening</li>
              <li>Research advancement in behavioral psychology and neuroscience</li>
            </ul>
            <p className="text-lg mt-6 text-white-800">
              We're committed to continuous improvement, ethical AI development, and making truth detection 
              more accessible, accurate, and reliable for legitimate applications worldwide.
            </p>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  )
}
