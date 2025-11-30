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
  AlertCircle,
  Trash2,
  AlertTriangle
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { formatDate } from '../lib/index'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Report {
  _id: string
  user_id: string
  session_id?: string
  module_type: 'text' | 'voice' | 'face'
  prediction: 'Truthful' | 'Deceptive'
  confidence: number
  confidence_percentage: number
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
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [reportToDelete, setReportToDelete] = useState<string | null>(null)

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
          report.module_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (report.session_id && report.session_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
          report.prediction.toLowerCase().includes(searchTerm.toLowerCase()) ||
          report.confidence_percentage.toString().includes(searchTerm.toLowerCase())
        )
      }

      // Filter by type
      if (filterType !== 'all') {
        filtered = filtered.filter(report => report.module_type === filterType)
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

      // Fetch reports directly from the simple reports endpoint
      const response = await fetch(`https://vericloud-db-wbhv.onrender.com/api/simple_reports/user/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const apiResponse = await response.json()
        console.log('📊 Reports API Response:', apiResponse)
        
        // Extract reports array from the response object
        const reportsArray = Array.isArray(apiResponse.reports) ? apiResponse.reports : []
        console.log('📊 Reports Array:', reportsArray)
        setReports(reportsArray)
      } else {
        console.error('❌ Reports API Error:', response.status, response.statusText)
        setError('Failed to fetch reports')
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

      // Fetch reports and calculate dashboard data
      const response = await fetch(`https://vericloud-db-wbhv.onrender.com/api/simple_reports/user/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const apiResponse = await response.json()
        console.log('📊 Dashboard API Response:', apiResponse)
        
        // Extract reports array from the response object
        const reportsArray = Array.isArray(apiResponse.reports) ? apiResponse.reports : []
        console.log('📊 Reports Array:', reportsArray)
        
        // Calculate dashboard stats
        const totalReports = reportsArray.length
        const truthfulCount = reportsArray.filter((r: Report) => r.prediction === 'Truthful').length
        const deceptiveCount = reportsArray.filter((r: Report) => r.prediction === 'Deceptive').length
        const completionRate = totalReports > 0 ? (truthfulCount + deceptiveCount) / totalReports * 100 : 0
        const averageConfidence = reportsArray.length > 0 
          ? reportsArray.reduce((sum: number, r: Report) => sum + r.confidence_percentage, 0) / reportsArray.length 
          : 0
        
        const reportTypes = reportsArray.reduce((acc: any, r: Report) => {
          acc[r.module_type] = (acc[r.module_type] || 0) + 1
          return acc
        }, {})

        const dashboardStats: DashboardData = {
          period_days: 30,
          total_reports: totalReports,
          completed_reports: truthfulCount + deceptiveCount,
          completion_rate: completionRate,
          report_types: reportTypes,
          average_confidence: averageConfidence,
          recent_reports: reportsArray.slice(0, 10)
        }

        setDashboardData(dashboardStats)
      }
    } catch (error) {
      console.error('Dashboard data fetch error:', error)
    }
  }

  const getTypeColor = (type: string) => {
    const colors = {
      voice: 'text-blue-600',
      face: 'text-purple-600',
      text: 'text-green-600'
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
      ['ID', 'Module Type', 'Prediction', 'Confidence', 'Status', 'Created', 'Session ID'],
      ...filteredReports.map(report => [
        report._id,
        report.module_type,
        report.prediction,
        `${report.confidence_percentage}%`,
        report.status,
        formatDate(new Date(report.timestamp)),
        report.session_id || 'N/A'
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

  // Delete single report
  const deleteReport = async (reportId: string) => {
    if (!user) return

    try {
      setDeleteLoading(reportId)
      const token = localStorage.getItem('token')
      if (!token) {
        setError('No authentication token found')
        return
      }

      const response = await fetch(`https://vericloud-db-wbhv.onrender.com/api/simple_reports/${reportId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        // Remove from local state
        setReports(prev => prev.filter(report => report._id !== reportId))
        setReportToDelete(null)
        setShowDeleteConfirm(false)
      } else {
        console.error('❌ Delete API Error:', response.status, response.statusText)
        setError('Failed to delete report')
      }
    } catch (error) {
      setError('Network error while deleting report')
      console.error('Delete error:', error)
    } finally {
      setDeleteLoading(null)
    }
  }

  // Delete all reports
  const deleteAllReports = async () => {
    if (!user) return

    try {
      setDeleteLoading('all')
      const token = localStorage.getItem('token')
      if (!token) {
        setError('No authentication token found')
        return
      }

      const response = await fetch(`https://vericloud-db-wbhv.onrender.com/api/simple_reports/user/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        // Clear all reports from local state
        setReports([])
        setReportToDelete(null)
        setShowDeleteConfirm(false)
      } else {
        console.error('❌ Delete All API Error:', response.status, response.statusText)
        setError('Failed to delete all reports')
      }
    } catch (error) {
      setError('Network error while deleting all reports')
      console.error('Delete all error:', error)
    } finally {
      setDeleteLoading(null)
    }
  }

  // Handle delete confirmation
  const handleDeleteClick = (reportId: string | 'all') => {
    setReportToDelete(reportId)
    setShowDeleteConfirm(true)
  }

  const confirmDelete = () => {
    if (reportToDelete === 'all') {
      deleteAllReports()
    } else if (reportToDelete) {
      deleteReport(reportToDelete)
    }
  }

  const cancelDelete = () => {
    setReportToDelete(null)
    setShowDeleteConfirm(false)
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
                  <option value="voice">Voice</option>
                  <option value="face">Face</option>
                  <option value="text">Text</option>
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
                  onClick={() => handleDeleteClick('all')}
                  variant="outline"
                  disabled={filteredReports.length === 0 || deleteLoading === 'all'}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {deleteLoading === 'all' ? 'Deleting...' : 'Delete All'}
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
                          <span className={`font-medium ${getTypeColor(report.module_type)}`}>
                            {report.module_type.replace('_', ' ').toUpperCase()}
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
                          {report.session_id && ` • Session: ${report.session_id.slice(-8)}`}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Prediction: {report.prediction} • Confidence: {report.confidence_percentage}%
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-2 mb-2">
                        <Button
                          onClick={() => handleDeleteClick(report._id)}
                          variant="outline"
                          size="sm"
                          disabled={deleteLoading === report._id}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                          {deleteLoading === report._id ? '...' : ''}
                        </Button>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Created: {formatDate(new Date(report.timestamp))}
                      </p>
                    </div>
                  </div>

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

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-background border rounded-lg p-6 max-w-md mx-4"
          >
            <div className="flex items-center space-x-3 mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <h3 className="text-lg font-semibold">
                {reportToDelete === 'all' ? 'Delete All Reports' : 'Delete Report'}
              </h3>
            </div>
            
            <p className="text-muted-foreground mb-6">
              {reportToDelete === 'all' 
                ? 'Are you sure you want to delete all your reports? This action cannot be undone.'
                : 'Are you sure you want to delete this report? This action cannot be undone.'
              }
            </p>
            
            <div className="flex space-x-3">
              <Button
                onClick={cancelDelete}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={confirmDelete}
                variant="destructive"
                className="flex-1"
                disabled={deleteLoading !== null}
              >
                {deleteLoading ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
