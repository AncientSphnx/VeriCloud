import React, { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  FileText,
  Download,
  Filter,
  Search,
  Calendar,
  BarChart3,
  TrendingUp,
  Eye,
  RefreshCw,
  AlertCircle
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { formatDate } from '../lib'
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

interface DashboardData {
  period_days: number
  total_reports: number
  completed_reports: number
  completion_rate: number
  report_types: { [key: string]: number }
  average_confidence: number
  recent_reports: Report[]
}

export const Reports: React.FC = () => {
  const { user } = useAuth()
  const [reports, setReports] = useState<Report[]>([])
  const [filteredReports, setFilteredReports] = useState<Report[]>([])
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Fetch user reports and dashboard data
  useEffect(() => {
    if (user) {
      fetchReports()
      fetchDashboardData()
    }
  }, [user])

  // Filter reports when data or filters change
  useEffect(() => {
    if (reports.length > 0) {
      let filtered = reports

      // Filter by search term
      if (searchTerm) {
        filtered = filtered.filter(report =>
          report.report_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
          report.session_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
          JSON.stringify(report.data).toLowerCase().includes(searchTerm.toLowerCase())
        )
      }

      // Filter by type
      if (filterType !== 'all') {
      }

      // Filter by status
      if (filterStatus !== 'all') {
        filtered = filtered.filter(report => report.status === filterStatus)
      }

      setFilteredReports(filtered)
    }
  }, [reports, searchTerm, filterType, filterStatus])

  const fetchReports = useCallback(async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('token')
      if (!token) {
        setError('No authentication token found')
        return
      }

      const response = await api.reports.getUserReports(user.id, token, 100, 0)

      if (response.success) {
        setReports(response.reports || [])
      } else {
        setError(response.message || 'Failed to fetch reports')
      }
    } catch (error) {
      setError('Network error while fetching reports')
      console.error('Reports fetch error:', error)
    } finally {
      setLoading(false)
    }
  }, [user])
  useEffect(() => {
    if (user) {
      fetchReports()
      fetchDashboardData()
    }
  }, [user, fetchReports])

  const fetchDashboardData = async () => {
    if (!user) return

    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const response = await api.reports.getReportsDashboard(user.id, token, 30)

      if (response.success) {
        setDashboardData(response.dashboard)
      }
    } catch (error) {
      console.error('Dashboard data fetch error:', error)
    }
  }

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
      completed: 'text-green-600',
      processing: 'text-yellow-600',
      failed: 'text-red-600'
    }
    return colors[status as keyof typeof colors] || 'text-muted-foreground'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'processing': return '⏳'
      case 'failed': return '❌'
      default: return '❓'
    }
  }

  const exportReports = () => {
    if (filteredReports.length === 0) return

    const csvContent = [
      ['ID', 'Type', 'Status', 'Created', 'Session ID', 'Confidence Score', 'S3 File'],
      ...filteredReports.map(report => [
        report._id,
        report.report_type,
        report.status,
        formatDate(new Date(report.timestamp)),
        report.session_id,
        report.metadata?.confidence_score || 'N/A',
        report.s3_file_path || 'N/A'
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `lie-detection-reports-${user?.id}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Calculate stats from real data
  const stats = dashboardData ? {
    total: dashboardData.total_reports,
    completed: dashboardData.completed_reports,
    completionRate: dashboardData.completion_rate,
    avgConfidence: Math.round(dashboardData.average_confidence)
  } : {
    total: 0,
    completed: 0,
    completionRate: 0,
    avgConfidence: 0
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-muted-foreground">Loading reports...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-500" />
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={fetchReports} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-4xl font-bold mb-2">
          <span className="text-blue-600">Reports & Analytics</span>
        </h1>
        <p className="text-muted-foreground text-lg">
          View and analyze your lie detection history and performance metrics
        </p>
      </motion.div>

      {/* Statistics Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <Card className="glass-morphism border-blue-600/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Reports</p>
                <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600/60" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-morphism border-green-600/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600/60" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-morphism border-purple-600/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">{stats.completionRate.toFixed(1)}%</p>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-600/60" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-morphism border-pink-600/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Confidence</p>
                <p className="text-2xl font-bold text-pink-600">{stats.avgConfidence}%</p>
              </div>
              <Eye className="h-8 w-8 text-pink-600/60" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Card className="glass-morphism border-muted/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Filter className="h-5 w-5" />
              <span>Filters & Search</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search">Search</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Search reports..."
                    value={searchTerm}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="type-filter">Analysis Type</Label>
                <select
                  id="type-filter"
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full h-10 px-3 py-2 bg-background border border-input rounded-md text-sm"
                >
                  <option value="all">All Types</option>
                  <option value="voice_analysis">Voice Analysis</option>
                  <option value="face_analysis">Face Analysis</option>
                  <option value="text_analysis">Text Analysis</option>
                  <option value="combined_analysis">Combined Analysis</option>
                  <option value="session_summary">Session Summary</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="status-filter">Status</Label>
                <select
                  id="status-filter"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full h-10 px-3 py-2 bg-background border border-input rounded-md text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="processing">Processing</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              <div className="flex items-end space-x-2">
                <Button
                  onClick={exportReports}
                  variant="outline"
                  disabled={filteredReports.length === 0}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
                <Button
                  onClick={fetchReports}
                  variant="outline"
                  size="icon"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Reports Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <Card className="glass-morphism border-muted/30">
          <CardHeader>
            <CardTitle>Analysis Reports</CardTitle>
            <CardDescription>
              {filteredReports.length} of {reports.length} reports shown
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {filteredReports.map((report, index) => (
                <motion.div
                  key={report._id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 + index * 0.05 }}
                  className="p-6 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(report.status)}`} />
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className={`font-medium ${getTypeColor(report.report_type)}`}>
                            {report.report_type.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            #{report._id.slice(-8)}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(report.status)}`}>
                            {getStatusIcon(report.status)} {report.status}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(new Date(report.timestamp))}
                          • Session: {report.session_id.slice(-8)}
                        </p>
                        {report.metadata?.confidence_score && (
                          <p className="text-sm text-muted-foreground">
                            Confidence: {report.metadata.confidence_score}%
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      {report.s3_file_path && (
                        <Button variant="outline" size="sm" className="mb-2">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      )}
                      <p className="text-sm text-muted-foreground">
                        Created: {formatDate(new Date(report.timestamp))}
                      </p>
                    </div>
                  </div>

                  {/* Show sample data if available */}
                  {report.data && Object.keys(report.data).length > 0 && (
                    <div className="mt-4 p-3 bg-muted/30 rounded-md">
                      <p className="text-sm font-medium mb-2">Analysis Results:</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        {Object.entries(report.data).slice(0, 4).map(([key, value]) => (
                          <div key={key}>
                            <span className="text-muted-foreground">{key}:</span>
                            <span className="ml-1 font-mono">
                              {typeof value === 'object' ? JSON.stringify(value).slice(0, 30) + '...' : String(value).slice(0, 20)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>

            {filteredReports.length === 0 && (
              <div className="p-16 text-center">
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">
                  {reports.length === 0 ? 'No Reports Yet' : 'No Reports Match Filters'}
                </h3>
                <p className="text-muted-foreground">
                  {reports.length === 0
                    ? 'Start analyzing to see your reports here'
                    : 'Try adjusting your filters or search terms'
                  }
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
