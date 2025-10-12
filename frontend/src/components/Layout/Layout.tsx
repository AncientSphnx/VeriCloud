import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface LayoutProps {
  children?: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)
  const toggleDarkMode = () => setDarkMode(!darkMode)

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen bg-background text-foreground">
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} darkMode={darkMode} />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header 
            onMenuClick={toggleSidebar}
            darkMode={darkMode}
            onDarkModeToggle={toggleDarkMode}
          />
          
          <main className="flex-1 overflow-auto bg-muted/20">
            <div className="container mx-auto p-4 md:p-6 max-w-7xl">
              {children || <Outlet />}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
