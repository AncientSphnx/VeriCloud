import React from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'

import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout/Layout'
import { Landing } from './pages/Landing'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { Dashboard } from './pages/Dashboard'
import { VoiceAnalysis } from './pages/VoiceAnalysis'
import { FaceAnalysis } from './pages/FaceAnalysis'
import { TextAnalysis } from './pages/TextAnalysis'
import { FusionDashboard } from './pages/FusionDashboard'
import { Reports } from './pages/Reports'
import { Settings } from './pages/Settings'
import { About } from './pages/About'
import { HowItWorks } from './pages/HowItWorks'
import { FAQ } from './pages/FAQ'
import { Contact } from './pages/Contact'
import './index.css'

function AppContent() {
  const location = useLocation()
  
  
  // Pages that should be excluded from theme system
  const excludedPages = ['/', '/login', '/signup']
  const isExcludedPage = excludedPages.includes(location.pathname)
  
  // Apply theme to document element for non-excluded pages
  
  
  return (
    <div>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/voice-analysis" element={
          <ProtectedRoute>
            <Layout>
              <VoiceAnalysis />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/face-analysis" element={
          <ProtectedRoute>
            <Layout>
              <FaceAnalysis />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/text-analysis" element={
          <ProtectedRoute>
            <Layout>
              <TextAnalysis />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/fusion-dashboard" element={
          <ProtectedRoute>
            <Layout>
              <FusionDashboard />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/reports" element={
          <ProtectedRoute>
            <Layout>
              <Reports />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <Layout>
              <Settings />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/about" element={
          <ProtectedRoute>
            <Layout>
              <About />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/how-it-works" element={
          <ProtectedRoute>
            <Layout>
              <HowItWorks />
            </Layout>
          </ProtectedRoute>
        } />
        {/*<Route path="/faq" element={
          <ProtectedRoute>
            <Layout>
              <FAQ />
            </Layout>
          </ProtectedRoute>
        } />*/}
        {/*<Route path="/contact" element={
          <ProtectedRoute>
            <Layout>
              <Contact />
            </Layout>
          </ProtectedRoute>
        } />*/}
      </Routes>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
    
        <Router>
          <AppContent />
        </Router>
      
    </AuthProvider>
  )
}

export default App
