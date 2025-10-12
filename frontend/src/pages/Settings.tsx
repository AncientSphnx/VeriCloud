import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Shield,
  Palette,
  Save,
  ArrowLeft,
  Eye,
  EyeOff,
  Download,
  Trash2,
  CheckCircle
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../services/api'

export const Settings: React.FC = () => {
  const { user } = useAuth()

  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    name: user?.name || ''
  })

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })

  const [settings, setSettings] = useState({
    notifications: true,
    autoSave: true,
    confidenceThreshold: 75,
    language: 'en'
  })

  const [isLoading, setIsLoading] = useState({
    profile: false,
    password: false,
    export: false,
    delete: false
  })

  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)

  const handleProfileUpdate = async () => {
    setIsLoading(prev => ({ ...prev, profile: true }))
    setMessage(null)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      setMessage({ type: 'success', text: 'Profile updated successfully!' })
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' })
    } finally {
      setIsLoading(prev => ({ ...prev, profile: false }))
    }
  }

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match.' })
      return
    }

    if (passwordData.newPassword.length < 6) {
      setMessage({ type: 'error', text: 'Password must be at least 6 characters long.' })
      return
    }

    setIsLoading(prev => ({ ...prev, password: true }))
    setMessage(null)

    try {
      // Get the user's token from localStorage
      const token = localStorage.getItem('token')

      if (!token) {
        setMessage({ type: 'error', text: 'Authentication required. Please log in again.' })
        return
      }

      // Make the real API call to change password
      const result = await authAPI.changePassword(passwordData.currentPassword, passwordData.newPassword, token)

      if (result.success) {
        setPasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        })
        setMessage({ type: 'success', text: 'Password changed successfully!' })
      } else {
        setMessage({ type: 'error', text: result.message || 'Failed to change password. Please check your current password.' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please check your connection and try again.' })
    } finally {
      setIsLoading(prev => ({ ...prev, password: false }))
    }
  }

  const handleExportData = async () => {
    setIsLoading(prev => ({ ...prev, export: true }))
    setMessage(null)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Create sample data export
      const exportData = {
        profile: profileData,
        settings: settings,
        exportDate: new Date().toISOString(),
        analyses: []
      }

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `vericloud-data-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setMessage({ type: 'success', text: 'Data exported successfully!' })
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to export data. Please try again.' })
    } finally {
      setIsLoading(prev => ({ ...prev, export: false }))
    }
  }

  const handleDeleteAccountClick = () => {
    setShowDeleteConfirmation(true)
  }

  const handleDeleteAccountConfirm = async () => {
    setShowDeleteConfirmation(false)
    setIsLoading(prev => ({ ...prev, delete: true }))
    setMessage(null)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))

      setMessage({ type: 'success', text: 'Account deletion request submitted. You will receive a confirmation email.' })
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to process account deletion. Please try again.' })
    } finally {
      setIsLoading(prev => ({ ...prev, delete: false }))
    }
  }

  const handleDeleteAccountCancel = () => {
    setShowDeleteConfirmation(false)
  }

  const handleSave = () => {
    setMessage({ type: 'success', text: 'Settings saved successfully!' })
    setTimeout(() => setMessage(null), 3000)
  }

  

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-display font-bold mb-4 text-blue-600">
            Settings
          </h1>
          <p className="text-muted-foreground text-lg">
            Manage your account preferences and application settings
          </p>
        </div>
        <Link to="/dashboard">
          <Button variant="outline" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Profile Settings */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-blue-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-blue-600" />
                Profile Settings
              </CardTitle>
              <CardDescription>
                Update your personal information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={profileData.username}
                  onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                  placeholder="Enter username"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter email"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={profileData.name}
                  onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter full name"
                />
              </div>

              <Button
                onClick={handleProfileUpdate}
                disabled={isLoading.profile}
                className="w-full"
              >
                {isLoading.profile ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                    Updating...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Update Profile
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Application Settings */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-purple-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SettingsIcon className="h-5 w-5 text-purple-600" />
                Application Settings
              </CardTitle>
              <CardDescription>
                Configure application behavior
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive analysis alerts</p>
                </div>
                <Button
                  variant={settings.notifications ? "brand" : "outline"}
                  size="sm"
                  onClick={() => setSettings(prev => ({ ...prev, notifications: !prev.notifications }))}
                >
                  {settings.notifications ? 'On' : 'Off'}
                </Button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-save Results</Label>
                  <p className="text-sm text-muted-foreground">Automatically save analysis results</p>
                </div>
                <Button
                  variant={settings.autoSave ? "brand" : "outline"}
                  size="sm"
                  onClick={() => setSettings(prev => ({ ...prev, autoSave: !prev.autoSave }))}
                >
                  {settings.autoSave ? 'On' : 'Off'}
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="threshold">Confidence Threshold (%)</Label>
                <Input
                  id="threshold"
                  type="number"
                  min="0"
                  max="100"
                  value={settings.confidenceThreshold}
                  onChange={(e) => setSettings(prev => ({ ...prev, confidenceThreshold: parseInt(e.target.value) }))}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Security Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-green-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-green-600" />
                Security & Privacy
              </CardTitle>
              <CardDescription>
                Manage your security preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Password Change Section */}
              <div className="space-y-4 border-b border-border pb-4">
                <h4 className="font-medium">Change Password</h4>

                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Current Password</Label>
                  <div className="relative">
                    <Input
                      id="currentPassword"
                      type={showPasswords.current ? "text" : "password"}
                      value={passwordData.currentPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                      placeholder="Enter current password"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3"
                      onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                    >
                      {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <div className="relative">
                    <Input
                      id="newPassword"
                      type={showPasswords.new ? "text" : "password"}
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                      placeholder="Enter new password"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3"
                      onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                    >
                      {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showPasswords.confirm ? "text" : "password"}
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      placeholder="Confirm new password"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3"
                      onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                    >
                      {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <Button
                  onClick={handlePasswordChange}
                  disabled={isLoading.password || !passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword}
                  className="w-full"
                >
                  {isLoading.password ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                      Changing...
                    </>
                  ) : (
                    <>
                      <Shield className="h-4 w-4 mr-2" />
                      Change Password
                    </>
                  )}
                </Button>
              </div>

              {/* Other Security Options */}
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Shield className="h-4 w-4 mr-2" />
                  Enable Two-Factor Authentication
                </Button>

                <Button
                  onClick={handleExportData}
                  disabled={isLoading.export}
                  variant="outline"
                  className="w-full justify-start"
                >
                  {isLoading.export ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                      Exporting...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      Download My Data
                    </>
                  )}
                </Button>

                <Button
                  onClick={handleDeleteAccountClick}
                  disabled={isLoading.delete}
                  variant="destructive"
                  className="w-full justify-start"
                >
                  {isLoading.delete ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Account
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Appearance Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Card className="shadow-elegant-lg bg-card/50 backdrop-blur-sm border-orange-600/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-orange-600" />
                Appearance
              </CardTitle>
              <CardDescription>
                Customize the look and feel
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              
              
              <div className="space-y-2">
                <Label htmlFor="language">Language</Label>
                <select
                  id="language"
                  value={settings.language}
                  onChange={(e) => setSettings(prev => ({ ...prev, language: e.target.value }))}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Message Display */}
      {message && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-lg border ${
            message.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-200'
              : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <CheckCircle className={`h-4 w-4 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`} />
            {message.text}
          </div>
        </motion.div>
      )}

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="flex justify-center"
      >
        <Button
          onClick={handleSave}
          size="lg"
          className="flex items-center gap-2 px-8"
        >
          <Save className="h-4 w-4" />
          Save All Settings
        </Button>
      </motion.div>

      {/* Delete Account Confirmation Modal */}
      {showDeleteConfirmation && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 shadow-xl"
          >
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
                <Trash2 className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Delete Account
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently removed.
              </p>
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={handleDeleteAccountCancel}
                  variant="outline"
                  className="px-4"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleDeleteAccountConfirm}
                  variant="destructive"
                  className="px-4"
                  disabled={isLoading.delete}
                >
                  {isLoading.delete ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                      Deleting...
                    </>
                  ) : (
                    'Delete Account'
                  )}
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
