import { useAuth } from '@/composables/useAuth'

export function authGuard(to, from, next) {
  const { isAuthenticated } = useAuth()
  
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next('/login')
  } else {
    next()
  }
}

export function guestGuard(to, from, next) {
  const { isAuthenticated } = useAuth()
  
  if (to.meta.guestOnly && isAuthenticated.value) {
    next('/')
  } else {
    next()
  }
}

export function adminGuard(to, from, next) {
  const { user } = useAuth()
  
  if (to.meta.requiresAdmin && user.value?.role !== 'admin') {
    next('/')
  } else {
    next()
  }
}