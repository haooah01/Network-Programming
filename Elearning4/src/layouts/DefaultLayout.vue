<template>
  <div class="default-layout">
    <AppHeader />
    
    <main class="main-content">
      <router-view />
    </main>
    
    <AppFooter />
  </div>
</template>

<script>
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

export default {
  name: 'DefaultLayout',
  components: {
    AppHeader,
    AppFooter
  }
}
</script>

<style scoped>
.default-layout {
  @apply min-h-screen flex flex-col;
}

.main-content {
  @apply flex-1;
}
</style>