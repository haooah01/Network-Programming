import axiosInstance from './axiosInstance'

export const authAPI = {
  login: (credentials) => {
    return axiosInstance.post('/auth/login', credentials)
  },

  register: (userData) => {
    return axiosInstance.post('/auth/register', userData)
  },

  logout: () => {
    return axiosInstance.post('/auth/logout')
  },

  refreshToken: () => {
    return axiosInstance.post('/auth/refresh')
  },

  forgotPassword: (email) => {
    return axiosInstance.post('/auth/forgot-password', { email })
  },

  resetPassword: (data) => {
    return axiosInstance.post('/auth/reset-password', data)
  },

  verifyEmail: (token) => {
    return axiosInstance.post('/auth/verify-email', { token })
  }
}