import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { authGuard, guestGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Global navigation guards
router.beforeEach(authGuard)
router.beforeEach(guestGuard)

export default router