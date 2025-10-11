import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userAPI } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const currentUser = ref(null)
  const isLoading = ref(false)
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0
  })

  const totalUsers = computed(() => users.value.length)
  const hasUsers = computed(() => users.value.length > 0)

  const fetchUsers = async (params = {}) => {
    try {
      isLoading.value = true
      const response = await userAPI.getUsers(params)
      users.value = response.data.users
      pagination.value = response.data.pagination
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Failed to fetch users' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserById = async (id) => {
    try {
      isLoading.value = true
      const response = await userAPI.getUserById(id)
      currentUser.value = response.data
      return { success: true, user: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Failed to fetch user' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (userData) => {
    try {
      isLoading.value = true
      const response = await userAPI.updateProfile(userData)
      currentUser.value = response.data
      return { success: true, user: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Failed to update profile' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    try {
      isLoading.value = true
      await userAPI.changePassword(passwordData)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Failed to change password' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const deleteUser = async (id) => {
    try {
      isLoading.value = true
      await userAPI.deleteUser(id)
      users.value = users.value.filter(user => user.id !== id)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Failed to delete user' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const addUser = (user) => {
    users.value.push(user)
  }

  const updateUser = (updatedUser) => {
    const index = users.value.findIndex(user => user.id === updatedUser.id)
    if (index !== -1) {
      users.value[index] = updatedUser
    }
  }

  const clearUsers = () => {
    users.value = []
    currentUser.value = null
  }

  return {
    users: computed(() => users.value),
    currentUser: computed(() => currentUser.value),
    isLoading: computed(() => isLoading.value),
    pagination: computed(() => pagination.value),
    totalUsers,
    hasUsers,
    fetchUsers,
    fetchUserById,
    updateProfile,
    changePassword,
    deleteUser,
    addUser,
    updateUser,
    clearUsers
  }
})