<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">Vue App</h3>
          <p class="footer-description">
            A modern Vue 3 application with best practices and clean architecture.
          </p>
        </div>

        <div class="footer-section">
          <h4 class="footer-subtitle">Quick Links</h4>
          <ul class="footer-links">
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/about">About</router-link></li>
            <li><router-link to="/contact">Contact</router-link></li>
            <li><router-link to="/privacy">Privacy Policy</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4 class="footer-subtitle">Contact Info</h4>
          <ul class="footer-info">
            <li>Email: info@example.com</li>
            <li>Phone: +84 123 456 789</li>
            <li>Address: 123 Vue Street, Ha Noi</li>
          </ul>
        </div>

        <div class="footer-section">
          <h4 class="footer-subtitle">Follow Us</h4>
          <div class="social-links">
            <a href="#" class="social-link">Facebook</a>
            <a href="#" class="social-link">Twitter</a>
            <a href="#" class="social-link">LinkedIn</a>
            <a href="#" class="social-link">Instagram</a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} Vue App. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.app-footer {
  @apply bg-gray-900 text-white;
}

.footer-container {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.footer-content {
  @apply py-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8;
}

.footer-section {
  @apply space-y-4;
}

.footer-title {
  @apply text-xl font-bold text-white;
}

.footer-subtitle {
  @apply text-lg font-semibold text-gray-300;
}

.footer-description {
  @apply text-gray-400 text-sm leading-relaxed;
}

.footer-links {
  @apply space-y-2;
}

.footer-links a {
  @apply text-gray-400 hover:text-white transition-colors text-sm;
}

.footer-info {
  @apply space-y-2 text-sm text-gray-400;
}

.social-links {
  @apply flex space-x-4;
}

.social-link {
  @apply text-gray-400 hover:text-white transition-colors text-sm;
}

.footer-bottom {
  @apply py-6 border-t border-gray-800 text-center;
}

.footer-bottom p {
  @apply text-sm text-gray-400;
}
</style>