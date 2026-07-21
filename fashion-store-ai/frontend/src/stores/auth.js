import { defineStore } from 'pinia'
import { authApi } from '../services'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('fs_user') || 'null'),
    token: localStorage.getItem('fs_token') || '',
    loading: false,
    error: '',
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login(email, password) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await authApi.login(email, password)
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('fs_token', this.token)
        localStorage.setItem('fs_user', JSON.stringify(this.user))
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },
    async register(payload) {
      this.loading = true
      this.error = ''
      try {
        await authApi.register(payload)
        await this.login(payload.email, payload.password)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Register failed'
        throw error
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.user = null
      this.token = ''
      localStorage.removeItem('fs_token')
      localStorage.removeItem('fs_user')
    },
  },
})
