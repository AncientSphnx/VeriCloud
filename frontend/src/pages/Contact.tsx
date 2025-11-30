import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Mail, 
  Phone, 
  MapPin, 
  Send,
  Github,
  Linkedin,
  Twitter,
  MessageSquare
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'

export const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setSubmitted(true)
    setIsSubmitting(false)
    
    // Reset form after 3 seconds
    setTimeout(() => {
      setSubmitted(false)
      setFormData({ name: '', email: '', subject: '', message: '' })
    }, 3000)
  }

  const contactInfo = [
    {
      icon: Mail,
      title: 'Email',
      value: 'support@ai-lie-detection.com',
      description: 'Send us an email anytime',
      color: 'blue-600'
    },
    {
      icon: Phone,
      title: 'Phone',
      value: '+1 (555) 123-4567',
      description: 'Mon-Fri from 8am to 6pm',
      color: 'purple-600'
    },
    {
      icon: MapPin,
      title: 'Office',
      value: 'San Francisco, CA',
      description: 'Silicon Valley Tech Hub',
      color: 'green-600'
    },
    {
      icon: MessageSquare,
      title: 'Live Chat',
      value: 'Available 24/7',
      description: 'Instant support online',
      color: 'pink-600'
    }
  ]

  const socialLinks = [
    { icon: Github, name: 'GitHub', url: '#', color: 'text-gray-400 hover:text-white' },
    { icon: Linkedin, name: 'LinkedIn', url: '#', color: 'text-blue-400 hover:text-blue-300' },
    { icon: Twitter, name: 'Twitter', url: '#', color: 'text-sky-400 hover:text-sky-300' },
    { icon: Mail, name: 'Email', url: '#', color: 'text-red-400 hover:text-red-300' }
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
          <span className="text-blue-600">Get In Touch</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Have questions about our AI lie detection system? We'd love to hear from you. 
          Send us a message and we'll respond as soon as possible.
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-12">
        {/* Contact Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="glass-morphism border-blue-600/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Send className="h-6 w-6 text-blue-600" />
                <span>Send us a Message</span>
              </CardTitle>
              <CardDescription>
                Fill out the form below and we'll get back to you within 24 hours
              </CardDescription>
            </CardHeader>
            <CardContent>
              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-8"
                >
                  <div className="w-16 h-16 bg-green-200 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-green-600 mb-2">
                    Message Sent!
                  </h3>
                  <p className="text-muted-foreground">
                    Thank you for contacting us. We'll get back to you soon.
                  </p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Name *</Label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        placeholder="Your full name"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email *</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="your.email@example.com"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject">Subject *</Label>
                    <Input
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      placeholder="What is this regarding?"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">Message *</Label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleInputChange}
                      placeholder="Tell us more about your inquiry..."
                      rows={6}
                      className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="brand"
                    size="lg"
                    className="w-full"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Contact Information */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="space-y-6"
        >
          <h2 className="text-2xl font-semibold text-purple-600 mb-6">
            Contact Information
          </h2>
          
          <div className="grid gap-6">
            {contactInfo.map((info, index) => (
              <motion.div
                key={info.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              >
                <Card className={`glass-morphism border-${info.color}/30`}>
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className={`w-12 h-12 bg-${info.color}/20 rounded-lg flex items-center justify-center flex-shrink-0`}>
                        <info.icon className={`h-6 w-6 text-${info.color}`} />
                      </div>
                      <div>
                        <h3 className={`font-semibold text-${info.color} mb-1`}>
                          {info.title}
                        </h3>
                        <p className="font-medium mb-1">{info.value}</p>
                        <p className="text-sm text-muted-foreground">
                          {info.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <Card className="glass-morphism border-muted/30">
              <CardHeader>
                <CardTitle>Follow Us</CardTitle>
                <CardDescription>
                  Stay updated with our latest developments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-4">
                  {socialLinks.map((social, index) => (
                    <motion.a
                      key={social.name}
                      href={social.url}
                      className={`w-10 h-10 rounded-lg bg-accent/50 flex items-center justify-center transition-colors ${social.color}`}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <social.icon className="h-5 w-5" />
                    </motion.a>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Additional Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <Card className="glass-morphism border-green-600/30">
              <CardHeader>
                <CardTitle className="text-green-600">Quick Support</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Response Time:</span>
                    <span className="text-green-600">&lt; 24 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Support Hours:</span>
                    <span>24/7 Online</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Languages:</span>
                    <span>English, Spanish</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>

      {/* FAQ Link */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.9 }}
        className="text-center"
      >
        <Card className="glass-morphism border-purple-600/30">
          <CardContent className="p-8">
            <h3 className="text-xl font-semibold mb-2">
              Looking for Quick Answers?
            </h3>
            <p className="text-muted-foreground mb-4">
              Check out our comprehensive FAQ section for immediate answers to common questions.
            </p>
            <Button variant="outline" asChild>
              <a href="/faq">
                View FAQ
              </a>
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
