import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI } from '../services/api'

interface User {
  id: string
  name: string
  username: string
  email: string
}

interface AuthContextType {
  user: User | null
  login: (username: string, email: string, password: string) => Promise<boolean>
  signup: (name: string, username: string, email: string, password: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing session on app load
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (username: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    
    try {
      const result = await authAPI.login(email, password);
      
      if (result.success) {
        const userData: User = {
          id: result.user.id,
          name: result.user.name,
          username: username, // Using provided username since backend doesn't store it
          email: result.user.email,
        };
        
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', result.token);
        setIsLoading(false);
        return true;
      } else {
        console.error('Login failed:', result.message);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      return false;
    }
  }

  const signup = async (name: string, username: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    
    try {
      const result = await authAPI.register(name, email, password);
      
      if (result.success) {
        const userData: User = {
          id: result.user.id,
          name: result.user.name,
          username: username, // Using provided username since backend doesn't store it
          email: result.user.email,
        };
        
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', result.token);
        setIsLoading(false);
        return true;
      } else {
        console.error('Signup failed:', result.message);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Signup error:', error);
      setIsLoading(false);
      return false;
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  const value: AuthContextType = {
    user,
    login,
    signup,
    logout,
    isLoading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
