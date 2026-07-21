import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('../pages/HomePage.vue') },
  { path: '/products', name: 'products', component: () => import('../pages/ProductPage.vue') },
  { path: '/products/:id', name: 'product-detail', component: () => import('../pages/ProductDetail.vue') },
  { path: '/cart', name: 'cart', component: () => import('../pages/CartPage.vue'), meta: { auth: true } },
  { path: '/checkout', name: 'checkout', component: () => import('../pages/CheckoutPage.vue'), meta: { auth: true } },
  { path: '/orders', name: 'orders', component: () => import('../pages/OrdersPage.vue'), meta: { auth: true } },
  { path: '/login', name: 'login', component: () => import('../pages/LoginPage.vue') },
  { path: '/admin', name: 'admin', component: () => import('../pages/AdminPage.vue'), meta: { auth: true, admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !auth.isAdmin) {
    return { name: 'home' }
  }
  return true
})

export default router
