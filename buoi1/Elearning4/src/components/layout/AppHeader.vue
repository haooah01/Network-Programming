<template>
  <header class="app-header">
    <div class="header-container">
      <div class="header-left">
        <router-link to="/" class="logo">
          <h1>Vue App</h1>
        </router-link>
      </div>

      <nav class="header-nav">
        <router-link 
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.path"
          class="nav-link"
          active-class="nav-link--active"
        >
          {{ item.name }}
        </router-link>
      </nav>

      <div class="header-right">
        <template v-if="isAuthenticated">
          <div class="user-menu">
            <button @click="toggleUserMenu" class="user-avatar">
              <img :src="user?.avatar || defaultAvatar" :alt="user?.name" />
            </button>
            
            <div v-if="showUserMenu" class="user-dropdown">
              <router-link to="/profile" class="dropdown-item">
                Profile
              </router-link>
              <router-link to="/settings" class="dropdown-item">
                Settings
              </router-link>
              <hr class="dropdown-divider" />
              <button @click="handleLogout" class="dropdown-item">
                Logout
              </button>
            </div>
          </div>
        </template>
        
        <template v-else>
          <router-link to="/login" class="auth-button">
            Login
          </router-link>
          <router-link to="/register" class="auth-button auth-button--primary">
            Sign Up
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'AppHeader',
  setup() {
    const { user, isAuthenticated, logout } = useAuth()
    const showUserMenu = ref(false)
    
    const navigationItems = [
      { name: 'Home', path: '/' },
      { name: 'About', path: '/about' },
      { name: 'Contact', path: '/contact' }
    ]

    const defaultAvatar = '/images/default-avatar.png'

    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value
    }

    const handleLogout = async () => {
      await logout()
      showUserMenu.value = false
    }

    return {
      user,
      isAuthenticated,
      navigationItems,
      defaultAvatar,
      showUserMenu,
      toggleUserMenu,
      handleLogout
    }
  }
}
</script>

<style scoped>
.app-header {
  @apply bg-white shadow-md border-b border-gray-200;
}

.header-container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16;
}

.header-left .logo {
  @apply text-2xl font-bold text-blue-600 hover:text-blue-700;
}

.header-nav {
  @apply hidden md:flex space-x-8;
}

.nav-link {
  @apply text-gray-600 hover:text-gray-900 font-medium transition-colors;
}

.nav-link--active {
  @apply text-blue-600;
}

.header-right {
  @apply flex items-center space-x-4;
}

.user-menu {
  @apply relative;
}

.user-avatar {
  @apply w-8 h-8 rounded-full overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.user-avatar img {
  @apply w-full h-full object-cover;
}

.user-dropdown {
  @apply absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50;
}

.dropdown-item {
  @apply block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left;
}

.dropdown-divider {
  @apply border-t border-gray-100 my-1;
}

.auth-button {
  @apply px-4 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900;
}

.auth-button--primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
</style>