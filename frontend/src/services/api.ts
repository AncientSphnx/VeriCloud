/**
 * API service for authentication and data operations
 */

// Use environment variable or fallback to localhost for development
const API_URL = process.env.REACT_APP_API_URL || 'https://vericloud-db-wbhv.onrender.com';

// Authentication API calls
export const authAPI = {
  // Register a new user
  register: async (name: string, email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });
      return await response.json();
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Login a user
  login: async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Change user password
  changePassword: async (currentPassword: string, newPassword: string, token: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ currentPassword, newPassword }),
      });
      return await response.json();
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, message: 'Network error' };
    }
  }
};

// Reports API calls
export const reportsAPI = {
  // Get all reports for a user
  getUserReports: async (userId: string, token: string, limit?: number, skip?: number) => {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit.toString());
      if (skip) params.append('skip', skip.toString());

      const queryString = params.toString() ? `?${params.toString()}` : '';

      const response = await fetch(`${API_URL}/api/reports/user/${userId}${queryString}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return await response.json();
    } catch (error) {
      console.error('Get user reports error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Get reports for a specific session
  getSessionReports: async (sessionId: string, token: string) => {
    try {
      const response = await fetch(`${API_URL}/api/reports/session/${sessionId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return await response.json();
    } catch (error) {
      console.error('Get session reports error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Get user report statistics
  getUserReportStats: async (userId: string, token: string) => {
    try {
      const response = await fetch(`${API_URL}/api/reports/user/${userId}/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return await response.json();
    } catch (error) {
      console.error('Get user report stats error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Get dashboard data for user reports
  getReportsDashboard: async (userId: string, token: string, days?: number) => {
    try {
      const params = days ? `?days=${days}` : '';
      const response = await fetch(`${API_URL}/api/reports/user/${userId}/dashboard${params}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return await response.json();
    } catch (error) {
      console.error('Get reports dashboard error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Create a new report
  createReport: async (reportData: any, token: string) => {
    try {
      const response = await fetch(`${API_URL}/api/reports/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(reportData),
      });
      return await response.json();
    } catch (error) {
      console.error('Create report error:', error);
      return { success: false, message: 'Network error' };
    }
  }
};

export default {
  auth: authAPI,
  reports: reportsAPI,
};