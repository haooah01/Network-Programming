import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import router from '@/router'

const user = ref(null)
const token = ref(localStorage.getItem('token'))
const isLoading = ref(false)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    try {
      isLoading.value = true
      const response = await authAPI.login(credentials)
      const { token: newToken, user: userData } = response.data
      
      token.value = newToken
      user.value = userData
      localStorage.setItem('token', newToken)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    try {
      isLoading.value = true
      const response = await authAPI.register(userData)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Registration failed' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      router.push('/login')
    }
  }

  const refreshToken = async () => {
    try {
      const response = await authAPI.refreshToken()
      const { token: newToken } = response.data
      token.value = newToken
      localStorage.setItem('token', newToken)
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  return {
    user: computed(() => user.value),
    token: computed(() => token.value),
    isAuthenticated,
    isLoading: computed(() => isLoading.value),
    login,
    register,
    logout,
    refreshToken
  }
}