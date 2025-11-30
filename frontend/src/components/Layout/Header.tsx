import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Menu, Moon, Sun, Settings, Play } from 'lucide-react'
import { Button } from '../ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog'
import { useAuth } from '../../contexts/AuthContext'
import { DemoMode } from '../DemoMode'

interface HeaderProps {
  onMenuClick: () => void
  darkMode: boolean
  onDarkModeToggle: () => void
}

export const Header: React.FC<HeaderProps> = ({ 
  onMenuClick, 
  darkMode, 
  onDarkModeToggle 
}) => {
  const { user } = useAuth()
  const [demoOpen, setDemoOpen] = useState(false)

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        
        
      </div>

      <div className="flex items-center space-x-2">
        {/*<Dialog open={demoOpen} onOpenChange={setDemoOpen}>
          <DialogTrigger asChild>
            <Button
              variant="brand"
              size="sm"
              className="text-xs"
            >
              <Play className="h-3 w-3 mr-1" />
              Demo
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>AI Lie Detection Demo</DialogTitle>
            </DialogHeader>
            <DemoMode onDemoComplete={() => setDemoOpen(false)} />
          </DialogContent>
        </Dialog>*/}

        <Button
          variant="ghost"
          size="icon"
          onClick={onDarkModeToggle}
          className="text-muted-foreground hover:text-foreground"
        >
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        
        <Link to="/settings">
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-foreground"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </Link>
      </div>
    </header>
  )
}
