import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

interface FAQItem {
  question: string
  answer: string
  category: 'general' | 'technical' | 'accuracy' | 'privacy'
}

export const FAQ: React.FC = () => {
  const [openItems, setOpenItems] = useState<number[]>([])

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const faqData: FAQItem[] = [
    {
      question: "How accurate is the AI lie detection system?",
      answer: "Our multi-modal system achieves an average accuracy of 85-92% across different test scenarios. The fusion of voice, facial, and handwriting analysis provides significantly higher accuracy than single-method approaches. However, accuracy can vary based on data quality, individual differences, and environmental factors.",
      category: "accuracy"
    },
    {
      question: "What types of lies can the system detect?",
      answer: "The system is designed to detect deceptive behavior patterns rather than specific types of lies. It can identify stress indicators, cognitive load changes, and behavioral anomalies that often accompany deception. It works best with deliberate deception rather than memory errors or subjective opinions.",
      category: "general"
    },
    {
      question: "Is my data secure and private?",
      answer: "Yes, we take privacy seriously. All analysis is performed locally when possible, and any data transmitted is encrypted. We don't store personal recordings or analysis results without explicit consent. Users have full control over their data and can delete it at any time.",
      category: "privacy"
    },
    {
      question: "Can the system work in real-time?",
      answer: "Yes, our voice and facial analysis modules can operate in real-time with minimal latency. Handwriting analysis requires a complete sample but processes quickly once uploaded. The fusion algorithm combines results within seconds of receiving all inputs.",
      category: "technical"
    },
    {
      question: "What equipment do I need to use the system?",
      answer: "For basic functionality, you need a computer with a microphone and camera. Higher quality equipment (professional microphones, HD cameras) can improve accuracy. For handwriting analysis, a smartphone camera or scanner is sufficient to capture clear images.",
      category: "technical"
    },
    {
      question: "How does the system handle different languages and accents?",
      answer: "Currently, the voice analysis is optimized for English but can work with other languages with reduced accuracy. We're continuously expanding language support. Facial and handwriting analysis are largely language-independent, making them more universally applicable.",
      category: "general"
    },
    {
      question: "Can the system be fooled or manipulated?",
      answer: "While no system is 100% foolproof, our multi-modal approach makes it significantly harder to deceive than single-method systems. The fusion algorithm is designed to detect inconsistencies between different analysis methods, making successful manipulation extremely difficult.",
      category: "accuracy"
    },
    {
      question: "Is this system legally admissible in court?",
      answer: "Legal admissibility varies by jurisdiction and specific use case. While our system provides scientific analysis, legal acceptance depends on local laws and court decisions. We recommend consulting with legal experts for specific applications in legal proceedings.",
      category: "general"
    },
    {
      question: "How long does analysis take?",
      answer: "Voice analysis: 2-5 seconds after recording. Facial analysis: Real-time during recording, 3-10 seconds for processing. Handwriting analysis: 5-15 seconds depending on image complexity. Fusion analysis: Additional 2-3 seconds to combine results.",
      category: "technical"
    },
    {
      question: "What factors can affect accuracy?",
      answer: "Several factors can impact accuracy: audio/video quality, lighting conditions, background noise, individual physiological differences, medical conditions affecting speech or movement, cultural differences in expression, and the subject's familiarity with the technology.",
      category: "accuracy"
    },
    {
      question: "Can I use this for employee screening?",
      answer: "While technically possible, we strongly recommend consulting legal and HR experts before using lie detection for employment decisions. Many jurisdictions have strict regulations about employee monitoring and privacy rights that must be considered.",
      category: "general"
    },
    {
      question: "How do you handle false positives and negatives?",
      answer: "Our system provides confidence scores rather than absolute determinations. We recommend using results as one factor among many in decision-making. The multi-modal approach helps reduce both false positives and negatives compared to single-method systems.",
      category: "accuracy"
    },
    {
      question: "Is training or calibration required for individual users?",
      answer: "No individual calibration is required. Our models are trained on diverse datasets to work across different populations. However, the system can adapt to individual patterns over time with repeated use, potentially improving accuracy for frequent users.",
      category: "technical"
    },
    {
      question: "What happens if one analysis method fails?",
      answer: "The system is designed to work with partial data. If one method fails (e.g., poor audio quality), the fusion algorithm adjusts weights and relies more heavily on the available methods. Results will indicate which methods were used and their individual confidence levels.",
      category: "technical"
    },
    {
      question: "Can I export or share analysis results?",
      answer: "Yes, you can export results in various formats (PDF reports, CSV data, JSON for integration). Sharing options include secure links with expiration dates and password protection. All exports maintain user privacy and data security standards.",
      category: "general"
    }
  ]

  const categories = {
    general: { name: 'General', color: 'blue-600' },
    technical: { name: 'Technical', color: 'purple-600' },
    accuracy: { name: 'Accuracy', color: 'green-600' },
    privacy: { name: 'Privacy', color: 'pink-600' }
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <h1 className="text-5xl font-bold mb-4">
          <span className="text-green-600">Frequently Asked Questions</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Find answers to common questions about our AI-driven lie detection system
        </p>
      </motion.div>

      {/* Category Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="grid md:grid-cols-4 gap-4"
      >
        {Object.entries(categories).map(([key, category]) => (
          <Card key={key} className={`glass-morphism border-${category.color}/30 text-center`}>
            <CardContent className="p-4">
              <h3 className={`font-semibold text-${category.color}`}>{category.name}</h3>
              <p className="text-sm text-muted-foreground">
                {faqData.filter(item => item.category === key).length} questions
              </p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* FAQ Items */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="space-y-4"
      >
        {faqData.map((item, index) => {
          const isOpen = openItems.includes(index)
          const category = categories[item.category]
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
            >
              <Card className={`glass-morphism border-${category.color}/30 cursor-pointer transition-all duration-200 ${
                isOpen ? `border-${category.color}/60` : ''
              }`}>
                <CardHeader 
                  className="pb-3"
                  onClick={() => toggleItem(index)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-start space-x-3">
                      <div className={`w-6 h-6 bg-${category.color}/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1`}>
                        <HelpCircle className={`h-3 w-3 text-${category.color}`} />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-left text-lg font-medium">
                          {item.question}
                        </CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-1 bg-${category.color}/20 text-${category.color} rounded-full`}>
                            {category.name}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      {isOpen ? (
                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <CardContent className="pt-0">
                      <div className="pl-9">
                        <p className="text-muted-foreground leading-relaxed">
                          {item.answer}
                        </p>
                      </div>
                    </CardContent>
                  </motion.div>
                )}
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Contact Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <Card className="glass-morphism border-blue-600/30 text-center">
          <CardHeader>
            <CardTitle className="text-2xl text-blue-600">
              Still Have Questions?
            </CardTitle>
            <CardDescription>
              Can't find what you're looking for? We're here to help!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              Contact our support team for personalized assistance with your specific use case or technical questions.
            </p>
            <div className="flex justify-center space-x-4">
              <a 
                href="/contact" 
                className="text-blue-600 hover:text-blue-600/80 transition-colors"
              >
                Contact Support
              </a>
              <span className="text-muted-foreground">•</span>
              <a 
                href="mailto:support@ai-lie-detection.com" 
                className="text-blue-600 hover:text-blue-600/80 transition-colors"
              >
                Email Us
              </a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
