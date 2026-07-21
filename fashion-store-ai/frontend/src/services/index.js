import api from './api'

export const authApi = {
  register: (payload) => api.post('/auth/register', payload),
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/auth/me'),
}

export const productApi = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  categories: () => api.get('/categories'),
  promotions: (params) => api.get('/promotions', { params }),
  create: (payload) => api.post('/products', payload),
  update: (id, payload) => api.patch(`/products/${id}`, payload),
  remove: (id) => api.delete(`/products/${id}`),
  createCategory: (payload) => api.post('/categories', payload),
  createPromotion: (payload) => api.post('/promotions', payload),
}

export const orderApi = {
  getCart: () => api.get('/cart'),
  addToCart: (payload) => api.post('/cart/items', payload),
  updateCartItem: (productId, payload, params) =>
    api.patch(`/cart/items/${productId}`, payload, { params }),
  clearCart: () => api.delete('/cart'),
  createOrder: (payload) => api.post('/orders', payload),
  myOrders: () => api.get('/orders'),
  getOrder: (id) => api.get(`/orders/${id}`),
  adminOrders: () => api.get('/admin/orders'),
  updateOrderStatus: (id, status) => api.patch(`/admin/orders/${id}`, { status }),
}

export const chatApi = {
  ask: (payload) => api.post('/chat', payload),
  faqs: () => api.get('/faqs'),
  storeInfo: () => api.get('/store-info'),
  createFaq: (payload) => api.post('/faqs', payload),
  chatLogs: () => api.get('/admin/chat-logs'),
  reindex: () => api.post('/admin/reindex'),
  updateStoreInfo: (payload) => api.put('/store-info', payload),
}

export const adminApi = {
  dashboard: () => api.get('/admin/dashboard'),
  users: () => api.get('/admin/users'),
  products: (params) => api.get('/admin/products', { params }),
}
