import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Mic, 
  Camera, 
  Type, 
  BarChart3,
  ChevronRight,
  Home
} from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'

const navigationItems = [
  {
    path: '/voice-analysis',
    label: 'Voice Analysis',
    icon: Mic,
    description: 'Audio-based detection'
  },
  {
    path: '/face-analysis',
    label: 'Face Analysis',
    icon: Camera,
    description: 'Video-based detection'
  },
  {
    path: '/text-analysis',
    label: 'Text Analysis',
    icon: Type,
    description: 'Text-based detection'
  },
  {
    path: '/fusion-dashboard',
    label: 'Fusion Dashboard',
    icon: BarChart3,
    description: 'Combined analysis'
  }
]

export const AnalysisNavigation: React.FC = () => {
  const location = useLocation()

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mb-8"
    >
      <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-display font-semibold text-blue-600">
              Detection Methods
            </h3>
            <Link to="/dashboard">
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <Home className="h-4 w-4" />
                Return to Dashboard
              </Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link key={item.path} to={item.path}>
                  <div className={`group p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
                    isActive
                      ? 'bg-blue-600 border-blue-600'
                      : 'border-input hover:bg-blue-600 hover:border-blue-600'
                  }`}>
                    <div className="flex flex-col items-center gap-2">
                      <Icon className={`h-6 w-6 transition-colors ${
                        isActive ? 'text-white' : 'text-blue-600'
                      } group-hover:text-yellow-300`} />
                      <div className="text-center">
                        <div className={`font-medium text-sm ${
                          isActive ? 'text-white' : 'text-foreground group-hover:text-white hover:text-white'
                        }`}>
                          {item.label}
                        </div>
                        <div className={`text-xs ${
                          isActive ? 'text-blue-100' : 'text-muted-foreground group-hover:text-blue-100 hover:text-blue-100'
                        }`}>
                          {item.description}
                        </div>
                      </div>
                      {isActive && (
                        <ChevronRight className="h-4 w-4 text-white" />
                      )}
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
