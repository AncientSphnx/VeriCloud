import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Home, 
  Mic, 
  Camera, 
  Type, 
  BarChart3, 
  FileText, 
  Info, 
  HelpCircle, 
  Mail,
  LogOut,
  User
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/button'

const sidebarItems = [
  { path: '/dashboard', icon: Home, label: 'Dashboard' },
  { path: '/voice-analysis', icon: Mic, label: 'Voice Analysis' },
  { path: '/face-analysis', icon: Camera, label: 'Face Analysis' },
  { path: '/text-analysis', icon: Type, label: 'Text Analysis' },
  { path: '/fusion-dashboard', icon: BarChart3, label: 'Fusion Analysis' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/about', icon: Info, label: 'About' },
  { path: '/how-it-works', icon: HelpCircle, label: 'How It Works' },
  //{ path: '/faq', icon: HelpCircle, label: 'FAQ' },
  //{ path: '/contact', icon: Mail, label: 'Contact' },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  darkMode: boolean
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, darkMode }) => {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024)

  useEffect(() => {
    const handleResize = () => setIsDesktop(window.innerWidth >= 1024)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ x: isDesktop ? 0 : (isOpen ? 0 : '-100%') }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 h-full w-64 bg-card border-r border-border z-50 lg:relative lg:z-auto"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-border">
          <Link to="/about" onClick={onClose} className="block">
            <img 
              src={darkMode ? "/logo1.png" : "/logo4.png"} 
              alt="AI Lie Detection Logo" 
              className="w-full h-auto object-contain" 
            />
          </Link>
            {user && (
              <div className="mt-2 flex items-center space-x-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{user.name}</span>
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {sidebarItems.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <Button
              variant="ghost"
              className="w-full justify-start text-muted-foreground hover:text-foreground"
              onClick={logout}
            >
              <LogOut className="h-4 w-4 mr-3" />
              Logout
            </Button>
          </div>
        </div>
      </motion.div>
    </>
  )
}
