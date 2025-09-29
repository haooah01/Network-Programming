import axiosInstance from './axiosInstance'

export const userAPI = {
  getProfile: () => {
    return axiosInstance.get('/user/profile')
  },

  updateProfile: (userData) => {
    return axiosInstance.put('/user/profile', userData)
  },

  changePassword: (passwordData) => {
    return axiosInstance.put('/user/change-password', passwordData)
  },

  uploadAvatar: (formData) => {
    return axiosInstance.post('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getUsers: (params) => {
    return axiosInstance.get('/users', { params })
  },

  getUserById: (id) => {
    return axiosInstance.get(`/users/${id}`)
  },

  deleteUser: (id) => {
    return axiosInstance.delete(`/users/${id}`)
  }
}