<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <router-link to="/" class="auth-logo">
            <h1>Vue App</h1>
          </router-link>
        </div>
        
        <div class="auth-content">
          <router-view />
        </div>
        
        <div class="auth-footer">
          <p>&copy; {{ currentYear }} Vue App. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthLayout',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.auth-layout {
  @apply min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8;
}

.auth-container {
  @apply w-full max-w-md;
}

.auth-card {
  @apply bg-white shadow-lg rounded-lg overflow-hidden;
}

.auth-header {
  @apply px-6 py-8 text-center border-b border-gray-200;
}

.auth-logo {
  @apply text-2xl font-bold text-blue-600 hover:text-blue-700;
}

.auth-content {
  @apply px-6 py-8;
}

.auth-footer {
  @apply px-6 py-4 bg-gray-50 border-t border-gray-200 text-center;
}

.auth-footer p {
  @apply text-sm text-gray-500;
}
</style>