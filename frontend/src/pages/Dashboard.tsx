import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Mic,
  Camera,
  Type,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  RefreshCw,
  AlertCircle,
  FileText,
  Activity
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Report {
  _id: string
  user_id: string
  session_id: string
  report_type: 'voice_analysis' | 'face_analysis' | 'text_analysis' | 'combined_analysis' | 'session_summary'
  data: any
  s3_file_path?: string
  timestamp: string
  status: 'completed' | 'processing' | 'failed'
  metadata?: {
    confidence_score?: number
    processing_time_ms?: number
    data_sources?: string[]
  }
}

interface DashboardStats {
  total_reports: number
  completed_reports: number
  completion_rate: number
  average_confidence: number
  report_types: { [key: string]: number }
  recent_reports?: Report[]
}

export const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [recentReports, setRecentReports] = useState<Report[]>([])
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = useCallback(async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('token')
      if (!token) {
        setError('No authentication token found')
        return
      }

      // Fetch dashboard data (recent reports and stats)
      const dashboardResponse = await api.reports.getReportsDashboard(user.id, token, 7)

      if (dashboardResponse.success) {
        setDashboardStats(dashboardResponse.dashboard)
        setRecentReports(dashboardResponse.dashboard.recent_reports || [])
      } else {
        setError(dashboardResponse.message || 'Failed to fetch dashboard data')
      }
    } catch (error) {
      setError('Network error while fetching dashboard data')
      console.error('Dashboard fetch error:', error)
    } finally {
      setLoading(false)
    }
  }, [user])

  // Fetch dashboard data on component mount
  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user, fetchDashboardData])

  const getTypeColor = (type: string) => {
    const colors = {
      voice_analysis: 'text-blue-600',
      face_analysis: 'text-purple-600',
      text_analysis: 'text-green-600',
      combined_analysis: 'text-pink-600',
      session_summary: 'text-yellow-600'
    }
    return colors[type as keyof typeof colors] || 'text-muted-foreground'
  }

  const getStatusColor = (status: string) => {
    const colors = {
      completed: 'bg-green-500',
      processing: 'bg-yellow-500',
      failed: 'bg-red-500'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-500'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'processing': return '⏳'
      case 'failed': return '❌'
      default: return '❓'
    }
  }

  // Calculate stats from real data
  const stats = dashboardStats ? [
    {
      label: 'Total Reports',
      value: dashboardStats.total_reports.toString(),
      icon: FileText,
      color: 'text-blue-600'
    },
    {
      label: 'This Week',
      value: dashboardStats.recent_reports?.length.toString() || '0',
      icon: Clock,
      color: 'text-green-600'
    },
    {
      label: 'Success Rate',
      value: `${dashboardStats.completion_rate.toFixed(1)}%`,
      icon: CheckCircle,
      color: 'text-purple-600'
    },
    {
      label: 'Avg Confidence',
      value: `${Math.round(dashboardStats.average_confidence)}%`,
      icon: TrendingUp,
      color: 'text-pink-600'
    }
  ] : [
    { label: 'Total Reports', value: '0', icon: FileText, color: 'text-muted-foreground' },
    { label: 'This Week', value: '0', icon: Clock, color: 'text-muted-foreground' },
    { label: 'Success Rate', value: '0%', icon: CheckCircle, color: 'text-muted-foreground' },
    { label: 'Avg Confidence', value: '0%', icon: TrendingUp, color: 'text-muted-foreground' }
  ]

  if (loading) {
    return (
      <div className="w-full">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-500" />
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={fetchDashboardData} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold mb-2">
          Welcome back, <span className="text-blue-600 font-display font-semibold">{user?.name || user?.username}</span>
        </h1>
        <p className="text-muted-foreground text-lg">
          Ready to analyze truth patterns with AI-powered detection
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        {stats.map((stat, index) => (
          <Card key={stat.label} className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className={`text-2xl font-display font-semibold ${stat.color}`}>{stat.value}</p>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.color.replace('text-', 'text-').replace('-600', '/60')}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mb-8"
      >
        <h2 className="text-2xl font-display font-semibold mb-6 text-purple-600">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: Mic,
              title: 'Voice Analysis',
              description: 'Analyze voice patterns for deception detection',
              path: '/voice-analysis',
              color: 'blue'
            },
            {
              icon: Camera,
              title: 'Face Analysis',
              description: 'Detect micro-expressions and facial cues',
              path: '/face-analysis',
              color: 'purple'
            },
            {
              icon: Type,
              title: 'Text Analysis',
              description: 'Analyze written text for deception patterns',
              path: '/text-analysis',
              color: 'green'
            },
            {
              icon: Activity,
              title: 'View Reports',
              description: 'Access your analysis history and reports',
              path: '/reports',
              color: 'pink'
            }
          ].map((action, index) => (
            <motion.div
              key={action.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
            >
              <Link to={action.path}>
                <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30 hover:border-blue-600/60 transition-all duration-300 cursor-pointer group">
                  <CardHeader className="text-center">
                    <action.icon className="h-12 w-12 text-blue-600 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
                    <CardTitle className="text-lg font-display font-semibold">{action.title}</CardTitle>
                    <CardDescription>{action.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <Button variant="ghost" className="w-full">
                      Start Analysis
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Recent Reports */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-display font-semibold text-green-600">
            Recent Reports
          </h2>
          <div className="flex space-x-2">
            <Button onClick={fetchDashboardData} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Link to="/reports">
              <Button variant="outline">View All</Button>
            </Link>
          </div>
        </div>

        <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-green-600/30">
          <CardContent className="p-0">
            {recentReports.length > 0 ? (
              <div className="divide-y divide-border">
                {recentReports.map((report, index) => (
                  <motion.div
                    key={report._id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                    className="p-6 hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(report.status)}`} />
                        <div>
                          <div className="flex items-center space-x-2">
                            <p className={`font-medium ${getTypeColor(report.report_type)}`}>
                              {report.report_type.replace('_', ' ').toUpperCase()}
                            </p>
                            <span className="text-xs text-muted-foreground">
                              #{report._id.slice(-8)}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {new Date(report.timestamp).toLocaleDateString()} • {new Date(report.timestamp).toLocaleTimeString()}
                          </p>
                          {report.metadata?.confidence_score && (
                            <p className="text-sm text-muted-foreground">
                              Confidence: {report.metadata.confidence_score}%
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-display font-semibold ${
                          report.status === 'completed' ? 'text-green-600' : 'text-yellow-500'
                        }`}>
                          {getStatusIcon(report.status)} {report.status}
                        </p>
                        {report.s3_file_path && (
                          <Button variant="outline" size="sm" className="mt-2">
                            <FileText className="h-4 w-4 mr-2" />
                            View Report
                          </Button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-16 text-center">
                <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No Reports Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start analyzing to see your reports here
                </p>
                <Link to="/voice-analysis">
                  <Button>
                    <Mic className="h-4 w-4 mr-2" />
                    Start Voice Analysis
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
